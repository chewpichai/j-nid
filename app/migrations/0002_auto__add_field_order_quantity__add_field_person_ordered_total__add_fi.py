# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.signals import ran_migration
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Order.quantity'
        db.add_column('orders', 'quantity',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Person.ordered_total'
        db.add_column('people', 'ordered_total',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=11, decimal_places=2),
                      keep_default=False)

        # Adding field 'Person.paid'
        db.add_column('people', 'paid',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=11, decimal_places=2),
                      keep_default=False)

        # Adding field 'Person.num_outstanding_orders'
        db.add_column('people', 'num_outstanding_orders',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Person.quantity'
        db.add_column('people', 'quantity',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'OrderItem.quantity'
        db.add_column('order_items', 'quantity',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Order.quantity'
        db.delete_column('orders', 'quantity')

        # Deleting field 'Person.ordered_total'
        db.delete_column('people', 'ordered_total')

        # Deleting field 'Person.paid'
        db.delete_column('people', 'paid')

        # Deleting field 'Person.num_outstanding_orders'
        db.delete_column('people', 'num_outstanding_orders')

        # Deleting field 'Person.quantity'
        db.delete_column('people', 'quantity')

        # Deleting field 'OrderItem.quantity'
        db.delete_column('order_items', 'quantity')


    models = {
        u'app.bank': {
            'Meta': {'object_name': 'Bank', 'db_table': "'banks'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'app.bankaccount': {
            'Meta': {'unique_together': "(('person', 'number'),)", 'object_name': 'BankAccount', 'db_table': "'bank_accounts'"},
            'bank': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bank_accounts'", 'to': u"orm['app.Bank']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bank_accounts'", 'to': u"orm['app.Person']"})
        },
        u'app.basket': {
            'Meta': {'object_name': 'Basket', 'db_table': "'baskets'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_sale': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'orders': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'baskets'", 'symmetrical': 'False', 'through': u"orm['app.BasketOrder']", 'to': u"orm['app.Order']"}),
            'price_per_unit': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'unit': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'app.basketorder': {
            'Meta': {'object_name': 'BasketOrder', 'db_table': "'baskets_orders'"},
            'basket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Basket']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deposit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_return': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_baskets'", 'to': u"orm['app.Order']"}),
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'return_baskets'", 'null': 'True', 'to': u"orm['app.Payment']"}),
            'price_per_unit': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'})
        },
        u'app.order': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Order', 'db_table': "'orders'"},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notation': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'paid': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'orders'", 'to': u"orm['app.Person']"}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'total': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'})
        },
        u'app.orderitem': {
            'Meta': {'object_name': 'OrderItem', 'db_table': "'order_items'"},
            'cost_per_unit': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_items'", 'to': u"orm['app.Order']"}),
            'price_per_unit': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_items'", 'to': u"orm['app.Product']"}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'total': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'unit': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'})
        },
        u'app.payment': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Payment', 'db_table': "'payments'"},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notation': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['app.Person']"})
        },
        u'app.person': {
            'Meta': {'object_name': 'Person', 'db_table': "'people'"},
            'address': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'detail1': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'detail2': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_card_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '13', 'blank': 'True'}),
            'is_customer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_general': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_supplier': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'num_outstanding_orders': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'ordered_total': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '11', 'decimal_places': '2'}),
            'paid': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '11', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'app.phonenumber': {
            'Meta': {'unique_together': "(('person', 'number'),)", 'object_name': 'PhoneNumber', 'db_table': "'phone_numbers'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'phone_numbers'", 'to': u"orm['app.Person']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'phone_numbers'", 'to': u"orm['app.PhoneType']"})
        },
        u'app.phonetype': {
            'Meta': {'object_name': 'PhoneType', 'db_table': "'phone_types'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'app.product': {
            'Meta': {'ordering': "['type', 'name']", 'unique_together': "(('name', 'type'),)", 'object_name': 'Product', 'db_table': "'products'"},
            'cost_per_unit': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_sale': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'price_per_unit': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'db_column': "'type'", 'to': u"orm['app.ProductType']"}),
            'unit': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'})
        },
        u'app.producttype': {
            'Meta': {'object_name': 'ProductType', 'db_table': "'product_types'"},
            'color': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'app.supply': {
            'Meta': {'object_name': 'Supply', 'db_table': "'supplies'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notation': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'supplies'", 'to': u"orm['app.Person']"})
        },
        u'app.supplyitem': {
            'Meta': {'object_name': 'SupplyItem', 'db_table': "'supply_items'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'price_per_unit': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'supply_items'", 'to': u"orm['app.Product']"}),
            'supply': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'supply_items'", 'to': u"orm['app.Supply']"}),
            'unit': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'})
        }
    }

    complete_apps = ['app']