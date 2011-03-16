from django.core.management.base import BaseCommand
from django.db import connection, transaction
import sys


class Command(BaseCommand):
    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('ALTER TABLE baskets_orders ADD payment_id INT(11) NULL AFTER order_id')
        cursor.execute('ALTER TABLE baskets_orders CHANGE is_pledge is_deposit TINYINT(1) NOT NULL')
        transaction.commit_unless_managed()
        sys.stdout.write('Successfully update tables.')
