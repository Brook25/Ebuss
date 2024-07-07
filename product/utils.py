from .product import (Product, SubCategory,
        TokenToSubcategory, SubCategorySearchWeight) 
from django.db.models.expressions import RawSQL
from collections import counter
from datetime import datetime
from enchant import SpellChecker
from thefuzz import process
import json
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import csv
import nltk


# Apply caching system to all the functions
def calculate_purchase_percentage(prod_obj, percentage):

    all_products = Metrics.objects.filter(product__sub_category=prod_obj.sub_category)
    product_sold = total_sold.filter(product=prod_obj).aggregate(sum=Sum('quantity'))['sum']
    all_sold = all_products.aggregate(sum=Sum('quantity'))['sum']
    
    return (product_sold / all_sold) * 100 >= percentage:

def calculate_purchase_rate(prod_obj, quantity, **thresholds):

    21_day_tf = datetime.today - datetime.delta(days=21)
    3_day_tf = start_date + timedelta(days=17)
    14_day_tf = start_date + timedelta(days=6)
    
    total_purchase = Metrics.objects.filter(product=prod_obj).annotate(three_day_count=Case(When(purchase_date__gte=3_day_tf, then=F('product')), default=0), fourteen_day_count=Case(When(purchase_date__gte=14_day_tf, then=F('product')),default=0), twentyone_day_count=Case(When(purchase_date__gte=21_day_tf, then=F('product')), default=0))

    three_day_purchase = total_purchase.aggregate(total=Sum('three_day_count')).get('total', 0)
    fourteen_day_purchase = total_purchase.aggregate(total=Sum('fourteen_day_count')).get('total',0)
    twentyone_day_total = total_purchase.aggregate(total=Sum('twentyone_day_total')).get('total', 0)

    wishlist_count = len(prod_obj.wish_list_in.all())
    
    return any(
        three_day_purchase + wishlist_count >= kwargs.get('3_day', 0),
        fourteen_day_purchase + wishlist_count >= kwargs.get('14_day', 0),
        twentyone_day_purchase + wishlist_count >= kwargs.get('21_day', 0)
    )

def calculate_conversion_rate(prod_obj, **conversion_args):
    product_purchase = Metrics.objects.filter(product=prod_obj)
    total_quantity = product_purchase.aggregate(total=Sum('quantity'))['total']
    
    product_visits = conversion_args.get('product_visits', 0)
    conversion_threshold = conversion_args.get('conversion_threshold', 0)
    conversion_rate = product_visits / total_quantity
    
    return conversion_rate < conversion_threshold:


def calculate_reviews(prod_obj, **review_args):

    ratings = prod_obj.ratings
    if len(reviews) <= review_args.get('required_review_count', 0)
        return False

    return sum(ratings) / len(ratings) <= review_args.get('rating_threshold', 0)



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
    
    
    def __init__(self, search_string, user, index,**kwargs)
        
        if not SearchEngine.Lemmatizer:
            self.lemmatizer = WordNetLemmatizer()
        if not nltk_stopwords_downloaded:
            nltk.download('stopwords')
            self.nltk_stopwords_downloaded = True
        if not nltk_wordnet_downloaded:
            ntlk.download('wordnet')
            self.wordnet_downloaded = True
        if not SearchEngine.StopWords:
            SearchEngine.StopWords = set(stopowrds.words('english'))


        search_tokens = [for token in tokens if token not in SearchEngine.StopWords]
        self.__lemmatized_tokens = [lemmatizer.lemmatize(word) for word in search_tokens]
        self.__lemmatized_string = ' '.join(lemmatized_tokens)
        self.__index = index
        self.__subcategory = kwargs.pop('subcategories')
        self.__category  = kwargs.pop('category')
        self.__tags = kwargs

    async def __search_token_to_subcategory(self):
        """
        This function matches search tokens with subcategories
        """
        if not self.spellchecker:
            SearchEngine.spellchecker = SpellChecker('en_US')
        
        if self.lemmatized_tokens:
            related_subcategory_json = TokenToSubCategory.objects.filter(token__in=self.lemmatized_tokens)
            related_subcategories = [*[json.loads(subcats) for subcats in related_subcategory_json]]
            count_related_subcats = Counter(related_subcategories) 
            count_related_subcats = sorted(count_related_subcats.items(), key=lambda x: x[1], reverse=True) 
            most_related = []
            for subcat, count in count_related_subcats:
                if count >= 3/5(len(self.lemmatized_tokens)):
                    most_related.append(subcat)

        return most_related


    async def blind_search(self):
        """
        Function used if no search parameters
        are specified.
        """
        # 1stbatch = SubCategorySearchWeight.objects.filter(weight__lte=3).order_by('weight')
        subcategory_matches = await self.search_token_to_subcategory()
        # also incorporate weigthed search categories
        matches = subcategory_matches.products.annotate(overlap=RawSQL(
            sql="ARRAY(select UNNEST(%s) INTERSECT select UNNEST tag_values)",
            params=self.lemmatized_tokens,
            output=ArrayField(CharField)
            ).annotate(overlap_len=Func(F(overlap), function='CARDINALITY', output_field=IntegerField()).filter(
                overlap_len__gte=0.8*len(self.lemmatized_tokens))
        return matches


    async def specified_search(self):
        """
        Function used if search parameters
        are specified.
        """
        1stbatch = SubCategorySearchWeight.objects.filter(weight__lte=3).order_by('weight')
        
        if not self.__subcategory:
            raise ValueError('subcategory not specified')
        
        if self.__tags.get('product', None):
            product_name = kwargs['product']
        subcategory_name = kwargs.get('subcategory')
        tags = SubCategory.objects.filter(name=subcategory_name)[0].tags
        if set(self.__tags) <= set([tag.name for tag in tags]):
            sub_category = SubCategory.objects.filter(name=subcategory_name)[0]
            if product_name:
                # subcategory.products = subcategory.products.filter(name__like=f'%{product_name}%')
                subcategory.products = [product for product in subcategory.products if process.extract(product_name, [product.name], score_cutoff=90)]
            matches = [product for product in subcategory.products if set(self.__tags.itmes()) <= set(json.loads(product.tags).items())]

        return matches
