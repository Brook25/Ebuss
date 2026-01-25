from .models import (Product, SubCategory,
        TokenToSubCategory, SubCategorySearchWeight)
from functools import reduce
from supplier.models import Metrics
import user.serializers
from shared.utils import paginate_queryset
from django.core.paginator import Paginator
from django.db import connections
from django.db.models import (CharField, IntegerField, DecimalField, Q, Func, F, Sum, Case,
                               When, Count, OuterRef, Subquery)
from django.contrib.postgres.fields import (ArrayField)
from django.db.models.expressions import RawSQL
from django_redis import get_redis_connection
from collections import Counter
from django.conf import settings
import datetime as datetime_object
from datetime import datetime
import enchant
import json
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from .serializers import ProductSerializer
import asyncio
import os
import csv
import nltk


# Apply caching system to all the functions

class PopularityCheck:

    NEAREST_DAY = 3
    FURTHER_DAY = 14
    FURTHEST_DAY = 21

    def __init__(self, metric_data, *args, **kwargs):

        popular_list = kwargs.get('popular_list', [])
        subcategory_ids = kwargs.get('subcategory_ids')
        if not subcategory_ids:
            raise ValueError("subcategory ids not specified.")
        
        days_ago_60 = datetime.today() - datetime_object.timedelta(days=60)
        subcat_filter = Q(product__sub_category__in=subcategory_ids)
        
        product_filter = Q(purchase_date__gte=days_ago_60)
        quantity_filter = Q(product__quantity__gte=1500)

        exclude_populars = ~Q(product__pk__in=popular_list)
 
        self.subcats = subcategory_ids
        self.purchase_ratio = kwargs.get('purchase_ratios', None)
        self.__all_products = metric_data.filter(subcat_filter & product_filter &
                                                   quantity_filter & exclude_populars)


    def __get_preleminary_aggregates(self):
            
        today = datetime.today()
        nearest_date = today - datetime_object.timedelta(days=self.__class__.NEAREST_DAY)
        further_date = today - datetime_object.timedelta(days=self.__class__.FURTHER_DAY)
        furthest_date = today - datetime_object.timedelta(days=self.__class__.FURTHEST_DAY)  
        
        self.__purchase_aggregates = self.__all_products.values('product', 'product__sub_category').annotate(
                                total_purchases=Sum('quantity'),
            three_d_purchases=Sum(Case(When(purchase_date__gte=nearest_date,
                                                 then=F('quantity')), default=0)),
                    fourteen_d_purchases=Sum(Case(When(purchase_date__gte=further_date,
                                                        then=F('quantity')), default=0)),
                        twentyone_d_purchases=Sum(Case(When(purchase_date__gte=furthest_date,
                                                             then=F('quantity')), default=0))
                           )


    def __caculate_purchase_percentage_orm(self):
        # continue here
        subcat_totals = Metrics.objects.filter(product__sub_category__pk__in=self.subcats).values('product__sub_category').annotate(threshold=Sum('quantity') * F('product__sub_category__popularity_ratio')).values_list('product__sub_category', 'threshold')
        subcat_dict = dict(subcat_totals)
        case_when_statments = [When(product__sub_category__pk=subcat_id, then=threshold)
                                for subcat_id, threshold in subcat_dict.items()]
        popular = self.__all_products.values('product').annotate(totals=Sum('quantity'),
         subcat_threshold=Case(*case_when_statments, output_field=IntegerField())).filter(totals__gte=F('subcat_threshold'))
        
        popular = [p['product'] for p in popular]
        
        self.__all_products = self.__all_products.exclude(product__pk__in=popular)
        return popular
        

    def __calculate_purchase_percentage(self):

        all_subcategory_sums = Metrics.objects.filter(product__sub_category__pk__in=self.subcats).values('product__sub_category').annotate(
            total_purchase=Sum('quantity'))

        subcat_placeholder = (', ').join(['%s'] * len(self.subcats))
        date = datetime.today().date()

        raw_sql = f"""
        SELECT p.id FROM supplier_metrics sm JOIN product_product p
        ON p.id = sm.product_id JOIN product_subcategory sc on p.sub_category_id = sc.id
        
        WHERE sc.id IN ({subcat_placeholder}) AND
              sm.purchase_date >= %s
        
        GROUP BY p.id
        
        HAVING SUM(sm.quantity) >= (
                SELECT SUM(spm.quantity) * ssc.popularity_ratio FROM supplier_metrics spm JOIN product_product pp ON spm.product_id = pp.id
                JOIN product_subcategory ssc ON ssc.id = p.sub_category_id

                WHERE ssc.id = p.sub_category_id AND
                      spm.purchase_date >= %s

                GROUP BY ssc.id
                );
            """                
        
        with connections['default'].cursor() as cursor:
            params = self.subcats + [date, date]
            cursor.execute(raw_sql, params)
            popular_product_ids = [popular for popular, in cursor.fetchall()]

        self.__all_products = self.__all_products.exclude(product__pk__in=popular_product_ids)
        return popular_product_ids
    
    def __calculate_purchase_rate(self):

        self.__get_prelimenary_aggregates()
        three_day_popular = Q(three_d_purchases__gte=F('product__sub_category__three_day_threshold'))
        fourteen_day_popular = Q(fourteen_d_purchases__gte=F('product__sub_category__fourteen_day_threshold'))
        twentyone_day_popular = Q(twentyone_d_purchases__gte=F('product__sub_category__twenty_one_day_threshold'))
        is_popular = Q(three_day_popular | fourteen_day_popular | twentyone_day_popular)
            
        popular = self.__purchase_aggregates.filter(is_popular)
        popular = [p['product'] for p in popular]

        self.__all_products = self.__all_products.exclude(product__pk__in=popular)
        return popular

    def __calculate_wishlist(self):

        popular = self.__all_products.annotate(
            wishlist_total=Count('product__wishlists_in')).filter(
                wishlist_total__gte=F('product__sub_category__wishlist_threshold'))

        popular = [p.product_id for p in popular]
        
        self.__all_products = self.__all_products.exclude(product__pk__in=popular)

        return popular
    

    def __calculate_reviews(self):

        popular = self.__all_products.filter(product__rating__gte=F('product__sub_category__rating_threshold'))
        
        popular = [p.product_id for p in popular]

        self.__all_products = self.__all_products.exclude(product__pk__in=popular)

        return popular

    def find_popular(self, raw_sql=False):
        
        purchase_percentage_calculator = self.__calculate_purchase_percentage if raw_sql else self.__caculate_purchase_percentage_orm
        return purchase_percentage_calculator() + \
                self.__calculate_purchase_rate() + \
                    self.__calculate_wishlist() + \
                        self.__calculate_reviews()


