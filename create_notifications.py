"""
Generate notifications for existing items in the cosmetics expiry tracking app.
"""

import os
import django
from datetime import date, timedelta, datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cosme_expiry_app.settings')
django.setup()

from beauty.models import Item, Notification
from django.utils import timezone

def create_notifications():
    """
    Generate appropriate notifications for all existing items
    """
    # Check if we already have notifications
    if Notification.objects.count() > 0:
        print(f"There are already {Notification.objects.count()} notifications in the database. Skipping creation.")
        return
    
    # Get all active (using) items
    active_items = Item.objects.filter(status='using')
    
    if not active_items:
        print("No active items found. Please create some items first.")
        return
    
    today = date.today()
    now = timezone.now()
    notifications_created = 0
    
    for item in active_items:
        days_remaining = (item.expires_on - today).days
        
        # Generate D30 notification (30 days before expiry)
        if days_remaining <= 30:
            scheduled_date = max(
                now - timedelta(days=1),  # Schedule for yesterday if already past
                datetime.combine(item.expires_on - timedelta(days=30), datetime.min.time(), tzinfo=timezone.get_current_timezone())
            )
            
            Notification.objects.create(
                user=item.user,
                item=item,
                type='D30',
                title=f"使用期限まで残り30日: {item.name}",
                body=f"【期限30日前】{item.name}の使用期限は{item.expires_on.strftime('%Y年%m月%d日')}です。あと30日以内に使い切りましょう。",
                scheduled_for=scheduled_date,
                read_at=None if days_remaining > 30 else now  # Mark as read if already past
            )
            notifications_created += 1
        
        # Generate D14 notification (14 days before expiry)
        if days_remaining <= 14:
            scheduled_date = max(
                now - timedelta(days=1),  # Schedule for yesterday if already past
                datetime.combine(item.expires_on - timedelta(days=14), datetime.min.time(), tzinfo=timezone.get_current_timezone())
            )
            
            Notification.objects.create(
                user=item.user,
                item=item,
                type='D14',
                title=f"使用期限まであと2週間: {item.name}",
                body=f"【期限14日前】{item.name}の使用期限は{item.expires_on.strftime('%Y年%m月%d日')}です。あと2週間以内に使い切りましょう。",
                scheduled_for=scheduled_date,
                read_at=None if days_remaining > 14 else now  # Mark as read if already past
            )
            notifications_created += 1
        
        # Generate D7 notification (7 days before expiry)
        if days_remaining <= 7:
            scheduled_date = max(
                now - timedelta(days=1),  # Schedule for yesterday if already past
                datetime.combine(item.expires_on - timedelta(days=7), datetime.min.time(), tzinfo=timezone.get_current_timezone())
            )
            
            Notification.objects.create(
                user=item.user,
                item=item,
                type='D7',
                title=f"使用期限まであと1週間: {item.name}",
                body=f"【期限7日前】{item.name}の使用期限は{item.expires_on.strftime('%Y年%m月%d日')}です。1週間以内に使い切りましょう。",
                scheduled_for=scheduled_date,
                read_at=None if days_remaining > 7 else now  # Mark as read if already past
            )
            notifications_created += 1
        
        # Generate OVERWEEK notification (after expiry)
        if days_remaining < 0:
            scheduled_date = datetime.combine(item.expires_on, datetime.min.time(), tzinfo=timezone.get_current_timezone())
            
            Notification.objects.create(
                user=item.user,
                item=item,
                type='OVERWEEK',
                title=f"使用期限が切れました: {item.name}",
                body=f"【期限超過】{item.name}は使用期限({item.expires_on.strftime('%Y年%m月%d日')})を{abs(days_remaining)}日超過しています。衛生上の理由から使用を控え、廃棄をご検討ください。",
                scheduled_for=scheduled_date,
                read_at=None  # Always unread for expired items
            )
            notifications_created += 1
    
    print(f"Created {notifications_created} notifications for {active_items.count()} active items.")

if __name__ == "__main__":
    create_notifications()