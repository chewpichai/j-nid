from django.core.management.base import BaseCommand
from j_nid.app.models import Order
import sys


class Command(BaseCommand):
    def handle(self, *args, **options):
        for i in range(2):
            for order in Order.objects.all():
                order.save()
        sys.stdout.write('Successfully update orders.')
