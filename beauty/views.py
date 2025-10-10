from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, FormView, View
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from .forms import SignUpForm, SignInForm
from .models import Taxon, LlmSuggestionLog


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

# views.py または services.py

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