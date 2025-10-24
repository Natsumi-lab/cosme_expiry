"""
List all Taxon objects in the database
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cosme_expiry_app.settings')
django.setup()

from beauty.models import Taxon

def list_taxons():
    """
    List all Taxon objects in the database
    """
    print("===== All Taxons =====")
    
    # Get all top-level taxons (parent is None)
    root_taxons = Taxon.objects.filter(parent__isnull=True).order_by('name')
    
    for root in root_taxons:
        print(f"[Level 0] {root.id}: {root.name}")
        
        # Get second-level taxons
        for child in Taxon.objects.filter(parent=root).order_by('name'):
            print(f"  [Level 1] {child.id}: {child.name}")
            
            # Get third-level taxons
            for grandchild in Taxon.objects.filter(parent=child).order_by('name'):
                print(f"    [Level 2] {grandchild.id}: {grandchild.name}")
    
    print(f"\nTotal taxons: {Taxon.objects.count()}")

if __name__ == "__main__":
    list_taxons()