class SearchEngine:
    """
    This is the search engine class used
    to match a search string with products.
    """
    Lemmatizer = None
    StopWords = []
    nltk_stopwords_downloaded = False
    nltk_wordnet_downloaded = False
    spellchecker = None
    
    
    def __init__(self, search_string, request, index, **kwargs):
        
        self.request = request
        
        if not SearchEngine.Lemmatizer:
            self.Lemmatizer = WordNetLemmatizer()
        if not self.nltk_stopwords_downloaded:
            nltk.download('stopwords', download_dir='/home/vagrant/new_django/nltk_data')
            self.nltk_stopwords_downloaded = True
        if not self.nltk_wordnet_downloaded:
            nltk.download('wordnet', download_dir='/home/vagrant/new_django/nltk_data')
            self.nltk_wordnet_downloaded = True
        if not self.StopWords:
            self.StopWords = nltk.corpus.stopwords.words('english')
        
        
        search_tokens = [token for token in search_string.split(' ') if token not in SearchEngine.StopWords]
        self.__lemmatized_tokens = [self.Lemmatizer.lemmatize(word) for word in search_tokens]
        self.__index = index
        self.__subcategory = kwargs.get('subcategories', None)
        self.__category  = kwargs.get('category', None)
        self.__tags = {k: v for k, v in kwargs.items() if k not in ['subcategory', 'category']}
    
    async def __search_token_to_subcategory(self, popularity='high'):
        """
        This function matches search tokens with subcategories
        """
        if not self.spellchecker:
            SearchEngine.spellchecker = enchant.Dict('en_US')
        
        if self.__lemmatized_tokens:
            related_subcats = await asyncio.to_thread(self.get_related_subcategories)
            self.related_subcats = related_subcats
            #if popularity == 'high':
            most_related_subcats = await asyncio.to_thread(self.get_subcats)
                #related_subcategories = Subcategory.objects.filter(pk__in=related_subcategories, weight__search_weight__lte=3)
            #else:
            #    related_subcategories = Subcategory.objects.filter(pk__in=related_subcategories, weight__search_weight__gt=3)
        return most_related_subcats

    
    def get_related_subcategories(self):
        related_subcats = TokenToSubCategory.objects.filter(token__in=self.__lemmatized_tokens).all().values('subcategories')
        related_subcats = [subcat['subcategories'] for subcat in related_subcats]
        related_subcats = list(reduce(lambda subcat1, subcat2: subcat1 + subcat2, related_subcats))
        return related_subcats


    def get_subcats(self):
        count_related_subcats = Counter(self.related_subcats) 
        count_related_subcats = sorted(count_related_subcats.items(), key=lambda x: x[1], reverse=True)
        most_related = [subcat for subcat, count in count_related_subcats if count >= 1/2 * len(self.__lemmatized_tokens)]
        most_related = SubCategory.objects.filter(name__in=most_related)
        return most_related


    @property
    async def blind_search(self):
        """
        Function used if no search parameters
        are specified.
        """
        self.__subcategory_matches = await self.__search_token_to_subcategory()
        #self.__subcategory_matches = await asyncio.to_thread(self.temp)
        # also incorporate weigthed search categories
        matches = await asyncio.to_thread(self.get_matching_products)
        
        return matches



    def get_matching_products(self):
        
        product_matches = Product.objects.filter(sub_category__in=self.__subcategory_matches).annotate(overlap=RawSQL(
        sql="ARRAY(select UNNEST (ARRAY[%s]::text[]) INTERSECT select UNNEST(tag_values))",
        params=tuple([self.__lemmatized_tokens]),
        output_field=ArrayField(CharField)
        )).annotate(overlap_len=Func(F('overlap'),
           function='CARDINALITY', output_field=IntegerField())).filter(
            overlap_len__gte=0.8*len(self.__lemmatized_tokens))
        products = paginate_queryset(product_matches, self.request, ProductSerializer, 40)
        return products.data

    @property
    async def specified_search(self):
        """
        Function used if search parameters
        are specified.
        """
        batch_1 = SubCategorySearchWeight.objects.filter(weight__lte=3).order_by('weight')
        
        if not self.__subcategory:
            raise ValueError('subcategory not specified')
        
        if self.__tags.get('product', None):
            product_name = kwargs['product']
        subcategory_name = kwargs.get('subcategory')
        tags = SubCategory.objects.filter(name=subcategory_name)[0].tags
        if set(self.__tags) <= set([tag.name for tag in tags]):
            sub_category = SubCategory.objects.filter(name=subcategory_name).products.all()
            if product_name:
                subcategory.products = [product for product in subcategory.products if process.extract(product_name, [product.name], score_cutoff=90)]
            matches = [product for product in subcategory.products if set(self.__tags.itmes()) <= set(json.loads(product.tags).items())]

        return matches

        
def get_populars(path, request):
    redis_client = get_redis_connection('default')
    popular_products = [int(product) for product in redis_client.lrange('popular', 0, -1)]

    query = Q()
    if path == 'product':
        query &= Q(pk__in=popular_products)

    elif path == 'subcategory':
        subcat_ids = request.GET.get('subcat_ids', [])
        if subcat_ids:
            query &= Q(pk__in=popular_products) & Q(subcategory__pk__in=subcat_ids)

    elif path == 'category':
        category_ids = request.GET.get('cat_id', [])
        if category_ids:
             query &= Q(subcategory__category__pk__in=category_ids) & Q( pk__in=popular_products)
    
    popular_products = ProductSerializer(Product.objects.filter(query), many=True)
    return {'popular_products': popular_products.data}
