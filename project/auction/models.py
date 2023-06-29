from django.db import models
from colorfield.fields import ColorField
from django.contrib.auth.models import User
import os

# Create your models here.

class ActivityLog(models.Model):
    module = models.CharField(max_length=100, null=False, blank=False)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    ip = models.CharField(max_length=100, null=True, blank=True)
    extra = models.TextField(null=True, blank=True)
    createdOn = models.DateTimeField(
        auto_now_add=True, blank=True, null=True, editable=True)
    def get_client_ip(request):
        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            ip = request.META.get("HTTP_X_REAL_IP")
            return str(ip)
        except:
            return ''
    
    def add(self, module, request):
        try:
            extra = {"get":dict(request.GET),"post":dict(request.POST), "body":str(request.body)}
            activityLog = ActivityLog()
            activityLog.module = module
            if request.user.is_authenticated:
                activityLog.user = request.user
            activityLog.extra = extra
            activityLog.ip = request.META.get("HTTP_X_REAL_IP").split(',')[0]
            activityLog.save()
        except:
            pass
        
    def __str__(self):
        return str(str(self.user) + " => " + self.module+ " => " + str(self.createdOn))
    
class Comment(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    text = models.TextField(null=False, blank=False)
    createdOn = models.DateTimeField( auto_now_add=True, blank=True, null=True, editable=True)
    updatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    def __str__(self):
        return str(self.text)    
    
class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null= False, primary_key=True) 
    phone = models.CharField(max_length=30, null=True, blank=True) 
    createdOn = models.DateTimeField( auto_now_add=True, blank=True, null=True, editable=True)
    updatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    comment =  models.ManyToManyField(Comment, blank=True)
    def __str__(self):
        return str(self.user)

    
class Condition(models.Model):
    name = models.CharField(max_length=60, null=False, blank=False)
    active = models.BooleanField(default=True, null=False, blank=False) 
    createdOn = models.DateTimeField( auto_now_add=True, blank=True, null=True, editable=True)
    updatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    comment =  models.ManyToManyField(Comment, blank=True)
    def __str__(self):
        return str(self.name)
    
class Category(models.Model):
    name = models.CharField(max_length=60, null=False, blank=False)
    active = models.BooleanField(default=True, null=False, blank=False) 
    createdOn = models.DateTimeField( auto_now_add=True, blank=True, null=True, editable=True)
    updatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    comment =  models.ManyToManyField(Comment, blank=True)
    def __str__(self):
        return str(self.name)
    

class Status(models.Model):
    name = models.CharField(max_length=60, null=False, blank=False)
    backgroundColor = ColorField(default='#14a44d', null=False, blank=False) 
    active = models.BooleanField(default=True, null=False, blank=False) 
    createdOn = models.DateTimeField( auto_now_add=True, blank=True, null=True, editable=True)
    updatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    comment =  models.ManyToManyField(Comment, blank=True)
    def __str__(self):
        return str(self.name)


class Item(models.Model):
    img = models.ImageField(upload_to = "auction/static/img/images/", null=True, blank=True)
    name = models.CharField(max_length=60, null=False, blank=False)
    starting_price = models.DecimalField(null=False, blank=False, max_digits=8, decimal_places=2, default=0.0)
    min_increase_price = models.DecimalField(null=False, blank=False, max_digits=8, decimal_places=2, default=0.0)
    max_increase_price = models.DecimalField(null=False, blank=False, max_digits=8, decimal_places=2, default=0.0)
    condition = models.ForeignKey(Condition, blank=False, null=False, on_delete=models.RESTRICT)
    status = models.ForeignKey(Status, blank=False, null=False, on_delete=models.RESTRICT)
    category = models.ManyToManyField(Category, blank=True)
    tag = models.CharField(max_length=60, null=False, blank=False)
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.RESTRICT)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True, null=False, blank=False) 
    createdOn = models.DateTimeField( auto_now_add=True, blank=True, null=True, editable=True)
    updatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    comment =  models.ManyToManyField(Comment, blank=True)
    
    def current_price(self):
        price_history = self.itempricehistory_set.all()
        # print(price_history)
        if not price_history:
            return self.starting_price
        return price_history.order_by("createdOn").last().price
    
    def bids(self):
        price_history = self.itempricehistory_set.all()
        return price_history.count()
    
    def last_price(self, user):
        price_history = self.itempricehistory_set.filter(user = user)
        if price_history:
            return price_history.order_by("createdOn").last().price
        return "-"
    
    def rank(self, user):
        price_history = self.itempricehistory_set.all()
        if price_history.filter(user = user):
            return price_history.filter(price__gt = self.last_price(user)).count() + 1
        return "-"
    
    def imgFileName(self):
        return os.path.basename(self.img.name)
    
    def imgFilePath(self):
        return 'img/images/' + str(os.path.basename(self.img.name))
    
    def __str__(self):
        return str(self.name)
    
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     lastPrice = ItemPriceHistory.objects.filter().order_by("-createdOn")
    #     if not lastPrice or lastPrice.last().price != self.price: 
    #         itemPriceHistory = ItemPriceHistory()
    #         itemPriceHistory.item = self
    #         itemPriceHistory.price = self.price
    #         itemPriceHistory.save()
            
            
class ItemPriceHistory(models.Model):
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.RESTRICT)
    item = models.ForeignKey(Item, blank=False, null=False, on_delete=models.RESTRICT)
    active = models.BooleanField(default=True, null=False, blank=False) 
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False, default=0.0)
    createdOn = models.DateTimeField( auto_now_add=True, blank=True, null=True, editable=True)
    updatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    def __str__(self):
        return str(self.item.name)
            
class ItemStatusHistory(models.Model):
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.RESTRICT)
    item = models.ForeignKey(Item, blank=False, null=False, on_delete=models.RESTRICT)
    status = models.ForeignKey(Status, blank=False, null=False, on_delete=models.RESTRICT)
    createdOn = models.DateTimeField( auto_now_add=True, blank=True, null=True, editable=True)
    updatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    def __str__(self):
        return str(self.item.name)