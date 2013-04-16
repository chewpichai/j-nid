# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Person'
        db.create_table('people', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('first_name', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('id_card_number', self.gf('django.db.models.fields.CharField')(default='', max_length=13, blank=True)),
            ('address', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('detail1', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('detail2', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('is_customer', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_supplier', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_general', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'app', ['Person'])

        # Adding model 'Bank'
        db.create_table('banks', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'app', ['Bank'])

        # Adding model 'BankAccount'
        db.create_table('bank_accounts', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bank_accounts', to=orm['app.Person'])),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('bank', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bank_accounts', to=orm['app.Bank'])),
        ))
        db.send_create_signal(u'app', ['BankAccount'])

        # Adding unique constraint on 'BankAccount', fields ['person', 'number']
        db.create_unique('bank_accounts', ['person_id', 'number'])

        # Adding model 'PhoneType'
        db.create_table('phone_types', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal(u'app', ['PhoneType'])

        # Adding model 'PhoneNumber'
        db.create_table('phone_numbers', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='phone_numbers', to=orm['app.Person'])),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='phone_numbers', to=orm['app.PhoneType'])),
        ))
        db.send_create_signal(u'app', ['PhoneNumber'])

        # Adding unique constraint on 'PhoneNumber', fields ['person', 'number']
        db.create_unique('phone_numbers', ['person_id', 'number'])

        # Adding model 'Payment'
        db.create_table('payments', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['app.Person'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('notation', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'app', ['Payment'])

        # Adding model 'ProductType'
        db.create_table('product_types', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('color', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'app', ['ProductType'])

        # Adding model 'Product'
        db.create_table('products', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='products', db_column='type', to=orm['app.ProductType'])),
            ('unit', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('cost_per_unit', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('price_per_unit', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('is_sale', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'app', ['Product'])

        # Adding unique constraint on 'Product', fields ['name', 'type']
        db.create_unique('products', ['name', 'type'])

        # Adding model 'Order'
        db.create_table('orders', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='orders', to=orm['app.Person'])),
            ('paid', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('total', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('notation', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'app', ['Order'])

        # Adding model 'OrderItem'
        db.create_table('order_items', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='order_items', to=orm['app.Order'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='order_items', to=orm['app.Product'])),
            ('cost_per_unit', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('price_per_unit', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('unit', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('total', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'app', ['OrderItem'])

        # Adding model 'Supply'
        db.create_table('supplies', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='supplies', to=orm['app.Person'])),
            ('notation', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'app', ['Supply'])

        # Adding model 'SupplyItem'
        db.create_table('supply_items', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('supply', self.gf('django.db.models.fields.related.ForeignKey')(related_name='supply_items', to=orm['app.Supply'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='supply_items', to=orm['app.Product'])),
            ('price_per_unit', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('unit', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'app', ['SupplyItem'])

        # Adding model 'Basket'
        db.create_table('baskets', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('price_per_unit', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('unit', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('is_sale', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'app', ['Basket'])

        # Adding model 'BasketOrder'
        db.create_table('baskets_orders', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('basket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Basket'])),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='order_baskets', to=orm['app.Order'])),
            ('payment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='return_baskets', null=True, to=orm['app.Payment'])),
            ('price_per_unit', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('is_deposit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_return', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'app', ['BasketOrder'])


    def backwards(self, orm):
        # Removing unique constraint on 'Product', fields ['name', 'type']
        db.delete_unique('products', ['name', 'type'])

        # Removing unique constraint on 'PhoneNumber', fields ['person', 'number']
        db.delete_unique('phone_numbers', ['person_id', 'number'])

        # Removing unique constraint on 'BankAccount', fields ['person', 'number']
        db.delete_unique('bank_accounts', ['person_id', 'number'])

        # Deleting model 'Person'
        db.delete_table('people')

        # Deleting model 'Bank'
        db.delete_table('banks')

        # Deleting model 'BankAccount'
        db.delete_table('bank_accounts')

        # Deleting model 'PhoneType'
        db.delete_table('phone_types')

        # Deleting model 'PhoneNumber'
        db.delete_table('phone_numbers')

        # Deleting model 'Payment'
        db.delete_table('payments')

        # Deleting model 'ProductType'
        db.delete_table('product_types')

        # Deleting model 'Product'
        db.delete_table('products')

        # Deleting model 'Order'
        db.delete_table('orders')

        # Deleting model 'OrderItem'
        db.delete_table('order_items')

        # Deleting model 'Supply'
        db.delete_table('supplies')

        # Deleting model 'SupplyItem'
        db.delete_table('supply_items')

        # Deleting model 'Basket'
        db.delete_table('baskets')

        # Deleting model 'BasketOrder'
        db.delete_table('baskets_orders')


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
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
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