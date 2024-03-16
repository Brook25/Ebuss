from datetime import datetime
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
