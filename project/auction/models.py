from django.db import models
from django.contrib.auth.models import User

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
    
    
class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null= False, primary_key=True) 
    phone = models.CharField(max_length=30, null=True, blank=True) 
    createdOn = models.DateTimeField( auto_now_add=True, blank=True, null=True, editable=True)
    updatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    def __str__(self):
        return str(self.user)
    
class Comment(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    text = models.TextField(null=False, blank=False)
    createdOn = models.DateTimeField( auto_now_add=True, blank=True, null=True, editable=True)
    updatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    def __str__(self):
        return str(self.text)
    
class Condition(models.Model):
    name = models.CharField(max_length=60, null=False, blank=False)
    active = models.BooleanField(default=True, null=False, blank=False) 
    createdOn = models.DateTimeField( auto_now_add=True, blank=True, null=True, editable=True)
    updatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    comment =  models.ManyToManyField(Comment, blank=True)
    def __str__(self):
        return str(self.text)
    
class Category(models.Model):
    name = models.CharField(max_length=60, null=False, blank=False)
    active = models.BooleanField(default=True, null=False, blank=False) 
    createdOn = models.DateTimeField( auto_now_add=True, blank=True, null=True, editable=True)
    updatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    comment =  models.ManyToManyField(Comment, blank=True)
    def __str__(self):
        return str(self.text)
