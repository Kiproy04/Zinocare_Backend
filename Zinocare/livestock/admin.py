from django.contrib import admin
from .models import Animal

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ("name", "breed", "species", "mkulima", "sex", "date_of_birth")
    search_fields = ("name", "species", "breed", "date_of_birth")
    list_filter = ("breed", "species")
