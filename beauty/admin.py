# beauty/admin.py

from django.contrib import admin
from .models import Taxon, Item, Notification, LlmSuggestionLog

@admin.register(Taxon)
class TaxonAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'depth', 'full_path', 'is_leaf')
    list_filter = ('depth',)
    search_fields = ('name', 'full_path')
    ordering = ('depth', 'name')
    
    def is_leaf(self, obj):
        return obj.is_leaf
    is_leaf.boolean = True
    is_leaf.short_description = '葉ノード'

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'brand', 'status', 'expires_on', 'risk_flag')
    list_filter = ('status', 'risk_flag', 'product_type__parent__parent')
    search_fields = ('name', 'brand', 'product_type__full_path')
    date_hierarchy = 'expires_on'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product_type":
            # 葉ノードのみ選択可能
            kwargs["queryset"] = Taxon.objects.filter(children__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'type', 'title', 'scheduled_for', 'read_at', 'created_at')
    list_filter = ('type', 'read_at', 'created_at')
    search_fields = ('title', 'body')
    date_hierarchy = 'scheduled_for'
    readonly_fields = ('created_at',)

@admin.register(LlmSuggestionLog)
class LlmSuggestionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'target', 'suggested_taxon', 'chosen_taxon', 'accepted', 'created_at')
    list_filter = ('target', 'accepted', 'created_at')
    search_fields = ('suggested_text',)