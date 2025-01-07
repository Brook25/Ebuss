from django.db.models import (Q, Sum, Count, Case, When)
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
        # if user not prime supplier raise
        self.__merchant = merchant
        self.__year_format = '%Y-%m-%d'
        if not date:
            self.__date = datetime.today()
            self.__day = self.__date.day
            self.__month = self.__date.month
            self.__year = self.__date.year
        else:
            self.__date = datetime.strptime(date, self.__year_format)
            self.__month = self.__date.month
            self.__year = self.__date.year


    @property
    def get_monthly_metric(self, **kwargs):
        if kwargs.get('weeks', None):
            weeks = kwargs.get('weeks')
            if weeks and type(weeks) is int:
                last_day_of_month = calendar.month_range(year, month)[1]
                week_start = [1, 8, 15, 22, last_day_of_month]
    
        elif kwargs.get('date', None):
            date = kwargs.get('date')
            date = datetime.strptime(self.date, self.year_format)
            month = date.month
        filter = {}
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
        weekly_purchase = Metrics.objects.filter(**filter,
            supplier=self.__merchant,
            purchase_date__year=year,
            purchase_date__month=month,
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
            data = Metrics.objects.filter(supplier=self.supplier, purchase_date__year=year)
            .annotate(month=purchase_date__month, total_purchase=Sum('amount'))
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
        if not self.__date:
            return None
        filter = {}
        if 'category' in kwargs:
            filter['category'] = kwargs.get('category', None)
        elif 'subcategory' in kwargs:
            filter['subcategory'] = kwargs.get('subcategory', None)
        products = kwargs.get('products', None)
        data = Metrics.objects.filter(**filter, product__in=products) \
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

        metric_data = Metrics.objects.filter(supplier=self.__merchant, month_query)


    @property
    def get_quarterly_revenue(self, **kwargs):

        quarter_start = ProductMetrics.get_quarter_start()
        month_query = Q(purchase_date__month__gte=quarter_start) & Q(purchase_date__lte=quater_start + 2)

        quarterly_revenue = Metrics.objects.filter(supplier=self.__merchant, month_query).aggregate(total_rev=Sum('total_price'))['total_price']

        return quarterly_revenue



    def popularity_metric(self, product, **kwargs):
        
        if months in kwargs:
            months = kwargs.get('months', [])
        if self.product and (self.month or months) and self.year:
            if not months:
                months.append(month)
            subcat_purchases = Metrics.objects.filter(
                    product__subcategory=subcategory,
                    purchase_date__month__in=months,
                    purchase_date__year=year) \
                    .values('purchase_date__month', 'amount') \
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
