from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import date, timedelta
import zoneinfo
from beauty.models import Item, Notification


class Command(BaseCommand):
    help = 'コスメアイテムの使用期限に基づいて通知を生成します'

    def handle(self, *args, **options):
        """通知生成のメイン処理"""
        tokyo_tz = zoneinfo.ZoneInfo('Asia/Tokyo')
        now_tokyo = timezone.now().astimezone(tokyo_tz)
        today_tokyo = now_tokyo.date()
        
        self.stdout.write(f"通知生成開始: {today_tokyo} ({now_tokyo.strftime('%A')})")
        
        created_counts = {
            'expired': 0,
            'week': 0,
            'biweek': 0,
            'month': 0
        }
        
        with transaction.atomic():
            # 期限切れ通知（毎週月曜日のみ）
            if now_tokyo.weekday() == 0:  # 月曜日 (0=月曜日)
                created_counts['expired'] = self._generate_expired_notifications(today_tokyo)
            
            # 30日以内通知
            created_counts['month'] = self._generate_expiry_notifications(
                today_tokyo, 30, 'D30', '期限30日以内のアイテムがあります'
            )
            
            # 14日以内通知
            created_counts['biweek'] = self._generate_expiry_notifications(
                today_tokyo, 14, 'D14', '期限14日以内のアイテムがあります'
            )
            
            # 7日以内通知
            created_counts['week'] = self._generate_expiry_notifications(
                today_tokyo, 7, 'D7', '期限7日以内のアイテムがあります'
            )
        
        # 結果出力
        total_created = sum(created_counts.values())
        self.stdout.write(
            self.style.SUCCESS(f'通知生成完了: 合計{total_created}件')
        )
        
        for notification_type, count in created_counts.items():
            if count > 0:
                self.stdout.write(f'  {notification_type}: {count}件')

    def _generate_expired_notifications(self, today):
        """期限切れ通知を生成（週次・月曜日のみ）"""
        expired_items = Item.objects.filter(
            expires_on__lt=today,
            status='using'
        ).select_related('user')
        
        created_count = 0
        for item in expired_items:
            # 重複チェック: 同じユーザー・アイテム・タイプの通知が既に存在するか
            existing = Notification.objects.filter(
                user=item.user,
                item=item,
                type='OVERWEEK',
                scheduled_for__date=today
            ).exists()
            
            if not existing:
                Notification.objects.create(
                    user=item.user,
                    item=item,
                    type='OVERWEEK',
                    title='使用期限切れのアイテムがあります',
                    body=f'{item.name}の使用期限が過ぎています（期限: {item.expires_on}）',
                    scheduled_for=timezone.now()
                )
                created_count += 1
        
        return created_count

    def _generate_expiry_notifications(self, today, days_threshold, notification_type, title):
        """指定期間以内の期限通知を生成（1回のみ）"""
        target_date = today + timedelta(days=days_threshold)
        
        # 期限がdays_threshold日以内（当日含む）のアイテムを取得
        items_in_range = Item.objects.filter(
            expires_on__lte=target_date,
            expires_on__gte=today,
            status='using'
        ).select_related('user')
        
        created_count = 0
        for item in items_in_range:
            # 重複チェック: 同じユーザー・アイテム・タイプの通知が既に存在するか
            existing = Notification.objects.filter(
                user=item.user,
                item=item,
                type=notification_type
            ).exists()
            
            if not existing:
                days_until_expiry = (item.expires_on - today).days
                Notification.objects.create(
                    user=item.user,
                    item=item,
                    type=notification_type,
                    title=title,
                    body=f'{item.name}の使用期限が{days_until_expiry}日後です（期限: {item.expires_on}）',
                    scheduled_for=timezone.now()
                )
                created_count += 1
        
        return created_count