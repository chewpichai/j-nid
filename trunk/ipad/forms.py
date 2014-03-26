from django import forms
from j_nid.app.models import *


class OrderSearchForm(forms.Form):
    customer = forms.ModelChoiceField(required=False,
                    queryset=Person.objects.filter(is_customer=True))
    start_date = forms.DateField(input_formats=['%d/%m/%Y'])
    end_date = forms.DateField(required=False, input_formats=['%d/%m/%Y'])

    def get_orders(self):
        get = self.cleaned_data.get
        orders = Order.objects.filter(created__gte=get('start_date'))
        
        if get('end_date'): orders = orders.filter(created__lte=get('end_date'))

        if get('customer'): orders = orders.filter(person=get('customer'))

        return orders
