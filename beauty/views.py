from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, FormView, View
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.http import Http404, JsonResponse
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import date, timedelta
from .forms import SignUpForm, SignInForm, ItemForm, UserSettingsForm, PasswordChangeForm
from .models import Taxon, LlmSuggestionLog, Item, Notification
import json
from .llm import suggest_taxon_candidates
from openai import APITimeoutError
from django.db.models import Count



@login_required
def home(request):
    """
    ホームページビュー
    統計データとサンプルアイテムを表示
    ログイン必須
    """
    return render(request, 'home.html')


@method_decorator([csrf_protect, never_cache], name='dispatch')
class SignUpView(CreateView):
    """ユーザー登録ビュー"""
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('beauty:home')  # 後でログインページに変更
    
    def dispatch(self, request, *args, **kwargs):
        """ログイン済みユーザーはホームにリダイレクト"""
        if request.user.is_authenticated:
            messages.info(request, '既にログインしています。')
            return redirect('beauty:home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """登録成功時の処理"""
        response = super().form_valid(form)
        
        # 自動ログイン
        login(self.request, self.object)
        
        # 成功メッセージ
        #messages.success(
        #    self.request, 
        #    f'ようこそ、{self.object.username}さん！アカウントの登録が完了しました。'
        #)
        
        return response
    
    def form_invalid(self, form):
        """登録失敗時の処理"""
        messages.error(
            self.request, 
            '入力内容に誤りがあります。以下のエラーを確認してください。'
        )
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """テンプレートコンテキストに追加データを渡す"""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'アカウント登録'
        context['page_description'] = 'コスメ期限管理アプリのアカウントを新規作成します。'
        return context


@method_decorator([csrf_protect, never_cache], name='dispatch')
class SignInView(FormView):
    """ユーザーログインビュー"""
    form_class = SignInForm
    template_name = 'signin.html'
    success_url = reverse_lazy('beauty:home')
    
    def dispatch(self, request, *args, **kwargs):
        """ログイン済みユーザーはホームにリダイレクト"""
        if request.user.is_authenticated:
            messages.info(request, '既にログインしています。')
            return redirect('beauty:home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """ログイン成功時の処理"""
        # フォームのクリーンデータからユーザー認証
        email = form.cleaned_data['username']  # フォームではusernameフィールドにメールアドレスが入る
        password = form.cleaned_data['password']
        
        # メールアドレスでユーザーを検索してusernameを取得
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(email=email)
            # 見つかったユーザーでパスワードチェック
            if user_obj.check_password(password):
                if user_obj.is_active:
                    # ログイン実行
                    login(self.request, user_obj)
                    
                    # 成功メッセージ
                    #messages.success(
                    #    self.request,
                    #    f'おかえりなさい、{user_obj.get_full_name() or user_obj.username}さん！'
                    #)
                    
                    return super().form_valid(form)
                else:
                    form.add_error(None, 'このアカウントは無効化されています。')
            else:
                form.add_error(None, 'メールアドレスまたはパスワードが正しくありません。')
        except User.DoesNotExist:
            form.add_error('username', 'このメールアドレスは登録されていません。')
        
        return self.form_invalid(form)
    
    def form_invalid(self, form):
        """ログイン失敗時の処理"""
        messages.error(
            self.request,
            'ログインに失敗しました。入力内容を確認してください。'
        )
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """テンプレートコンテキストに追加データを渡す"""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ログイン'
        context['page_description'] = 'コスメ期限管理アプリにログインします。'
        return context


@method_decorator([csrf_protect, require_POST], name='dispatch')
class SignOutView(View):
    """ユーザーログアウトビュー"""
    
    def post(self, request, *args, **kwargs):
        """ログアウト処理"""
        if request.user.is_authenticated:
            # ユーザー名を保存（ログアウト前に取得）
            username = request.user.get_full_name() or request.user.username
            
            # ログアウト実行
            logout(request)
            
            # 成功メッセージ
            #messages.success(
            #    request,
            #    f'{username}さん、お疲れさまでした。またのご利用をお待ちしております。'
            #)
        else:
            # 既にログアウト済み
            messages.info(request, '既にログアウトしています。')
        
        # ログインページにリダイレクト
        return redirect('beauty:signin')


def process_llm_suggestion(user, image_data, product_name_hint=None):
    """
    LLMにカテゴリを推定させる
    """
    # LLM APIを呼び出し
    llm_response = call_llm_api(image_data, product_name_hint)
    # 例：{"category": "リップグロス", "taxon_id": 42, "confidence": 0.95}
    
    # 推定されたTaxonを取得
    suggested_taxon = Taxon.objects.get(id=llm_response['taxon_id'])
    
    # ログに記録
    log = LlmSuggestionLog.objects.create(
        user=user,
        target='category',
        suggested_text=llm_response.get('raw_text', ''),
        suggested_taxon=suggested_taxon,
        accepted=False  # まだユーザー確認前
    )
    
    return {
        'log_id': log.id,
        'suggested_taxon': suggested_taxon,
        'full_path': suggested_taxon.full_path,
        'confidence': llm_response.get('confidence', 0)
    }

def confirm_llm_suggestion(log_id, user_confirmed_taxon_id):
    """
    ユーザーがLLM提案を確認・修正
    """
    log = LlmSuggestionLog.objects.get(id=log_id)
    chosen_taxon = Taxon.objects.get(id=user_confirmed_taxon_id)
    
    log.chosen_taxon = chosen_taxon
    log.accepted = (log.suggested_taxon == chosen_taxon)
    log.save()
    
    return chosen_taxon


@login_required
def item_new(request):
    """アイテム新規登録ビュー"""
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            
            # 画像アップロード処理
            if 'image' in request.FILES:
                # 後でPillowを使った画像処理を追加予定
                pass
            
            item.save()
            
            messages.success(
                request,
                f'「{item.name}」を登録しました。'
            )
            return redirect('beauty:item_detail', id=item.id) 
        else:
            messages.error(
                request,
                'アイテムの登録に失敗しました。入力内容を確認してください。'
            )
    else:
        form = ItemForm()
    
    context = {
        'form': form,
        'page_title': 'アイテム新規登録',
        'page_description': '新しいコスメアイテムを登録します'
    }
    
    return render(request, 'items/new.html', context)

@login_required
def item_list(request):
    """アイテム一覧ビュー（期限タブは再読み込み型）"""

    # ---- パラメータ取得 ----
    tab          = request.GET.get('tab', 'all')          # 期限タブ: all/expired/week/biweek/month/safe
    search       = request.GET.get('search', '').strip()  # 検索
    product_type = request.GET.get('product_type', '')    # カテゴリID（Taxon）
    status       = request.GET.get('status', '')          # using / finished など
    sort         = request.GET.get('sort', 'expires_on')  # ソートキー
    # （優先: tab / 互換: status）
    raw_tab   = request.GET.get('tab', '').strip()
    raw_stat  = request.GET.get('status', '').strip()

    # 互換: ?status=expired/week/biweek/month/safe → tab に正規化
    status_to_tab = {
        'expired': 'expired',
        'week':    'week',
        'biweek':  'biweek',
        'month':   'month',
        'safe':    'safe',
    }
    tab = raw_tab or status_to_tab.get(raw_stat, 'all')

    search       = request.GET.get('search', '').strip()
    product_type = request.GET.get('product_type', '').strip()
    # 「使用中/使い切り」などの状態は state に退避（必要なければこの行は削除）
    state        = request.GET.get('state', '').strip()
    sort         = request.GET.get('sort', 'expires_on').strip()

    # ---- 日付境界（相互排他）----
    today = date.today()
    d7  = today + timedelta(days=7)
    d14 = today + timedelta(days=14)
    d30 = today + timedelta(days=30)

    # ---- ベースクエリ（このユーザーのものだけ）----
    base_qs = Item.objects.filter(user=request.user).select_related('product_type')

    # ---- 検索 ----
    if search:
        base_qs = base_qs.filter(name__icontains=search)

    # ---- カテゴリ（自身＋子孫を含める）----
    if product_type:
        try:
            target_id = int(product_type)
            descendant_ids = [target_id]
            # 簡易BFSで子孫を収集（再帰より安全）
            queue = [target_id]
            while queue:
                pid = queue.pop(0)
                children = list(Taxon.objects.filter(parent_id=pid).values_list('id', flat=True))
                descendant_ids.extend(children)
                queue.extend(children)
            base_qs = base_qs.filter(product_type_id__in=descendant_ids)
        except (ValueError, Taxon.DoesNotExist):
            pass

    # ---- ステータス ----
    if status in ['using', 'finished']:
        base_qs = base_qs.filter(status=status)

    # ---- タブごとのフィルタ（カードのバッジと完全一致：相互排他）----
    qs = base_qs
    if tab == 'expired':
        # 期限切れ：今日より前
        qs = base_qs.filter(expires_on__lt=today)
    elif tab == 'week':
        # 7日以内：今日〜7日後（含む）
        qs = base_qs.filter(expires_on__gte=today, expires_on__lte=d7)
    elif tab == 'biweek':
        # 14日以内：8〜14日後（8日後 = d7+1）
        qs = base_qs.filter(expires_on__gte=d7 + timedelta(days=1), expires_on__lte=d14)
    elif tab == 'month':
        # 30日以内：15〜30日後
        qs = base_qs.filter(expires_on__gte=d14 + timedelta(days=1), expires_on__lte=d30)
    elif tab == 'safe':
        # 余裕あり：30日超
        qs = base_qs.filter(expires_on__gt=d30)
    else:
        tab = 'all'  # 不正値は all 扱い

    # ---- ソート　----
    ORDERING_MAP = {
        'expires_on': 'expires_on',
        '-expires_on': '-expires_on', 
        'created_at': 'created_at',
        '-created_at': '-created_at'
    }
    
    # 不正値が来てもデフォルト（expires_on）にフォールバック
    ordering = ORDERING_MAP.get(sort, 'expires_on')

    # フィルタ済みクエリにソートを適用
    qs = qs.order_by(ordering)

    # ---- カード表示用：残日数＆リスク文言 ----
    items_with_data = []
    for item in qs:
        days_remaining = (item.expires_on - today).days
        if days_remaining < 0:
            risk_level = 'expired'
            risk_text  = '期限切れ'
        elif days_remaining <= 7:
            risk_level = 'critical'
            risk_text  = '期限7日以内'
        elif days_remaining <= 14:
            risk_level = 'warning'
            risk_text  = '期限14日以内'
        elif days_remaining <= 30:
            risk_level = 'caution'
            risk_text  = '期限30日以内'
        else:
            risk_level = 'safe'
            risk_text  = '余裕あり'

        items_with_data.append({
            'item': item,
            'days_remaining': days_remaining,
            'days_remaining_abs': abs(days_remaining),
            'risk_level': risk_level,
            'risk_text': risk_text,
        })

    # ---- バッジ件数（相互排他の同じ境界で計算）----
    counts = {
        'all':     base_qs.count(),
        'expired': base_qs.filter(expires_on__lt=today).count(),
        'week':    base_qs.filter(expires_on__gte=today,                 expires_on__lte=d7).count(),
        'biweek':  base_qs.filter(expires_on__gte=d7 + timedelta(days=1), expires_on__lte=d14).count(),
        'month':   base_qs.filter(expires_on__gte=d14 + timedelta(days=1),expires_on__lte=d30).count(),
        'safe':    base_qs.filter(expires_on__gt=d30).count(),
    }

    # ---- レンダリング ----
    return render(request, 'items/item_list.html', {
        'items_with_data': items_with_data,   # テンプレート側は item.item / item.risk_text で参照
        'current_tab': tab,
        'current_sort': sort,
        'tab_counts': counts,
        'search': search,
        'product_type': product_type,
        'status': status,
    })  
    
    # カテゴリフィルタ（指定されたカテゴリとその子孫を含む）
    # if product_type:
    #     try:
    #         taxon = Taxon.objects.get(id=product_type)
    #         # 自身と子孫のTaxonIDを取得
    #         descendant_ids = [product_type]
    #         def get_descendants(parent_id):
    #             children = Taxon.objects.filter(parent_id=parent_id).values_list('id', flat=True)
    #             for child_id in children:
    #                 descendant_ids.append(child_id)
    #                 get_descendants(child_id)
    #         get_descendants(product_type)
    #         items = items.filter(product_type_id__in=descendant_ids)
    #     except Taxon.DoesNotExist:
    #         pass
    
    
    # 各タブのアイテム数を計算
    all_items = Item.objects.filter(user=request.user)
    
    tab_counts = {
        'all': all_items.count(),
        'expired': all_items.filter(expires_on__lt=today).count(),
        'week': all_items.filter(expires_on__gte=today, expires_on__lte=today + timedelta(days=7)).count(),
        'biweek': all_items.filter(expires_on__gte=today, expires_on__lte=today + timedelta(days=14)).count(),
        'month': all_items.filter(expires_on__gte=today, expires_on__lte=today + timedelta(days=30)).count(),
        'safe': all_items.filter(expires_on__gt=today + timedelta(days=30)).count(),
    }
    
    context = {
        'items_with_data': items_with_data,
        'tab_counts': tab_counts,
        'current_tab': tab,
        'current_search': search,
        'current_status': status,
        'current_sort': sort,
        'page_title': 'アイテム一覧',
        'page_description': '登録したコスメアイテムの一覧を表示します'
    }
    
    return render(request, 'items/item_list.html', context)


@login_required
def item_edit(request, id):
    """アイテム編集ビュー"""
    # ログインユーザーのアイテムのみ取得（セキュリティ対策）
    try:
        item = Item.objects.get(id=id, user=request.user)
    except Item.DoesNotExist:
        other_user_item = Item.objects.filter(id=id).first()
        if other_user_item:
            raise PermissionDenied("このアイテムを編集する権限がありません。")
        else:
            raise Http404("アイテムが見つかりません。")
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            # 差分チェック
            has_changes = False
            for field_name in form.fields:
                original_value = getattr(item, field_name)
                new_value = form.cleaned_data[field_name]
                
                # 特別な処理が必要なフィールド
                if field_name == 'product_type':
                    if original_value.id != new_value.id:
                        has_changes = True
                        break
                elif field_name == 'image':
                    if new_value != original_value:
                        has_changes = True
                        break
                elif original_value != new_value:
                    has_changes = True
                    break
            
            if not has_changes:
                messages.info(request, '変更はありません。')
                return render(request, 'items/edit.html', {
                    'form': form,
                    'item': item,
                    'page_title': f'アイテム編集 - {item.name}',
                    'page_description': f'{item.name}の情報を編集します'
                })
            
            # 変更がある場合は保存
            updated_item = form.save()
            messages.success(request, 'アイテム情報を更新しました。')
            return redirect('beauty:item_detail', id=updated_item.id)
        else:
            messages.error(request, 'アイテムの更新に失敗しました。入力内容を確認してください。')
    else:
        form = ItemForm(instance=item)
    
    context = {
        'form': form,
        'item': item,
        'page_title': f'アイテム編集 - {item.name}',
        'page_description': f'{item.name}の情報を編集します'
    }
    
    return render(request, 'items/edit.html', context)


@login_required
def item_detail(request, id):
    """アイテム詳細ビュー"""
    # ログインユーザーのアイテムのみ取得（セキュリティ対策）
    try:
        item = Item.objects.get(id=id, user=request.user)
    except Item.DoesNotExist:
        other_user_item = Item.objects.filter(id=id).first()
        if other_user_item:
            raise PermissionDenied("このアイテムにアクセスする権限がありません。")
        else:
            raise Http404("アイテムが見つかりません。")
    
    # 残日数とリスクレベルを計算
    today = date.today()
    days_remaining = (item.expires_on - today).days
    days_abs = abs(days_remaining)  # ←★ 追加：絶対値を計算

    # リスクレベル判定
    if days_remaining < 0:
        risk_level = 'expired'
        risk_text = '期限切れ'
        risk_class = 'danger'
    elif days_remaining <= 7:
        risk_level = 'critical'
        risk_text = '期限7日以内'
        risk_class = 'warning'
    elif days_remaining <= 14:
        risk_level = 'warning'
        risk_text = '期限14日以内'
        risk_class = 'warning-orange'
    elif days_remaining <= 30:
        risk_level = 'caution'
        risk_text = '期限30日以内'
        risk_class = 'fine'
    else:
        risk_level = 'safe'
        risk_text = '余裕あり'
        risk_class = 'safety'
    
    context = {
        'item': item,
        'days_remaining': days_remaining,
        'days_abs': days_abs,  # ←★ 追加
        'risk_level': risk_level,
        'risk_text': risk_text,
        'risk_class': risk_class,
        'page_title': f'アイテム詳細 - {item.name}',
        'page_description': f'{item.name}の詳細情報を表示します'
    }
    
    return render(request, 'items/detail.html', context)


@login_required
def api_taxons(request):
    """Taxon階層取得API"""
    from django.http import JsonResponse
    
    parent_id = request.GET.get('parent')
    
    if parent_id:
        try:
            taxons = Taxon.objects.filter(parent_id=parent_id).order_by('name')
        except:
            return JsonResponse({'error': 'Invalid parent ID'}, status=400)
    else:
        # 親がnullのTaxon（大カテゴリ）を取得
        taxons = Taxon.objects.filter(parent__isnull=True).order_by('name')
    
    data = [{'id': t.id, 'name': t.name} for t in taxons]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def mark_notifications_read(request):
    """通知をグループ単位で既読にするAPI"""
    notification_type = request.POST.get('type')
    
    # 有効な通知タイプかチェック
    valid_types = ['OVERWEEK', 'D7', 'D14', 'D30']
    if notification_type not in valid_types:
        return JsonResponse({'error': 'Invalid notification type'}, status=400)
    
    # 該当ユーザーの指定タイプの未読通知を一括既読化
    updated_count = Notification.objects.filter(
        user=request.user,
        type=notification_type,
        read_at__isnull=True
    ).update(read_at=timezone.now())
    
    # 更新後の未読総数を取得
    unread_count = Notification.objects.filter(
        user=request.user,
        read_at__isnull=True
    ).count()
    
    return JsonResponse({
        'success': True,
        'updated_count': updated_count,
        'unread_total': unread_count
    })


@login_required
def get_notifications_summary(request):
    """通知サマリー取得API（ヘッダー表示用）"""
    user = request.user
    
    # タイプ別の未読通知数を取得
    notification_counts = {}
    for notification_type, title in [
        ('OVERWEEK', '使用期限を過ぎたアイテムがあります'),
        ('D7', '期限7日以内のアイテムがあります'),
        ('D14', '期限14日以内のアイテムがあります'),
        ('D30', '期限30日以内のアイテムがあります'),
    ]:
        count = Notification.objects.filter(
            user=user,
            type=notification_type,
            read_at__isnull=True
        ).count()
        
        notification_counts[notification_type] = {
            'count': count,
            'title': title,
            'has_unread': count > 0
        }
    
    # 総未読数
    total_unread = sum(item['count'] for item in notification_counts.values())
    
    return JsonResponse({
        'notifications': notification_counts,
        'total_unread': total_unread
    })


@login_required
def settings(request):
    """ユーザー設定ページ"""
    user = request.user
    
    # 現在の通知設定を取得（UserProfileがある場合）
    # 今回は簡易的にsessionで管理
    notifications_enabled = request.session.get('notifications_enabled', True)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            # プロフィール更新
            settings_form = UserSettingsForm(request.POST)
            password_form = PasswordChangeForm(user=user)
            
            if settings_form.is_valid():
                # ユーザーネーム更新
                new_username = settings_form.cleaned_data.get('username')
                if new_username and new_username != user.username:
                    user.username = new_username
                    user.save()
                
                # 通知設定更新
                notifications_enabled = settings_form.cleaned_data.get('notifications_enabled', False)
                request.session['notifications_enabled'] = notifications_enabled
                
                messages.success(request, 'プロフィール設定を更新しました。')
                return redirect('beauty:settings')
            else:
                messages.error(request, 'プロフィール更新に失敗しました。入力内容を確認してください。')
        
        elif action == 'change_password':
            # パスワード変更
            settings_form = UserSettingsForm(initial={
                'username': user.username,
                'notifications_enabled': notifications_enabled
            })
            password_form = PasswordChangeForm(user=user, data=request.POST)
            
            if password_form.is_valid():
                new_password = password_form.cleaned_data['new_password1']
                user.set_password(new_password)
                user.save()
                
                # セッション維持
                update_session_auth_hash(request, user)
                
                messages.success(request, 'パスワードを変更しました。')
                return redirect('beauty:settings')
            else:
                messages.error(request, 'パスワード変更に失敗しました。入力内容を確認してください。')
    
    else:
        # GET request
        settings_form = UserSettingsForm(initial={
            'username': user.username,
            'notifications_enabled': notifications_enabled
        })
        password_form = PasswordChangeForm(user=user)
    
    context = {
        'settings_form': settings_form,
        'password_form': password_form,
        'page_title': 'アカウント設定',
        'page_description': 'アカウント情報と設定を管理します'
    }
    
    return render(request, 'settings.html', context)

@login_required
@require_POST
def suggest_category_api(request):
    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
        name  = (data.get("name")  or "").strip()
        brand = (data.get("brand") or "").strip()
        item_text = " / ".join([s for s in [name, brand] if s])

        # 葉ノードだけを候補集合として LLM に渡す（パンくず付き）
        leafs = _leaf_taxa()
        taxon_payload = [{"id": t.id, "name": t.name, "path": _breadcrumb(t)} for t in leafs]

        # 事前フィルタで候補集合を絞る（ヒット時は効果絶大）
        taxon_payload_pref = prefilter_taxons(taxon_payload, item_text)

        #  デバッグ用出力
        print("=== DEBUG START ===")
        print("item_text:", item_text)
        print("payload size:", len(taxon_payload))
        print("prefiltered size:", len(taxon_payload_pref))
        print("example paths:", [p["path"] for p in taxon_payload_pref[:5]])
        print("=== DEBUG END ===")

        # LLMに「このリストからしか選ぶな」を渡す
        candidates = suggest_taxon_candidates(taxon_payload_pref, item_text, top_k=3)

        # 返ってきたIDの正当性チェック（保険）
        valid_ids = {p["id"] for p in taxon_payload_pref}
        candidates = [c for c in candidates if c.get("taxon_id") in valid_ids]

        # LLMが空だったらフォールバック
        if not candidates:
            candidates = naive_fallback(taxon_payload_pref, item_text, top_k=3)

        # 最小ログ（採用は保存時に True を別途記録）
        for c in candidates:
            LlmSuggestionLog.objects.create(
                user=request.user, item=None,
                target="product_type",
                suggested_taxon_id=c["taxon_id"],
                accepted=False
            )
        return JsonResponse({"candidates": candidates})

    except APITimeoutError:
        return JsonResponse({"error": "AI応答がタイムアウトしました。少し待って再試行してください。"}, status=504)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# --- 葉ノードだけを取得する関数（小カテゴリだけ抽出） ---
def _leaf_taxa():
    return (
        Taxon.objects
        .filter(children__isnull=True)
        .select_related("parent")
        .order_by("name")
    )

# --- パンくず（大 > 中 > 小）表記を作る補助 ---
def _breadcrumb(taxon):
    names = []
    cur = taxon
    while cur:
        names.append(cur.name)
        cur = cur.parent
    return " > ".join(reversed(names))

# --- アイテム登録ページ（GET表示） ---
@login_required
def item_create_view(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            return redirect("_form")  # 登録後のリダイレクト先
    else:
        form = ItemForm()

    # 葉ノードだけ抽出してパンくず形式に加工
    leafs = _leaf_taxa()
    taxon_leafs = [{"id": t.id, "breadcrumb": _breadcrumb(t)} for t in leafs]

    context = {
        "form": form,
        "taxon_leafs": taxon_leafs,  # ← テンプレで {{ taxon_leafs }} に利用
    }
    return render(request, "items/_form.html", context)

# ---- 事前フィルタ（テキストに応じて候補集合を狭める）----
def prefilter_taxons(payload, text):
    txt = (text or "").lower()
    rules = [
        (["マスカラ", "mascara"], ["マスカラ"]),
        (["化粧水", "トナー", "ローション"], ["化粧水"]),
        (["口紅", "リップスティック"], ["口紅", "リップ"]),
        (["クレンジング", "クレンズ"], ["クレンジング"]),
        (["ファンデ", "ファンデーション"], ["ファンデ"]),
    ]
    for keys, labels in rules:
        if any(k in txt for k in keys):
            return [p for p in payload if any(lbl in p["name"] or lbl in p["path"] for lbl in labels)]
    return payload  # ヒットなしなら全体

# ---- LLMが空を返した時の簡易フォールバック ----
def naive_fallback(payload, text, top_k=3):
    txt = (text or "").lower()
    def score(p):
        s = 0
        if any(k in txt for k in ["マスカラ","mascara"]):
            if "マスカラ" in p["name"] or "マスカラ" in p["path"]: s += 3
        if any(k in txt for k in ["化粧水","トナー","ローション"]):
            if "化粧水" in p["name"] or "化粧水" in p["path"]: s += 3
        # 追加の弱いヒット
        tokens = ["ファンデ","リップ","アイライナー","アイシャドウ","チーク","乳液","美容液","ジェル","バーム","オイル","石鹸","フォーム","クレンジング"]
        for tk in tokens:
            if tk in txt and (tk in p["name"] or tk in p["path"]):
                s += 1
        return s
    ranked = sorted(((score(p), p) for p in payload), key=lambda x: x[0], reverse=True)
    out = [{"taxon_id": p["id"], "path": p["path"], "confidence": min(0.9, sc/5.0)}
           for sc, p in ranked[:top_k] if sc > 0]
    return out

#棒グラフ
@login_required
def expiry_stats(request):
    today = date.today()
    d7  = today + timedelta(days=7)
    d14 = today + timedelta(days=14)
    d30 = today + timedelta(days=30)

    qs = Item.objects.filter(user=request.user)

    data = {
        "expired": qs.filter(expires_on__lt=today).count(),
        "week":    qs.filter(expires_on__gte=today,                     expires_on__lte=d7).count(),
        "biweek":  qs.filter(expires_on__gte=d7 + timedelta(days=1),    expires_on__lte=d14).count(),
        "month":   qs.filter(expires_on__gte=d14 + timedelta(days=1),   expires_on__lte=d30).count(),
        "safe":    qs.filter(expires_on__gt=d30).count(),
    }
    return JsonResponse(data)

#円グラフ
@login_required
def category_stats(request):
    qs = Item.objects.filter(user=request.user)

    #  外部キーは product_type（→ DB上は product_type_id）
    rows = (
        qs.values('product_type_id')
          .annotate(count=Count('id'))
          .order_by('product_type_id')
    )

    # 使われているIDをまとめて取得し、id→表示名のマップを作成
    ids = [r['product_type_id'] for r in rows if r['product_type_id'] is not None]
    name_map = {t.id: str(t) for t in Taxon.objects.filter(id__in=ids)}

    labels, counts = [], []
    for r in rows:
        pt_id = r['product_type_id']
        labels.append(name_map.get(pt_id, '未設定'))
        counts.append(r['count'])


    return JsonResponse({"labels": labels, "counts": counts})
