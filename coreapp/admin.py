from django.contrib import admin
from .models import User, Campaign,Category, Contributions,Requests

# Register your models here.

admin.site.register(User)
admin.site.register(Campaign)
admin.site.register(Category)
admin.site.register(Contributions)
admin.site.register(Requests)
