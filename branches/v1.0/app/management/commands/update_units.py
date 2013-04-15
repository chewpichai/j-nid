from django.core.management.base import BaseCommand
from django.db import connection, transaction
import sys


class Command(BaseCommand):
    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('ALTER TABLE products MODIFY unit NUMERIC(9, 2) NOT NULL')
        cursor.execute('ALTER TABLE order_items MODIFY unit NUMERIC(9, 2) NOT NULL')
        cursor.execute('ALTER TABLE supply_items MODIFY unit NUMERIC(9, 2) NOT NULL')
        transaction.commit_unless_managed()
        sys.stdout.write('Successfully update tables.')
