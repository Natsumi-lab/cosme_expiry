from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date


class BaseModel(models.Model):
    """
    共通フィールド（作成日時・更新日時）を提供する抽象ベースモデル
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        abstract = True


class Category(BaseModel):
    """
    コスメのカテゴリ（リップ、アイシャドウ、ファンデーション等）
    """
    name = models.TextField(unique=True, verbose_name='カテゴリ名')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'カテゴリ'
        verbose_name_plural = 'カテゴリ'
        ordering = ['name']


class Shape(BaseModel):
    """
    コスメの形状（リキッド、パウダー、クリーム等）
    """
    name = models.TextField(unique=True, verbose_name='形状名')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='カテゴリ',
        related_name='shapes'
    )

    def __str__(self):
        if self.category:
            return f"{self.category.name} - {self.name}"
        return self.name

    class Meta:
        verbose_name = '形状'
        verbose_name_plural = '形状'
        ordering = ['category__name', 'name']


class Item(BaseModel):
    """
    ユーザーが登録するコスメアイテム
    """
    STATUS_CHOICES = [
        ('using', '使用中'),
        ('finished', '使用済み'),
    ]
    
    RISK_FLAG_CHOICES = [
        ('low', '低'),
        ('mid', '中'),
        ('high', '高'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='ユーザー',
        related_name='items',
        db_index=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='カテゴリ',
        related_name='items'
    )
    shape = models.ForeignKey(
        Shape,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='形状',
        related_name='items'
    )
    name = models.TextField(verbose_name='商品名', db_index=True)
    brand = models.TextField(null=True, blank=True, verbose_name='ブランド', db_index=True)
    color_code = models.TextField(null=True, blank=True, verbose_name='色番/カラー')
    image_url = models.TextField(null=True, blank=True, verbose_name='画像URL')
    opened_on = models.DateField(verbose_name='開封日', db_index=True)
    expires_on = models.DateField(verbose_name='消費期限日', db_index=True)
    expires_overridden = models.BooleanField(
        default=False,
        verbose_name='期限手動上書き'
    )
    status = models.TextField(
        choices=STATUS_CHOICES,
        default='using',
        verbose_name='ステータス',
        db_index=True
    )
    finished_at = models.DateField(
        null=True,
        blank=True,
        verbose_name='使用終了日'
    )
    risk_flag = models.TextField(
        choices=RISK_FLAG_CHOICES,
        null=True,
        blank=True,
        verbose_name='期限リスク',
        db_index=True
    )
    memo = models.TextField(null=True, blank=True, verbose_name='メモ')

    def clean(self):
        """
        Item固有のバリデーション
        """
        super().clean()
        
        if self.status == 'finished':
            if not self.finished_at:
                raise ValidationError({
                    'finished_at': '使用済みの場合、使用終了日は必須です。'
                })
            if self.finished_at != date.today():
                raise ValidationError({
                    'finished_at': '使用終了日は今日の日付のみ設定可能です。'
                })
        elif self.status == 'using':
            if self.finished_at:
                raise ValidationError({
                    'finished_at': '使用中の場合、使用終了日は設定できません。'
                })

    def __str__(self):
        return f"{self.name} ({self.brand or 'ブランド不明'})"

    class Meta:
        verbose_name = 'アイテム'
        verbose_name_plural = 'アイテム'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'expires_on']),
            models.Index(fields=['user', 'risk_flag']),
        ]


class Notification(models.Model):
    """
    ユーザーへの通知（期限切れ警告等）
    """
    TYPE_CHOICES = [
        ('D30', '30日前通知'),
        ('D14', '14日前通知'),
        ('D7', '7日前通知'),
        ('OVERWEEK', '期限超過週次通知'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='ユーザー',
        related_name='notifications',
        db_index=True
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name='アイテム',
        related_name='notifications'
    )
    type = models.TextField(
        choices=TYPE_CHOICES,
        verbose_name='通知種別',
        db_index=True
    )
    title = models.TextField(verbose_name='通知タイトル')
    body = models.TextField(verbose_name='通知本文')
    scheduled_for = models.DateTimeField(
        verbose_name='通知予定時刻',
        db_index=True
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='既読時刻',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    @property
    def is_read(self):
        """既読かどうかを判定"""
        return self.read_at is not None

    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-scheduled_for']
        indexes = [
            models.Index(fields=['user', 'read_at']),
            models.Index(fields=['user', 'scheduled_for']),
        ]


class LlmSuggestionLog(models.Model):
    """
    LLM提案の採用/却下ログ（最小限の記録）
    """
    TARGET_CHOICES = [
        ('category', 'カテゴリ'),
        ('shape', '形状'),
        ('advice', 'アドバイス'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='ユーザー',
        related_name='llm_suggestion_logs',
        db_index=True
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='アイテム',
        related_name='llm_suggestion_logs'
    )
    target = models.TextField(
        choices=TARGET_CHOICES,
        verbose_name='提案対象',
        db_index=True
    )
    accepted = models.BooleanField(
        default=False,
        verbose_name='採用/却下'
    )
    chosen_value = models.TextField(
        null=True,
        blank=True,
        verbose_name='採用した値'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    def __str__(self):
        status = '採用' if self.accepted else '却下'
        return f"{self.user.username} - {self.get_target_display()} - {status}"

    class Meta:
        verbose_name = 'LLM提案ログ'
        verbose_name_plural = 'LLM提案ログ'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'target']),
            models.Index(fields=['user', 'accepted']),
        ]


# マイグレーション実行手順：
# python manage.py makemigrations beauty
# python manage.py migrate