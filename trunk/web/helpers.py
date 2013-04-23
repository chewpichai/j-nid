# coding=utf8
from django.db.models import Sum
from django.utils import simplejson
from j_nid.app.models import OrderItem, Payment
import sys


class SummaryData(object):
	def __init__(self, date):
		self.date = date
		self.orderitems = OrderItem.objects.filter(order__created__year=self.date.year,
												   order__created__month=self.date.month,
												   order__created__day=self.date.day)
		self.payments = Payment.objects.filter(created__year=self.date.year,
											   created__month=self.date.month,
											   created__day=self.date.day)
		self.total = self.orderitems.aggregate(Sum('total'))['total__sum'] or 0
		self.quantity = self.orderitems.aggregate(Sum('quantity'))['quantity__sum'] or 0
		self.paid = self.payments.aggregate(Sum('amount'))['amount__sum'] or 0
		self.products = {}
		self.hours = {}

		for item in self.orderitems:
			self.products.setdefault(item.product, []).append(item)
			self.hours.setdefault(item.order.created.hour, []).append(item)

		self.productstats = []

		for product, items in self.products.items():
			stat = {}
			stat['product'] = product
			prices = [item.price_per_unit for item in items]
			stat['min_price'] = min(prices) 
			stat['max_price'] = max(prices)
			stat['avrg_price'] = sum(prices) / len(prices)
			stat['quantity'] = sum([item.quantity for item in items])
			stat['total'] = sum([item.total for item in items])
			self.productstats.append(stat)

		self.productstats.sort(key=lambda stat: stat['total'], reverse=True)
		self.hoursjson = [0] * 24

		for hour, items in self.hours.items():
			self.hoursjson[hour] = sum([item.total for item in items])

		self.hoursjson = simplejson.dumps(self.hoursjson)
		self.productsjson = [[stat['product'].name, stat['quantity']] for stat in self.productstats[:6]]
		self.productsjson.append([u'อื่นๆ', sum([stat['quantity'] for stat in self.productstats[6:]])])
		self.productsjson = simplejson.dumps(self.productsjson)
