from django.db.models import Q
from .models import (Metrics, Inventory)
from .serializers import BaseSerializer
import calendar

class ProductMetrics:

    def __init__(self, merchant, date=None, product=None, **kwargs):
        
        # if user not prime supplier raise
        self.__merchant = merchant
        self.__year_format = '%Y-%m'
        if not date:
            month = datetime.today().month
            year = datetime.today().year
        else:
            date = datetime.strptime(date, self.__year_format)
            month = date.month
            year = date.year
        self.__month = month
        self.__year = year
        if product:
            self.__product = product

    def __get_weekly_metric(**kwargs):
        if kwargs.get('weeks', None):
            weeks = kwargs.get('weeks')
            if weeks and type(weeks) is int:
                last_day_of_month = calender.month_range(year, month)[1]
                week_start = [1, 8, 15, 22, last_day_of_month]
                for weeks in range(len(week_start)):
                    if week_start[i] < datetime.date.today.date():
                        break
        else if kwargs.get('date', None):
            date = kwargs.get('date')
            date = datetime.strptime(self.date, self.year_format)
            month = date.month
        purchase_history = {}
        for week in range(weeks):
            week_purchase = Metrics.objects.filter(
                purchase_date__year=year,
                purchase_date__month=month,
                Q(purchase_date__date__gte=week_start[week]) |
                Q(purchase_date__date__lte=week_start[week + 1]))
                .annotate(total=Sum(amount))
            purchase_history[f'week_{week + 1}_purchase'] = week_purchase

        return purchase_history


    def __calc_weekly_metric(self, **kwargs):
        
        if self.month and self.year:
            filter = {
                        kwargs.get('category', None), 
                        kwargs.get('subcategory', None)
                        kwargs.get('product', None)
                     }
            month_purchases = Metrics.objects.filter(
                    Q(purchase_date__month=month)
                    & Q(purchase_date__year=self.year), **filter).order_by('purchase_date')
            last_day_of_month = calender.month_range(year, month)[1]
            week_starts = [1, 8, 15, 22, last_day_of_month]
            month_purchases = {1: 0, 2: 0, 3: 0, 4: 0}
            for purchase in month_purchases:
                pur_month = purchase.date.month
                for i in range(len(week_starts)):
                    if pur_month >= week_starts[i] and \
                        pur_month < week_start[i + 1]:
                            month_purchases[i] += purchase.amount 
        return pur_month


    def yearly_metric(self, **kwargs):
        if not self.year:
            return None
        if not kwargs:
            data = Metrics.objects.filter(supplier=self.supplier, purchase_date__year=year)
            .values('purchase_date__month')
            .annotate(total_purchase=Sum('amount'))
            .order_by('purchase_date__month')
            return data
        
        filter = {}
        if 'month_range' in kwargs:
            start_month = kwargs.get('month_range', {}).get('start_month', None)
            end_month = kwargs.get('month_range', {}).get('end_month', None)

        elif 'months' in kwargs:
            filter = {'months': kwargs.get('months', None)}
        if 'category' in kwargs:
            filter['category'] = kwargs.get('category', None)
        elif 'subcategory' in kwargs:
            filter['subcategory'] = kwargs.get('subcategory', None)
        products = kwargs.get('products', [])

        if months:
            data = Metrics.objects.filter(**filter, product__in=products)
            .values('purchase_date__month')
            .annotate(total_purchase=Sum('amount'))
            .order_by('purchase_date__month')

        return data


    def daily_metric(self, month, **kwargs):
        if not self.month and type(month) is not int:
            return None
        filter = {'days': kwargs.get('days', None)}
        if 'date_range' in kwargs and kwargs.get('date_range'):
            start_date = kwargs.get('date_range').get('start_date', None)
            end_date = kwargs.get('date_range').get('end_date', None)
            if not (start_date and end_date):
                raise ValueError('invalid date range provided.')

        if 'category' in kwargs:
            filter['category'] = kwargs.get('category', None)
        elif 'subcategory' in kwargs:
            filter['subcategory'] = kwargs.get('subcategory', None)
        products = kwargs.get('products',[])
        data = Metrics.objects.filter(**filter, product__in=products)
        if start_date and end_date:
            data = data.filter(Q(purchase_date__gte=start_date) & 
                    Q(purchase_date__lte=end_date))
        data = data
            .values('purchase_date__day')
            .annotate(total_purchase=Sum('amount'))
            .order_by('purhcase_date__day')

        return data
 

    def hourly_metric(self, day, **kwargs):
        if not day and type(day) not int:
            return None
        filter = {}
        if 'category' in kwargs:
            filter['category'] = kwargs.get('category', None)
        elif 'subcategory' in kwargs:
            filter['subcategory'] = kwargs.get('subcategory', None)
        products = kwargs.get('products', None)
        data = Metrics.object.filter(**filter, product__in=products).
            values('purchase_date__hour').
            annotate(total_purchase=Sum('amount')).
            order_by('purchase_date__hour')

        return data

    def weekly_metric(self, **kwargs):
        return self.calc_weekly_purchases()

    def popularity_metric(self, **kwargs):
        
        if months in kwargs:
            months = kwargs.get('months', [])
        if self.product and (self.month or months) and self.year:
            if not months:
                months.append(month)
            subcat_purchases = Metrics.objects.filter(
                    product__subcategory=subcategory,
                    purchase_date__month__in=months,
                    purchase_date__year=year)
                    .values('purchase_date__month', 'amount')
                    .annotate(product_total=Case(When(product=self.product,
                        then=Sum(amount), default=0)),
                        other_total=Case(When(~Q(product__id=self.product__id),
                        then=Sum(amount), default=0)),
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
        customer_data = Metrics.objects.values('customer', 'total_purchase').annotate(
                total_purchase=Sum(amount), count=Count(customer)).order_by('-total_purchase')

        customer_details = User.objects.filter(pk__in=[customer.pk for customer in customer_detials]).prefetch_related('location', 'email')
        
        return zip(customer_data, customer_details)

    def get_top_locations(self, number, month_range):
        pass
