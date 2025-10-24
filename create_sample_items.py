"""
Create sample items for testing the cosmetics expiry tracking app.
"""

import os
import django
from datetime import date, timedelta
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cosme_expiry_app.settings')
django.setup()

from django.contrib.auth import get_user_model
from beauty.models import Item, Taxon

def create_sample_items():
    """
    Create sample items for testing
    """
    User = get_user_model()
    
    # Make sure we have a user to associate with items
    try:
        user = User.objects.get(username='admin2')
    except User.DoesNotExist:
        print("User 'admin2' not found. Please create this user first.")
        return
    
    # Get leaf taxons (those without children)
    leaf_taxons = [
        taxon for taxon in Taxon.objects.all()
        if not Taxon.objects.filter(parent=taxon).exists()
    ]
    
    if not leaf_taxons:
        print("No leaf taxons found. Please create taxon hierarchy first.")
        return
    
    # Check if we already have items
    if Item.objects.count() > 0:
        print(f"There are already {Item.objects.count()} items in the database. Skipping creation.")
        return
    
    # Sample brand names
    brands = [
        "資生堂", "カネボウ", "コーセー", "NARS", "MAC", "エスティローダー", 
        "イヴ・サンローラン", "ディオール", "シャネル", "THREE", "SUQQU", "RMK",
        "ADDICTION", "Dior", "ETUDE HOUSE", "LANEIGE", "innisfree", "KATE", "OPERA"
    ]
    
    # Sample colors and codes
    color_codes = [
        "01 ナチュラル", "02 ベージュ", "03 ピンク", "04 コーラル", "05 レッド", 
        "06 オレンジ", "07 ブラウン", "08 プラム", "09 ヌード", "10 ローズ",
        "PK-1", "BE-2", "OR-3", "RD-4", "BR-5", "GD-6", "BK-7"
    ]
    
    # Sample product names for different categories
    product_names = {
        "foundation": ["エアリーステイ", "シンクロスキン", "アクアリフト", "パーフェクトルフィル", "ラディアント"],
        "mascara": ["ラッシュセンセーション", "ボリュームインパクト", "カールキープ", "フルダイナミック", "ロングアンドカール"],
        "lipstick": ["ベルベットマット", "クリーミーグロウ", "リップスティックミニ", "カラーステイ", "ウルトラピグメント"],
        "eyeshadow": ["アイカラーパレット", "シマリングアイズ", "デュオアイシャドウ", "クリームアイカラー", "カラースフレ"],
        "skincare": ["モイスチャライザー", "ブライトニングセラム", "クリアローション", "ハイドレイティングミルク", "バランシングトナー"]
    }
    
    # Create 10 sample items
    for i in range(10):
        # Random product type
        product_type = random.choice(leaf_taxons)
        
        # Determine product category for naming
        category_key = "skincare"
        if "ファンデーション" in product_type.full_path:
            category_key = "foundation"
        elif "マスカラ" in product_type.full_path:
            category_key = "mascara"
        elif "リップ" in product_type.full_path:
            category_key = "lipstick"
        elif "アイシャドウ" in product_type.full_path:
            category_key = "eyeshadow"
        
        # Generate random dates
        today = date.today()
        opened_days_ago = random.randint(10, 200)
        opened_on = today - timedelta(days=opened_days_ago)
        
        # Calculate expiry based on product type
        if "マスカラ" in product_type.full_path:
            # Mascara typically lasts 3-6 months
            shelf_life_days = random.randint(90, 180)
        elif "リップ" in product_type.full_path:
            # Lipsticks typically last 1-2 years
            shelf_life_days = random.randint(365, 730)
        elif "ファンデーション" in product_type.full_path:
            # Foundations typically last 6-12 months
            shelf_life_days = random.randint(180, 365)
        elif "スキンケア" in product_type.full_path:
            # Skincare typically lasts 6-12 months
            shelf_life_days = random.randint(180, 365)
        else:
            # Default 12 months
            shelf_life_days = 365
            
        expires_on = opened_on + timedelta(days=shelf_life_days)
        
        # Calculate risk flag
        days_remaining = (expires_on - today).days
        if days_remaining < 0:
            risk_flag = 'high'
        elif days_remaining <= 14:
            risk_flag = 'mid'
        else:
            risk_flag = 'low'
        
        # Status and finished_at
        status = 'using'
        finished_at = None
        if random.random() < 0.3:  # 30% chance to be finished
            status = 'finished'
            finished_at = today - timedelta(days=random.randint(1, 30))
        
        # Create the item
        brand = random.choice(brands)
        name = f"{brand} {random.choice(product_names[category_key])}"
        color_code = random.choice(color_codes) if random.random() < 0.7 else ""
        
        item = Item.objects.create(
            user=user,
            product_type=product_type,
            name=name,
            brand=brand,
            color_code=color_code,
            opened_on=opened_on,
            expires_on=expires_on,
            expires_overridden=False,
            status=status,
            finished_at=finished_at,
            risk_flag=risk_flag,
            memo=f"サンプルアイテム #{i+1}" if random.random() < 0.5 else ""
        )
        
        print(f"Created item: {item.name} (expires on: {item.expires_on}, risk: {item.risk_flag})")
    
    print(f"Created {Item.objects.count()} sample items successfully.")

if __name__ == "__main__":
    create_sample_items()