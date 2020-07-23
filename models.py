from app import db
import hashlib
import datetime
import peewee as pw



class Order(pw.Model):
    amount =      pw.DecimalField(max_digits=10, decimal_places=2, auto_round=True)
    currency =    pw.CharField(max_length=25)
    payway =      pw.CharField(max_length=255, null=True)
    shop_id =     pw.CharField(max_length=255)
    secret_key =  pw.CharField(max_length=255)
    sign =        pw.CharField(max_length=255, null=True)
    description = pw.TextField(default='')
    response =    pw.TextField(default='{}')
    date =        pw.DateTimeField(default=datetime.datetime.now())
    
    class Meta:
        database = db

    def __str__(self):
        s = f'{str(self.id)} {str(self.date)} {str(self.amount)}'
        return s

    def get_hash(self, fields, prms):
        for attr in fields:
            if getattr(self, attr) is None:
                return None
        pre_gen = [prms[key] for key in sorted(list(prms.keys()))]
        sha256 = hashlib.sha256(':'.join(pre_gen).encode('utf-8')).hexdigest()
        return sha256

    @property
    def method_pay(self):
        fields = ['id','amount', 'currency','shop_id','secret_key']
        prms = {
            'amount' : str(self.amount),
            'currency' : str(self.currency),
            'shop_id' : str(self.shop_id),
            'shop_order_id' : str(self.id) + str(self.secret_key),
        }
        return self.get_hash(fields, prms)

    @property
    def method_bill(self):
        fields = ['amount', 'currency', 'shop_id']
        prms = {
            'shop_amount' :    str(self.amount),
            'shop_currency' :  str(self.currency),
            'shop_id' :        str(self.shop_id),
            'shop_order_id' :  str(self.id) + str(self.secret_key),
            'payer_currency' : str(self.currency),
        }
        return self.get_hash(fields, prms)
    
    @property
    def method_invoice(self):
        fields = ['amount', 'currency', 'payway', 'shop_id', 'id']
        prms = {
            'amount' :   str(self.amount),
            'currency' : str(self.currency),
            'payway' :   str(self.payway),
            'shop_id' :  str(self.shop_id),
            'shop_order_id' : str(self.id) + str(self.secret_key),
        }
        return self.get_hash(fields, prms)

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
        pay_methods = {
            '978' : self.method_pay,
            '840' : self.method_bill,
            '643' : self.method_invoice,
        }
        self.sign = pay_methods[self.currency] if self.currency in pay_methods.keys() else None
        return super(Order, self).save(*args, **kwargs)
        
