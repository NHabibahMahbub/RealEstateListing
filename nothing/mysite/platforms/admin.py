from django.contrib import admin
from .models import Platform, Inquiry, Bid

# Register your models here.
admin.site.register(Platform)
admin.site.register(Inquiry)
admin.site.register(Bid)
