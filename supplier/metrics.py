from django.db.models import (Q, Sum, Count, Case, When, IntegerField)
from django.db.models.functions import (ExtractDay, ExtractHour, ExtractMonth)
from datetime import datetime
from .models import (Metrics, Inventory)
from .serializers import MetricSerializer
import calendar

class ProductMetrics:

    def __init__(self, merchant, date=None, **kwargs):
        '''
        add group by options. daily and then by product and etc
        '''
        self.merchant = merchant
        self.date_format = '%Y-%m-%d'
        self.date = date
        self.day = self.date.day
        self.month = self.date.month
        self.year = self.date.year
       

    @property
    def date(self):
        return self.date
    
    @date.setter
    def date(self, value):
        if value is None:
            self._date = datetime.today()
        try:
            self._date = datetime.strptime(self.date, self.date_format)
        except Exception as e:
            raise ValueError('Error: wrong format or data type.' + str(e))

    @property
    def merchant(self):
        return self.merchant
    
    @merchant.setter
    def merchant(self, value):
        if not value.is_supplier:
            raise ValueError("Merchant is not a supplier.")
        self._merchant = value

    @property
    def get_monthly_metric(self, **kwargs):
        user_month = kwargs.get('month', None)
        month = user_month if user_month else self.__month
        if month and type(month) is int:
                last_day_of_month = calendar.month_range(self.year, month)[1]
                week_start = [1, 8, 15, 22, last_day_of_month]
        filter = { 'supplier': self.merchant,
            'purchase_date__year': self.year,
            'purchase_date__month': month
            }
        
        if 'category' in kwargs:
            filter['category'] = kwargs.get('category', None)
        elif 'subcategory' in kwargs:
            filter['subcategory'] = kwargs.get('subcategory', None)
        elif 'products' in kwargs:
            filter['products'] = kwargs.get('products', [])
        
        week_1 = Q(purchase_date__date__gte=week_start[0]) & Q(purchase_date__date__lt=week_start[1])
        week_2 = Q(purchase_date__date__gte=week_start[1]) & Q(purchase_date__date__lt=week_start[2])
        week_3 = Q(purchase_date__date__gte=week_start[2]) & Q(purchase_date__date__lt=week_start[3])
        week_4 = Q(purchase_date__date__gte=week_start[3]) & Q(purchase_date__date__lte=week_start[4])
        weekly_purchase = Metrics.objects.filter(**filter
            ).annotate(week=Case(When(week_1, Then=1), When(week_2, Then=2),
                When(week_3, Then=3), When(week_4, Then=4),
                output_field=IntegerField())).annotate(count=Count('product'),
                     weekly_purchases=Sum('amount')).order_by('week')

            
        return weekly_purchase 

    def __metric_serializer(self, **kwargs):
        
        queryset = kwargs.get('queryset', None)
        try:
            serialized_metric = MetricSerializer(queryset, many=True)
            return serialized_metric.data
        except (MissingFieldError, AttributeError, TypeError, ValueError) as e:
            return ({'error': str(e)})

    @property
    def get_yearly_metric(self, **kwargs):
        if not self.year:
            return None

        if not kwargs:
            data = Metrics.objects.filter(supplier=self.supplier, purchase_date__year=self.year) \
            .annotate(month=ExtractMonth('purchase_date'), total_purchase=Sum('amount')) \
            .order_by('purchase_date__month').values('purchase_date', 'month', 'total_purchase')
            return data
        
        filter = {'purchase_date__year': self.year}
        
        if 'month_range' in kwargs:
            start_month = kwargs.get('month_range', {}).get('start_month', 1)
            end_month = kwargs.get('month_range', {}).get('end_month', 12)
            filter['months_in'] = list(range(start_month, end_month + 1))

        elif 'months' in kwargs:
            filter['months_in'] = kwargs.get('months', []).sort()
            

        elif kwargs.get('quarterly', False):
            start_month = self.get_quarter_start()
            filter['months_in'] = list(range(start_month, start_month + 5))

        else:
            filter['months_in'] = list(range(1, 13))
        
        if 'category' in kwargs:
            filter['category'] = kwargs.get('category', None)
        elif 'subcategory' in kwargs:
            filter['subcategory'] = kwargs.get('subcategory', None)
        elif 'products' in kwargs:
            filter['products'] = kwargs.get('products', [])
        

        data = Metrics.objects.filter(**filter).annotate(month=ExtractMonth('purchase_date'), product_count=Count('product'), 
                            total_purchase=Sum('amount')).select_related('product').order_by('purchase_date__month')

        return self.metric_serializer(data)

    @property
    def get_daily_metric(self, month, **kwargs):
        if not self.month and type(month) is not int:
            return None
        
        filter = {'purchase_date__month': self.month, 'purchase_date__year': self.year}
        if 'date_range':
            start_date = kwargs.get('date_range', {}).get('start_date', 1)
            end_date = kwargs.get('date_range', {}).get('end_date', 31)
            filter['purchase_date__date__in'] = list(range(start_date, end_date + 1))
        elif 'dates' in kwargs:
            filter['purchase_date__date__in'] = kwargs.get('dates', list(range(1, 31))).sort()
        if 'category' in kwargs:
            filter['category'] = kwargs.get('category', None)
        elif 'subcategory' in kwargs:
            filter['subcategory'] = kwargs.get('subcategory', None)
        elif 'products' in kwargs:
            filter['products'] = kwargs.get('products',[])
        data = Metrics.objects.filter(**filter) \
            .annotate(count=Count('product'), date=ExtractDay('purchase_date'), total_purchase=Sum('amount')) \
            .order_by('-date')

        return self.metric_serilizer(data)


    @property
    def hourly_metric(self, **kwargs):
        if not self.date:
            return None
        filter = {}
        if 'category' in kwargs:
            filter['category'] = kwargs.get('category', None)
        elif 'subcategory' in kwargs:
            filter['subcategory'] = kwargs.get('subcategory', None)
        elif 'products' in kwargs:
            filter['products_in'] = kwargs.get('products', [])
        data = Metrics.objects.filter(**filter) \
            .annotate(hour=ExtractHour('purchase_date')) \
            .annotate(total_purchase=Sum('amount')) \
            .order_by('purchase_date__hour')

        return self.metric_serializer(data)

    def weekly_metric(self, **kwargs):
        return self.calc_weekly_purchases()

    @staticmethod
    def get_quater_start():
        curr_date = datetime.today()
        if curr_date.month <= 3:
            quarter_start = 1
        elif 4 <= curr_date.month < 7:
            quarter_start = 4
        elif 7 <= curr_date.month < 10:
            quarter_start = 7
        else:
            quarter_start = 10

        return quarter_start

    @property
    def get_quarterly_metric(self, **kwargs):
        
        quarter_start = ProductMetrics.get_quarter_start()
        month_query = Q(purchase_date__month__gte=quarter_start) & Q(purchase_date__lte=quarter_start + 2)

        metric_data = Metrics.objects.filter(supplier=self.merchant).filter(month_query)


    @property
    def get_quarterly_revenue(self, **kwargs):

        quarter_start = ProductMetrics.get_quarter_start()
        month_query = Q(purchase_date__month__gte=quarter_start) & Q(purchase_date__lte=quarter_start + 2)

        quarterly_revenue = Metrics.objects.filter(supplier=self.__merchant).filter(month_query).aggregate(total_rev=Sum('total_price'))['total_price']

        return quarterly_revenue



    def popularity_metric(self, product, **kwargs):
        
        if months in kwargs:
            months = kwargs.get('months', [])
        if self.product and (self.month or months) and self.year:
            if not months:
                months.append(self.month)
            subcat_purchases = Metrics.objects.filter(
                    product__subcategory=subcategory,
                    purchase_date__month__in=months,
                    purchase_date__year=self.year) \
                    .annotate(product_total=Case(When(product=self.product,
                        then=Sum('amount'), default=0)),
                        other_total=Case(When(~Q(product__id=self.product__id),
                        then=Sum('amount'), default=0)),
                        product_count=Case(When(product=self.product,
                        then=Count(product), default=0)),
                        other_count=Case(When(~Q(product__id=self.product__id),
                        then=Count(product), default=0)))
            # may be include CTRs        


            return (product_total, subcat_total)


class CustomerMetrics:

    def __init__(self, merchant):
        self.__merchant = merchant


    def get_top_customers(self, number, month_range):
        customer_data = Metrics.objects.annotate(
                count=Count(customer), total_purchases=Sum(total_price)).select_related('customer').order_by('-total_purchases').values('total_purchases', 'customer__first_name', 'customer__last_name', 'customer__username', 'customer__country', 'customer__email')

        return customer_data

    def get_top_locations(self, number, month_range):
        pass
