from django.db.models import (Q, Sum, F, Count, Case, When, IntegerField)
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
        self.metric_query = Metrics.objects.filter(supplier=self.merchant)



    @staticmethod
    def get_query_params(metric_type):
        
        if metric_type not in ['hourly', 'daily', 'weekly', 'monthly']:
            raise ValueError('wrong metric type provided.')
        
        basic_params = ['category', 'subcategory', 'products']
        query_params = {
            'hourly': basic_params,
            'daily': basic_params + ['date_range', 'dates'],
            'weekly': basic_params + ['month'],
            'monthly': basic_params + ['month', 'month_range', 'quarterly']
        }
        
        return query_params[metric_type]



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
        if value.is_supplier:
            raise ValueError("Merchant is not a supplier.")
        self._merchant = value

    def get_weekly_metric(self, **kwargs):
        
        filter_params = ['month', 'category', 'subcategory', 'products']
        kwargs = {k: v for k, v in kwargs.items() if k in filter_params}
 
        month = kwargs.pop('month', None)
        month = month if month else self.__month
        
        if month and type(month) is int:
                last_day_of_month = calendar.month_range(self.year, month)[1]
                week_start = [1, 8, 15, 22, last_day_of_month]
        
        filter = { 'supplier': self.merchant,
            'purchase_date__year': self.year,
            'purchase_date__month': month
            }

        values = ['week'] if not len(kwargs) else ['week', 'product__name']

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
        
        weekly_purchase = self.metric_query.filter(**filter) \
            .annotate(week=Case(When(week_1, Then=1), When(week_2, Then=2),
                When(week_3, Then=3), When(week_4, Then=4),
                    output_field=IntegerField())).values(*values).annotate(weekly_purchases=Sum('amount')).order_by('week')

            
        return weekly_purchase 

    def _metric_serializer(self, **kwargs):
        
        queryset = kwargs.get('queryset', None)
        try:
            serialized_metric = MetricSerializer(queryset, many=True)
            return serialized_metric.data
        except (MissingFieldError, AttributeError, TypeError, ValueError) as e:
            return ({'error': str(e)})

    @property
    def get_monthly_metric(self, **kwargs):
        if not self.year:
            return None

        values = ['month']
        
        kwargs = {k: v for k, v in kwargs.items() if k in ProductMetrics.get_query_params('monthly')}
        
        filter = {'purchase_date__year': self.year}

        month_range = kwargs.pop('month_range', None)
        months = kwargs.pop('months', None)
        quarterly = kwargs.pop('quarterly', None)

        if month_range:
            start_month = kwargs.get('month_range', {}).get('start_month', 1)
            end_month = kwargs.get('month_range', {}).get('end_month', 12)
            filter['months__in'] = list(range(start_month, end_month + 1))

        elif months:
            filter['months__in'] = kwargs.get('months', []).sort()
            

        elif quarterly:
            start_month = self.get_quarter_start()
            filter['months__in'] = list(range(start_month, start_month + 2))

        else:
            filter['months__in'] = list(range(1, 13))
        
        if len(kwargs) == 0:
            values.append('product__name')

        
        if kwargs.get('category', None):
            filter['product__subcategory__category__in'] = kwargs['category']
        elif 'subcategory' in kwargs:
            filter['product__subcategory__in'] = kwargs['subcategory']
        elif 'products' in kwargs:
            filter['product__in'] = kwargs['products']
        

        data = self.metric_query.filter(**filter).annotate(month=ExtractMonth('purchase_date')).values(*values) \
            .annotate(total_amount=Sum('amount'), total_quantity=Sum('quantity')).order_by('month')

        return data

    def get_daily_metric(self, month, **kwargs):
        if type(month) is not int:
            return None
        
        kwargs = {k: v for k, v in kwargs.items() if k in ProductMetrics.get_query_params('daily')}
        
        filter = {'purchase_date__month': month, 'purchase_date__year': self.year}
        
        date_range = kwargs.pop('date_range', None)
        dates = kwargs.pop('dates', None)

        if date_range:
            start_date = date_range.get('start_date', 1)
            end_date = date_range.get('end_date', 31)
            filter['purchase_date__date__in'] = list(range(start_date, end_date + 1))
        elif dates:
            filter['purchase_date__date__in'] = dates     
        
        values = ['purchase_data'] if len(kwargs) == 0 else ['purchase_date', 'product__name']

        if kwargs.get('category', None):
            filter['product__subcategory__category'] = kwargs['category']
        elif kwargs.get('subcategory', None):
            filter['product__subcategory'] = kwargs['subcategory']
        elif kwargs.get('products', None):
            filter['product__in'] = kwargs['products']
        
        return self.metric_query.filter(**filter).values(*values) \
            .annotate(day=ExtractDay('purchase_date'), total_purchase=Sum('amount'), total_quantity=Sum('quantity')) \
            .order_by('-day')


    @property
    def hourly_metric(self, **kwargs):
        if not self.date:
            return None

        values = ['hour'] 

        kwargs = {k: v for k, v in kwargs.items() if k in ProductMetrics.get_query_params('hourly')}
        
        if len(kwargs):
            values.append('product__name')

        filter = {}
        
        if 'category' in kwargs:
            filter['category__in'] = kwargs.get('category', None)
        elif 'subcategory' in kwargs:
            filter['subcategory__in'] = kwargs.get('subcategory', None)
        elif 'products' in kwargs:
            filter['products__in'] = kwargs.get('products', [])
        
        return self.metric_query.filter(**filter) \
            .annotate(hour=ExtractHour('purchase_date')).values(*values) \
            .annotate(total_purchase=Sum('amount'), total_quantity=Sum('quantity')) \
            .order_by('hour')

        
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

        return self.metric_query.filter(supplier=self.merchant).filter(month_query)


    @property
    def get_quarterly_revenue(self, **kwargs):

        quarter_start = ProductMetrics.get_quarter_start()
        month_query = Q(purchase_date__month__gte=quarter_start) & Q(purchase_date__lte=quarter_start + 2)

        quarterly_revenue = self.metric_query.filter(supplier=self.merchant).filter(month_query).aggregate(total_rev=Sum('total_price'))['total_price']

        return quarterly_revenue

    def get_yearly_metric(self, **kwargs):
    
        years = kwargs.get('years', [self.years])
        filter = {'purchase_date__year__in': years}
        kwargs = {k: v for k, v in kwargs.items() if k in ['product', 'subcategory', 'category']}

        values = ['purchase_date__year']
        if kwargs:
            values.append('product__name')
        
        if 'category' in kwargs:
            filter['category__in'] = kwargs.get('category', None)
        elif 'subcategory' in kwargs:
            filter['subcategory__in'] = kwargs.get('subcategory', None)
        elif 'products' in kwargs:
            filter['products__in'] = kwargs.get('products', [])

        return self.metric_query.filter(**filter).values(*values) \
            .annotate(total_purchase=Sum('quantity'), total_amount=Sum('amount')) \
                .order_by('purchase_date__year')
        

    def popularity_metric(self, product, **kwargs):
        
        if months in kwargs:
            months = kwargs.get('months', [])
        if not all([self.product, (self.month or months), self.year]):
            return
        if not months:
            months.append(self.month)
        subcat_purchases = self.metric_query.filter(
                product__subcategory=product.subcategory,
                purchase_date__month__in=months,
                purchase_date__year=self.year) \
                .annotate(product_total=Sum(Case(When(product=self.product),
                    then=F('amount'), default=0, output_field=IntegerField)),
                    other_total=Sum(Case(When(~Q(product=self.product)),
                        then=F('amount'), default=0, output_field=IntegerField()))).values('product','product_total', 'other_total')
        # may be include CTRs
        
        return subcat_purchases


class CustomerMetrics:

    def __init__(self, merchant):
        self.metric_query = Metrics.objects.filter(product__supplier=merchant, purchase_dat__year=year)

    def get_top_customers(self, start_date, end_date):
        
        date_filter = Q(purchase_date__gte=start_date) & Q(purchase_date__lte=end_date)
        customer_data = self.metric_query(date_filter) \
        .values('customer__first_name', 'customer__last_name', 'customer__email') \
        .annotate(total_purchases=Sum('quantity'), total_amount=Sum('amount')).order_by('total_amount', 'total_quantity')

        return customer_data

    def get_top_locations(self, number, month_range):
        pass
