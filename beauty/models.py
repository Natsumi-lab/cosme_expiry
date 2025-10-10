from django.db import models
from django.conf import settings
from django.utils import timezone

class BaseModel(models.Model):
    """共通フィールド"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        abstract = True

# ===== Taxonモデル（新規追加） =====
class Taxon(models.Model):
    """商品カテゴリ（階層構造）"""
    name = models.CharField(max_length=100, verbose_name="カテゴリ名")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="親カテゴリ"
    )
    depth = models.IntegerField(default=0, verbose_name="階層レベル")
    full_path = models.CharField(max_length=300, blank=True, verbose_name="フルパス")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    @property
    def is_leaf(self):
        return not self.children.exists()
    
    class Meta:
        verbose_name = "カテゴリ"
        verbose_name_plural = "カテゴリ"
        ordering = ['depth', 'name']
    
    def save(self, *args, **kwargs):
        if self.parent:
            self.depth = self.parent.depth + 1
            self.full_path = f"{self.parent.full_path} > {self.name}"
        else:
            self.depth = 0
            self.full_path = self.name
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.full_path

# ===== Itemモデル（修正版） =====
class Item(BaseModel):
    """アイテム"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="ユーザー"
    )
    
    # 変更: category_id → product_type
    product_type = models.ForeignKey(
        Taxon,
        on_delete=models.CASCADE,
        verbose_name="商品カテゴリ",
        help_text="最も詳細なカテゴリを選択してください"
    )
    
    name = models.CharField(max_length=200, verbose_name="商品名")
    brand = models.CharField(max_length=100, blank=True, verbose_name="ブランド")
    color_code = models.CharField(max_length=50, blank=True, verbose_name="色番/カラー")
    image_url = models.CharField(max_length=500, blank=True, verbose_name="画像URL")
    image = models.ImageField(upload_to='items/', blank=True, null=True, verbose_name="商品画像")
    
    opened_on = models.DateField(verbose_name="開封日")
    expires_on = models.DateField(verbose_name="使用期限")
    expires_overridden = models.BooleanField(default=False, verbose_name="期限手動上書き")
    
    STATUS_CHOICES = [
        ('using', '使用中'),
        ('finished', '使用済み'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='using',
        verbose_name="ステータス"
    )
    finished_at = models.DateField(null=True, blank=True, verbose_name="使用終了日")
    
    RISK_CHOICES = [
        ('low', '低'),
        ('mid', '中'),
        ('high', '高'),
    ]
    risk_flag = models.CharField(
        max_length=10,
        choices=RISK_CHOICES,
        blank=True,
        verbose_name="期限リスク"
    )
    
    memo = models.TextField(blank=True, verbose_name="メモ")
    
    @property
    def main_category(self):
        """大分類を取得"""
        taxon = self.product_type
        while taxon.parent:
            taxon = taxon.parent
        return taxon
    
    @property
    def middle_category(self):
        """中分類を取得"""
        taxon = self.product_type
        if taxon.depth == 2 and taxon.parent:
            return taxon.parent
        elif taxon.depth == 1:
            return taxon
        return None
    
    class Meta:
        verbose_name = "アイテム"
        verbose_name_plural = "アイテム"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.product_type})"

# ===== Notificationモデル（変更なし） =====
class Notification(BaseModel):
    """通知"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    
    TYPE_CHOICES = [
        ('D30', '30日前'),
        ('D14', '14日前'),
        ('D7', '7日前'),
        ('OVERWEEK', '期限切れ'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="通知種別")
    title = models.CharField(max_length=200, verbose_name="通知タイトル")
    body = models.TextField(verbose_name="通知本文")
    scheduled_for = models.DateTimeField(verbose_name="通知予定時刻")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="既読時刻")
    
    class Meta:
        verbose_name = "通知"
        verbose_name_plural = "通知"
        ordering = ['-scheduled_for']
    
    def __str__(self):
        return f"{self.title} - {self.user}"

# ===== LlmSuggestionLogモデル（修正版） =====
class LlmSuggestionLog(BaseModel):
    """LLM提案ログ"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, null=True, blank=True, on_delete=models.SET_NULL)
    
    target = models.CharField(
        max_length=20,
        choices=[
            ('category', 'カテゴリ'),
            ('product_name', '商品名'),
            ('brand', 'ブランド'),
        ],
        verbose_name="推定対象"
    )
    
    suggested_text = models.TextField(verbose_name="LLM推定テキスト")
    
    # 新規追加
    suggested_taxon = models.ForeignKey(
        Taxon,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='llm_suggestions',
        verbose_name="推定カテゴリ"
    )
    
    # 新規追加
    chosen_taxon = models.ForeignKey(
        Taxon,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_choices',
        verbose_name="選択カテゴリ"
    )
    
    accepted = models.BooleanField(default=False, verbose_name="採用")
    
    class Meta:
        verbose_name = "LLM提案ログ"
        verbose_name_plural = "LLM提案ログ"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.target} - {self.user}"