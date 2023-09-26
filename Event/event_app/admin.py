from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'date_created')
    search_fields = ('title', 'creator__username')
    list_filter = ('date_created',)
