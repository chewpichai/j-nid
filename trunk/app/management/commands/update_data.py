from django.core.management.base import BaseCommand
from j_nid.app.models import Order, OrderItem, Person


class Command(BaseCommand):
    def handle(self, *args, **options):
        if args[0] == 'orderitem':
            orderitems = OrderItem.objects.all()
            
            for orderitem in orderitems:
                orderitem.quantity = orderitem.get_quantity()
                orderitem.save()

            print 'Successful update order items.'
        
        if args[0] == 'order':
            orders = Order.objects.all()

            for order in orders:
                order.quantity = order.get_quantity()
                order.save()

            print 'Successful update orders.'

        if args[0] == 'person':
            people = Person.objects.all()

            for person in people:
                person.ordered_total = person.get_ordered_total()
                person.paid = person.get_paid()
                person.num_outstanding_orders = person.get_num_outstanding_orders()
                person.quantity = person.get_quantity()
                person.outstanding_total = person.get_outstanding_total()
                person.latest_order_date = person.get_latest_order_date()
                person.save()

            print 'Successful update people.'
