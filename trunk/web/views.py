from django.db.models import Sum
from django.shortcuts import render
from j_nid.app.models import *
from j_nid.web.forms import *
from j_nid.web.helpers import *
import datetime


def get_monthly_sales_report(request):
    form = MonthlyForm(request.GET)
    
    if form.is_valid():
        month = form.cleaned_data['month']
        year = form.cleaned_data['year']
        date = datetime.date(year, month, 1)
        sum_quantity = 0
        sum_order = 0
        sum_payment = 0
        report = []
        
        while 1:
            orders = Order.objects.filter(created__day=date.day,
                                          created__month=date.month,
                                          created__year=date.year)
            payments = Payment.objects.filter(created__day=date.day,
                                              created__month=date.month,
                                              created__year=date.year)
            quantity = orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
            total_order = orders.aggregate(Sum('total'))['total__sum'] or 0
            total_payment = payments.aggregate(Sum('amount'))['amount__sum'] or 0
            sum_quantity += quantity
            sum_order += total_order
            sum_payment += total_payment
            report.append({'date': date,
                           'quantity': quantity,
                           'total_order': total_order,
                           'total_payment': total_payment})
            date += datetime.timedelta(days=1)

            if date.month != month: break

        sums = {'quantity': sum_quantity, 'total_order': sum_order,
                'total_payment': sum_payment}
        avgs = {'quantity': sum_quantity / len(report),
                'total_order': sum_order / len(report),
                'total_payment': sum_payment / len(report)}
    
    return render(request, 'web/monthly-sales-report.html', locals())


def get_daily_sales_report(request):
    form = DailyForm(request.GET)
    
    if form.is_valid():
        date = form.cleaned_data['date']
        orders = Order.objects.filter(created__day=date.day,
                                      created__month=date.month,
                                      created__year=date.year) \
                      .order_by('created')
        sums = orders.aggregate(Sum('total'))['total__sum'] or 0

    return render(request, 'web/daily-sales-report.html', locals())


def get_payment_report(request):
    form = PaymentReportForm(request.GET)

    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date'] + datetime.timedelta(days=1)
        payments = Payment.objects.filter(created__range=(start_date, end_date)) \
                          .order_by('created')
        sums = payments.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'web/payment-report.html', locals())



def get_customer_report(request):
    form = CustomerReportForm(request.GET)

    if form.is_valid():
        person = form.cleaned_data['person']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date'] + datetime.timedelta(days=1)
        balance = person.get_balance_until(start_date)
        orders = person.orders.filter(created__range=(start_date, end_date)).order_by('created')
        payments = person.payments.filter(created__range=(start_date, end_date)).order_by('created')
        sum_order = orders.aggregate(Sum('total'))['total__sum'] or 0
        sum_payment = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        summary = balance + (sum_payment - sum_order)

    return render(request, 'web/customer-report.html', locals())


def get_order(request, id):
    order = Order.objects.get(pk=id)
    baskets = {}

    for basket in order.order_baskets.filter(is_deposit=True):
        val = baskets.setdefault(basket.name, {'name': basket.name,
                                               'quantity': 0,
                                               'unit': 0,
                                               'price': basket.price_per_unit,
                                               'total': 0})
        val['unit'] += 1
        val['total'] += basket.price_per_unit

    baskets = baskets.values()

    return render(request, 'web/include/order.html', locals())


def get_payment(request, id):
    payment = Payment.objects.get(pk=id)
    deposit_baskets = {}
    non_deposit_baskets = {}

    for basket in payment.return_baskets.filter(is_deposit=True):
        val = deposit_baskets.setdefault(basket.name, {'name': basket.name,
                                                       'quantity': 0,
                                                       'price': basket.price_per_unit,
                                                       'total': 0})
        val['quantity'] += 1
        val['total'] += basket.price_per_unit

    for basket in payment.return_baskets.filter(is_deposit=False):
        val = non_deposit_baskets.setdefault(basket.name, {'name': basket.name,
                                                           'quantity': 0,
                                                           'price': basket.price_per_unit,
                                                           'total': 0})
        val['quantity'] += 1
        val['total'] += basket.price_per_unit

    deposit_baskets = deposit_baskets.values()
    non_deposit_baskets = non_deposit_baskets.values()

    return render(request, 'web/include/payment.html', locals())


def get_daily_transaction_report(request):
    form = DailyForm(request.GET)
    
    if form.is_valid():
        date = form.cleaned_data['date']
        orders = Order.objects.filter(created__day=date.day,
                                      created__month=date.month,
                                      created__year=date.year)
        payments = Payment.objects.filter(created__day=date.day,
                                          created__month=date.month,
                                          created__year=date.year)
        transactions = list(orders) + list(payments)
        transactions.sort(key=lambda t: t.created, reverse=False)

    return render(request, 'web/daily-transaction-report.html', locals())


def get_dashboard(request):
  # today = datetime.date.today()
  today = datetime.date(2013, 3, 31)
  yesterday = today - datetime.timedelta(days=1)
  summary = SummaryData(today)
  yesterday_summary = SummaryData(yesterday)
  quantity_diff = summary.quantity - yesterday_summary.quantity
  total_diff = summary.total - yesterday_summary.total
  paid_diff = summary.paid - yesterday_summary.paid
  return render(request, 'web/dashboard.html', locals())
