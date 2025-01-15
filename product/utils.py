from .models import (Product, SubCategory,
        TokenToSubCategory, SubCategorySearchWeight)
from functools import reduce
from supplier.models import Metrics
from .serializers import ProductSerializer
from django.core.paginator import Paginator
from django.db.models import (CharField, IntegerField, Q, Func, F)
from django.contrib.postgres.fields import (ArrayField)
from django.db.models.expressions import RawSQL
from collections import Counter
from django.conf import settings
from datetime import datetime
import enchant
import json
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import asyncio
import os
import csv
import nltk


# Apply caching system to all the functions

class PopularityCheck:

    NEAREST_DAY = 3
    FURTHER_DAY = 14
    FURTHEST_DAY = 21

    def __init__(self, metrics_data, subcats, *args, **kwargs):


        days_ago_40 = datetime.today - datetime.delta(day=40)
        product_filter = Q(purchase_date=days_ago_40)
        quantity_filter = Q(product__quantity__gte=1500)
        exclude_populars = ~Q(pk__in=popular_list)
        day_tf_21 = datetime.today - datetime.delta(days=self.__class__.NEAREST_DAY)
        day_tf_3 = datetime.today - datetime.delta(days=self.__class__.FURTHER_DAY)
        dy_tf_14 = datetime.today - datetime.delta(days=self.__class__.FURTHEST_DAY)
        
        self.subcats = subcats
        self.__all_products = metrics_data.filter(product_filter & quantity_filter & exclude_populars)
        
        def __get_preleminary_aggregates(self, subcat):
            
            subcat_products = self.__all_products.filter(product__subcategory=subcat)
            
            self.__purchase_aggregates = subcat_products.annotate(
                three_d_purchases=Sum(Case(When(purchase_date__gte=day_tf_3, then=F('quantity')), default=0)),
                    fourteen_d_purchases=Sum(Case(When(purchase_date__gte=day_tf_14, then=F('quantity')), default=0)),
                        twentyone_d_purchases=Sum(Case(When(purchase_date__gte=day_tf_21, then=F('quantity')), default=0)),
                            total_purchases=Sum('quantity'),
                                product_count=Count(product))
        )

    def __calculate_purchase_percentage(self):

        all_product_agg = self.__all_products.aggregate(sum=Sum('quantity'))['sum']
        popular = self.__purchase_aggregates.filter(F('popular_by_total_purchase') / all_product_agg >= ratio)

        self.__purchase_aggregates = self.__purchase_aggregates.exclude(popular)
        return popular
    
    def __calculate_purchase_rate(self):

        three_d_popular = Q(three_d_purchases__gte=thresholds.get('3_day', 0))
        fourteen_d_popular = Q(fourteen_d_purchases__gte=thresholds.get('14_day', 0))
        twentyone_d_popular = Q(twentyone_d_purchases__gte=thresholds.get('21_day', 0))

        popular = self.__purchase_aggregates.filter(three_d_popular | fourteen_d_popular | twentyone_d_popular)

        self.__purchase_aggregates = self.__purchase_aggregates.exclude(popular)
        return popular

    def __calculate_wishlist(self):

        wishlist_threshold = kwargs.get('wishlist_threshold', 0)
        exclude = ~Q(product__in=kwargs.get('popular',[]))
        popular = self.__purchase_aggregates.filter(exclude).annotate(
            wishlist_total=Count(product__wishlist_in)).filter(wishlist_total__gte=wishlist_threshold)
        
        self.__purchase_aggregates = self.__purchase_aggregates.exclude(popular)

        return popular
    
    def __calculate_conversion_rate(self):

        threshold = kwargs.get('conversion_threshold', 0)
        popular = self.__purchase_aggregates.filter(F('product_purchases') / F('click_throughs') >= threshold)
        self.__purchase_aggregates = self.__purchase_aggregates.exclude(popular)

        return popular

    def __calculate_reviews(self):

        purchase_threshold = kwargs.get('purchase_thresholds', 100)
        rating_threshold = kwargs.get('rating_threshold', 4)
        popular = self.__purchase_aggregates.filter(F('product_purchases') >= purchase_threshold, rating__gte=rating_threshold)
        
        self.__purchase_aggregates = self.__purchase_aggregates.exclude(popular)

        return popular

    def find_popular(self):
 
        popular = []
        for subcat in self.subcats:
            popular += self.calculate_purchase_percentage + \
                self.calculate_purchase_rate + \
                    self.calculate_wishlist + \
                        self.calculate_purchase_percentage
        return popular



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
    
    
    def __init__(self, search_string, user, index, **kwargs):
        
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
        print(self.__lemmatized_tokens)
    
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
        print(related_subcats)
        return related_subcats


    def get_subcats(self):
        count_related_subcats = Counter(self.related_subcats) 
        count_related_subcats = sorted(count_related_subcats.items(), key=lambda x: x[1], reverse=True)
        print(count_related_subcats)
        most_related = [subcat for subcat, count in count_related_subcats if count >= 1/2 * len(self.__lemmatized_tokens)]
        most_related = SubCategory.objects.filter(name__in=most_related)
        print(most_related)
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
        
        Product.objects.filter(pk=913).update(tag_values=['Aurora', '14Mp', '64GB', 'android13'])
        product_matches = Product.objects.filter(sub_category__in=self.__subcategory_matches).annotate(overlap=RawSQL(
        sql="ARRAY(select UNNEST (ARRAY[%s]::text[]) INTERSECT select UNNEST(tag_values))",
        params=tuple([self.__lemmatized_tokens]),
        output_field=ArrayField(CharField)
        )).annotate(overlap_len=Func(F('overlap'),
           function='CARDINALITY', output_field=IntegerField())).filter(
            overlap_len__gte=0.8*len(self.__lemmatized_tokens))
        print(product_matches)
        paginate = Paginator(product_matches, 20)
        matched_products = paginate.page(self.__index).object_list
        products_serialized = ProductSerializer(matched_products, many=True)
        return products_serialized.data

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
