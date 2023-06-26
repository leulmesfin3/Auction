from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(ActivityLog)
admin.site.register(UserDetail)
admin.site.register(Comment)
admin.site.register(Condition)
admin.site.register(Category)
admin.site.register(Status)
admin.site.register(Item)
admin.site.register(ItemPriceHistory)
admin.site.register(ItemStatusHistory)