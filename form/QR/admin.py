from django.contrib import admin
from .models import Laptop
from .models import Owner

admin.site.register(Laptop)
admin.site.register(Owner)
