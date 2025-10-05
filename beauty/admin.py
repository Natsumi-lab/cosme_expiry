from django.contrib import admin
from .models import Category, Shape, Item, Notification, LlmSuggestionLog

# Category モデルを管理画面に登録
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

# Shape モデルを管理画面に登録
@admin.register(Shape)
class ShapeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('category', 'created_at')

# Item モデルを管理画面に登録
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'category', 'status', 'opened_on', 'expires_on', 'risk_flag')
    search_fields = ('name', 'brand')
    list_filter = ('status', 'risk_flag', 'category', 'created_at')
    date_hierarchy = 'expires_on'

# Notification モデルを管理画面に登録
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item', 'type', 'title', 'scheduled_for', 'read_at')
    search_fields = ('title', 'body')
    list_filter = ('type', 'read_at', 'created_at')

# LlmSuggestionLog モデルを管理画面に登録
@admin.register(LlmSuggestionLog)
class LlmSuggestionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item', 'target', 'accepted', 'created_at')
    search_fields = ('chosen_value',)
    list_filter = ('target', 'accepted', 'created_at')