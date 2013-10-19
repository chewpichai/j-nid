# coding=utf8
from django import forms
from j_nid.app.models import Person, ProductType
import datetime


NOW = datetime.date.today()


MONTH_LIST = ((1, u'มกราคม'),
              (2, u'กุมภาพันธ์'),
              (3, u'มีนาคม'),
              (4, u'เมษายน'),
              (5, u'พฤษภาคม'),
              (6, u'มิถุนายน'),
              (7, u'กรกฎาคม'),
              (8, u'สิงหาคม'),
              (9, u'กันยายน'),
              (10, u'ตุลาคม'),
              (11, u'พฤศจิกายน'),
              (12, u'ธันวาคม'))

YEAR_LIST = [(y, y) for y in range(NOW.year, 2009, -1)]


class MonthlyForm(forms.Form):
    month = forms.TypedChoiceField(choices=MONTH_LIST, coerce=int)
    year = forms.TypedChoiceField(choices=YEAR_LIST, coerce=int)


class DailyForm(forms.Form):
    date = forms.DateField(input_formats=['%d-%m-%Y'])


class PaymentReportForm(forms.Form):
    start_date = forms.DateField(input_formats=['%d-%m-%Y'])
    end_date = forms.DateField(input_formats=['%d-%m-%Y'])


class CustomerReportForm(forms.Form):
    person = forms.ModelChoiceField(queryset=Person.objects.exclude(outstanding_total=0))
    start_date = forms.DateField(input_formats=['%d-%m-%Y'])
    end_date = forms.DateField(input_formats=['%d-%m-%Y'])


class CustomerSearchForm(forms.Form):
    name = forms.CharField()

    def get_customers(self):
      name = self.cleaned_data['name']
      return Person.objects.filter(name__contains=name)

class ProductSearchForm(forms.Form):
    SALE_CHOICES = ((1, u'มีขาย'),
                    (0, u'ไม่มีขาย'))

    is_sale = forms.ChoiceField(required=False, widget=forms.RadioSelect, choices=SALE_CHOICES)
    product_type = forms.ModelChoiceField(required=False, queryset=ProductType.objects)
