from django.db import models
import json
# Create your models here.

class Config(models.Model):
    # check db first: allow db first for a while
    dbfirst=models.BooleanField(default=False)

# this is to save the brands of a refsearch, so that next time I will serve the ref directly with the brands from db if config.dbfirst is True
class Refbrands(models.Model):
    ref=models.CharField(max_length=500, default=None, null=True, blank=True)
    brands=models.JSONField(default=list, null=True, blank=True)

class Token(models.Model):
    token=models.CharField(max_length=500, default=None, null=True, blank=True)
    name=models.CharField(max_length=500, default=None, null=True, blank=True)
class Cars(models.Model):
    vin=models.CharField(max_length=500, default=None, null=True, blank=True)
    # other vin equivalent
    vinequ=models.JSONField(default=list, null=True, blank=True)
    bodytype=models.CharField(max_length=500, default=None, null=True, blank=True)
    name=models.CharField(max_length=500, default=None, null=True, blank=True)
    yearfrom=models.CharField(max_length=500, default=None, null=True, blank=True)
    yearto=models.CharField(max_length=500, default=None, null=True, blank=True)
    uuid=models.CharField(max_length=500, default=None, null=True, blank=True)
    drivetype=models.CharField(max_length=500, default=None, null=True, blank=True)
    enginetype=models.CharField(max_length=500, default=None, null=True, blank=True)
    enginecodes=models.TextField()
    cylinders=models.IntegerField()
    valve=models.IntegerField()
    # this could hold extra data about car, image....
    carinfo=models.JSONField(default=dict, null=True, blank=True)
    def __str__(self) -> str:
        return self.vin

class Products(models.Model):
    # common code means a code that will unite the same products, this will be used to identify the same product in another brand ex: gdb400 will have the code 54545-56554-kljn-215 this code will in (unknonw) brand
    commoncode=models.JSONField(default=list, null=True, blank=True)
    car_codes = models.JSONField(default=list, null=True, blank=True)
    features = models.JSONField(default=dict, null=True, blank=True)
    # supplier code and disp of that supp, since we are saving date of suppliers
    fullName = models.CharField(max_length=500, default=None, null=True, blank=True)
    brand = models.CharField(max_length=500, default=None, null=True, blank=True)
    brandid = models.CharField(max_length=500, default=None, null=True, blank=True)
    brandref = models.CharField(max_length=500, default=None, null=True, blank=True)
    refs = models.JSONField(default=list, null=True, blank=True)
    oems = models.JSONField(default=list, null=True, blank=True)
    ean = models.JSONField(default=list, null=True, blank=True)
    code = models.CharField(max_length=500, default=None, null=True, blank=True)
    image = models.TextField(default=None, null=True, blank=True)
    categoryid = models.CharField(max_length=500, default=None, null=True, blank=True)
    # assemblyGroups is actually the category
    assemblyGroups = models.CharField(max_length=500, default=None, null=True, blank=True)
    def getpdctcars(self):
        return self.car_codes or []
    def getpdctrefs(self):
        return self.refs or []
    def __str__(self) -> str:
        return f'{self.brandref}-{self.brand}-{self.car_codes}-{self.categoryid}-{self.assemblyGroups}'
# this is just for serving the brands
class Brand(models.Model):
    # code will be the categoryid and assembly id, this is to know which brands to serve
    code=models.CharField(max_length=500, default=None, null=True, blank=True)
    brands=models.JSONField(default=list, null=True, blank=True)
    def __str__(self) -> str:
        return self.code
# this is to track the products of that brand izd llan 4 labasz n4d oho
class Brandpdcts(models.Model):
    # code will be brandcode-vehiculecode-assambly
    code=models.CharField(max_length=500, default=None, null=True, blank=True)
    loaded=models.BooleanField(default=False)
    def __str__(self) -> str:
        return self.code

# this is to track the products of that ref izd llan 4 labasz n4d oho
class Refpdcts(models.Model):
    # code will be ref-assambly
    code=models.CharField(max_length=500, default=None, null=True, blank=True)
    loaded=models.BooleanField(default=False)
    brands=models.JSONField(default=list, null=True, blank=True)
    def __str__(self) -> str:
        return self.code
class Carmodel(models.Model):
    manifacturer_code=models.CharField(max_length=500, default=None, null=True, blank=True)
    models=models.JSONField(default=list, null=True, blank=True)

class Cartarget(models.Model):
    model_code=models.CharField(max_length=500, default=None, null=True, blank=True)
    targets=models.JSONField(default=list, null=True, blank=True)

class Configuration(models.Model):
    # to decide weather searching in db first,
    searchdb=models.BooleanField(default=False)
    # accounts of rep
    accounts=models.JSONField(default=list, null=True, blank=True)
    
class Systemstock(models.Model):
    name=models.CharField(max_length=900)
    description=models.TextField()
    price=models.FloatField(default=0.00)
    forclient=models.BooleanField(default=False)
    def __str__(self) -> str:
        return f'{self.name} {self.price} {"Client" if self.forclient else "suppl"}'