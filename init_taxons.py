"""
Create initial Taxon data for the cosmetics expiry tracking app.
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cosme_expiry_app.settings')
django.setup()

from beauty.models import Taxon

def create_taxon_hierarchy():
    """
    Create a three-level hierarchy of cosmetic categories:
    Main categories > Subcategories > Product types
    """
    # Make sure we don't create duplicates
    if Taxon.objects.count() > 0:
        print("Taxon data already exists. Skipping creation.")
        return
    
    # Main categories (level 0)
    makeup = Taxon.objects.create(name="メイクアップ")
    skincare = Taxon.objects.create(name="スキンケア")
    haircare = Taxon.objects.create(name="ヘアケア")
    fragrance = Taxon.objects.create(name="フレグランス")
    
    # Makeup subcategories (level 1)
    face = Taxon.objects.create(name="ベースメイク", parent=makeup)
    eye = Taxon.objects.create(name="アイメイク", parent=makeup)
    lip = Taxon.objects.create(name="リップ", parent=makeup)
    cheek = Taxon.objects.create(name="チーク", parent=makeup)
    
    # Skincare subcategories (level 1)
    cleansers = Taxon.objects.create(name="クレンジング・洗顔", parent=skincare)
    moisturizers = Taxon.objects.create(name="保湿ケア", parent=skincare)
    treatments = Taxon.objects.create(name="美容液・トリートメント", parent=skincare)
    masks = Taxon.objects.create(name="パック・マスク", parent=skincare)
    
    # Haircare subcategories (level 1)
    shampoo_cond = Taxon.objects.create(name="シャンプー・コンディショナー", parent=haircare)
    styling = Taxon.objects.create(name="スタイリング剤", parent=haircare)
    treatments_hair = Taxon.objects.create(name="トリートメント", parent=haircare)
    
    # Fragrance subcategories (level 1)
    perfume = Taxon.objects.create(name="香水", parent=fragrance)
    body_mist = Taxon.objects.create(name="ボディミスト", parent=fragrance)
    
    # Product types for Face (level 2)
    Taxon.objects.create(name="ファンデーション", parent=face)
    Taxon.objects.create(name="コンシーラー", parent=face)
    Taxon.objects.create(name="BBクリーム", parent=face)
    Taxon.objects.create(name="CCクリーム", parent=face)
    Taxon.objects.create(name="フェイスパウダー", parent=face)
    Taxon.objects.create(name="プライマー", parent=face)
    
    # Product types for Eye (level 2)
    Taxon.objects.create(name="アイシャドウ", parent=eye)
    Taxon.objects.create(name="アイライナー", parent=eye)
    Taxon.objects.create(name="マスカラ", parent=eye)
    Taxon.objects.create(name="アイブロウ", parent=eye)
    
    # Product types for Lip (level 2)
    Taxon.objects.create(name="口紅", parent=lip)
    Taxon.objects.create(name="リップグロス", parent=lip)
    Taxon.objects.create(name="リップティント", parent=lip)
    Taxon.objects.create(name="リップライナー", parent=lip)
    Taxon.objects.create(name="リップバーム", parent=lip)
    
    # Product types for Cheek (level 2)
    Taxon.objects.create(name="パウダーチーク", parent=cheek)
    Taxon.objects.create(name="クリームチーク", parent=cheek)
    Taxon.objects.create(name="チークティント", parent=cheek)
    
    # Product types for Cleansers (level 2)
    Taxon.objects.create(name="クレンジングオイル", parent=cleansers)
    Taxon.objects.create(name="クレンジングフォーム", parent=cleansers)
    Taxon.objects.create(name="クレンジングジェル", parent=cleansers)
    Taxon.objects.create(name="ミセラーウォーター", parent=cleansers)
    Taxon.objects.create(name="洗顔料", parent=cleansers)
    
    # Product types for Moisturizers (level 2)
    Taxon.objects.create(name="化粧水", parent=moisturizers)
    Taxon.objects.create(name="乳液", parent=moisturizers)
    Taxon.objects.create(name="フェイスクリーム", parent=moisturizers)
    Taxon.objects.create(name="フェイスオイル", parent=moisturizers)
    Taxon.objects.create(name="美容オイル", parent=moisturizers)
    
    # Product types for Treatments (level 2)
    Taxon.objects.create(name="美容液", parent=treatments)
    Taxon.objects.create(name="アンプル", parent=treatments)
    Taxon.objects.create(name="セラム", parent=treatments)
    Taxon.objects.create(name="アイクリーム", parent=treatments)
    Taxon.objects.create(name="ニキビケア", parent=treatments)
    
    # Product types for Masks (level 2)
    Taxon.objects.create(name="シートマスク", parent=masks)
    Taxon.objects.create(name="クレイマスク", parent=masks)
    Taxon.objects.create(name="ジェルマスク", parent=masks)
    Taxon.objects.create(name="スリーピングマスク", parent=masks)
    
    # Product types for Shampoo & Conditioner (level 2)
    Taxon.objects.create(name="シャンプー", parent=shampoo_cond)
    Taxon.objects.create(name="コンディショナー", parent=shampoo_cond)
    Taxon.objects.create(name="スカルプケア", parent=shampoo_cond)
    
    # Product types for Styling (level 2)
    Taxon.objects.create(name="ヘアワックス", parent=styling)
    Taxon.objects.create(name="ヘアスプレー", parent=styling)
    Taxon.objects.create(name="ヘアジェル", parent=styling)
    Taxon.objects.create(name="ヘアオイル", parent=styling)
    
    # Product types for Hair Treatments (level 2)
    Taxon.objects.create(name="ヘアマスク", parent=treatments_hair)
    Taxon.objects.create(name="ヘアパック", parent=treatments_hair)
    Taxon.objects.create(name="ヘアエッセンス", parent=treatments_hair)
    
    # Product types for Perfume (level 2)
    Taxon.objects.create(name="オードパルファム", parent=perfume)
    Taxon.objects.create(name="オードトワレ", parent=perfume)
    Taxon.objects.create(name="ソリッドパフューム", parent=perfume)
    
    # Product types for Body Mist (level 2)
    Taxon.objects.create(name="ボディミスト", parent=body_mist)
    Taxon.objects.create(name="ルームスプレー", parent=body_mist)
    
    print(f"Created {Taxon.objects.count()} taxon categories successfully.")

if __name__ == "__main__":
    create_taxon_hierarchy()