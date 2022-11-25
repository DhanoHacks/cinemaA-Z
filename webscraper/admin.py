from django.contrib import admin
from .models import MovieData, List, Items

# Register your models here.
admin.site.register(MovieData)
admin.site.register(List)
admin.site.register(Items)