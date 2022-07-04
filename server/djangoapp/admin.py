from django.contrib import admin
# from .models import related models

from .models import CarModel, CarMake
# Register your models here.

# CarModelInline class
class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 5

class CarMakeInline(admin.StackedInline):
    model = CarMake
    extra = 5


# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'year')
    list_filter = ['year']
    search_fields = ['name', 'description']

class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_display = ('name', 'description')
    search_fields = ['name', 'description']

# CarMakeAdmin class with CarModelInline

# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)
