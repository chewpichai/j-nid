# coding=utf8
from django import forms
from j_nid.app.models import *
import datetime


class OrderSearchForm(forms.Form):
    customer = forms.ModelChoiceField(required=False,
                    queryset=Person.objects.filter(is_customer=True),
                    empty_label=u'เลือกลูกค้า')
    start_date = forms.DateField(input_formats=['%d/%m/%Y'],
                    widget=forms.DateInput(attrs={'class': 'date form-control'}))
    end_date = forms.DateField(required=False, input_formats=['%d/%m/%Y'],
                    widget=forms.DateInput(attrs={'class': 'date form-control'}))

    def get_orders(self):
        get = self.cleaned_data.get
        orders = Order.objects.filter(created__gte=get('start_date'))
        
        if get('end_date'):
            end_date = get('end_date') + datetime.timedelta(days=1)
            orders = orders.filter(created__lte=end_date)

        if get('customer'): orders = orders.filter(person=get('customer'))

        return orders
