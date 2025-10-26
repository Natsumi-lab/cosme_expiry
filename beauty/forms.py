from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Item, Taxon
import re


class SignUpForm(UserCreationForm):
    """ユーザー登録フォーム"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ユーザーネーム',
            'id': 'username'
        }),
        label='ユーザーネーム',
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'メールアドレス',
            'id': 'email'
        }),
        label='メールアドレス',
        help_text='ログイン時に使用するメールアドレスを入力してください。'
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'パスワード',
            'id': 'password1'
        }),
        label='パスワード',
        help_text='8文字以上で、英数字を含む強固なパスワードを設定してください。'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'パスワード（確認用）',
            'id': 'password2'
        }),
        label='パスワード（確認用）',
        help_text='確認のため、同じパスワードを再度入力してください。'
    )
    
    terms_accepted = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'terms-checkbox'
        }),
        label='利用規約とプライバシーポリシーに同意する',
        required=True,
        error_messages={'required': '利用規約への同意が必要です。'}
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        """メールアドレスの重複チェック"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('このメールアドレスは既に登録されています。')
        return email
    
    def clean_password1(self):
        """パスワード強度チェック"""
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise ValidationError('パスワードは8文字以上である必要があります。')
        
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError('パスワードには英字を含める必要があります。')
        
        if not re.search(r'\d', password):
            raise ValidationError('パスワードには数字を含める必要があります。')
        
        return password
    
    def save(self, commit=True):
        """ユーザー保存時にメールアドレスを設定"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
        return user


class SignInForm(forms.Form):
    """ログインフォーム（カスタム）"""
    
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'メールアドレス',
            'id': 'email',
            'autocomplete': 'email'
        }),
        label='メールアドレス',
        help_text='登録時に使用したメールアドレスを入力してください。'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'パスワード',
            'id': 'password',
            'autocomplete': 'current-password'
        }),
        label='パスワード',
        help_text='アカウント作成時に設定したパスワードを入力してください。'
    )
    
    def clean_username(self):
        """メールアドレス形式の検証"""
        username = self.cleaned_data.get('username')
        if username:
            # メールアドレス形式の簡易チェック
            if '@' not in username or '.' not in username:
                raise ValidationError('有効なメールアドレスを入力してください。')
        return username


class ItemForm(forms.ModelForm):
    """アイテム登録フォーム"""
    
    product_type = forms.ModelChoiceField(
        queryset=Taxon.objects.filter(children__isnull=True),  # 葉ノードのみ
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_product_type'
        }),
        label='商品カテゴリ',
        help_text='最も詳細なカテゴリを選択してください',
        empty_label='カテゴリを選択してください'
    )
    
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '商品名を入力してください',
            'id': 'name'
        }),
        label='商品名'
    )
    
    brand = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ブランド名を入力してください',
            'id': 'brand'
        }),
        label='ブランド名'
    )
    
    color_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '色番やカラー名を入力してください',
            'id': 'color_code'
        }),
        label='色番/カラー'
    )
    
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'id': 'image',
            'accept': 'image/*'
        }),
        label='商品画像',
        help_text='JPEG, PNG形式の画像をアップロードできます'
    )
    
    opened_on = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'id_opened_on'
        }),
        label='開封日'
    )
    
    expires_on = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'id_expires_on'
        }),
        label='使用期限'
    )
    
    memo = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'メモがあれば入力してください',
            'id': 'memo',
            'rows': 4
        }),
        label='メモ'
    )
    
    class Meta:
        model = Item
        fields = ['image', 'product_type', 'name', 'brand', 'color_code', 'opened_on', 'expires_on', 'memo']

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # カテゴリの選択肢を階層的に表示
        leaf_taxons = Taxon.objects.filter(children__isnull=True).select_related('parent')
        choices = [('', 'カテゴリを選択してください')]
        
        for taxon in leaf_taxons:
            display_name = taxon.full_path or taxon.name
            choices.append((taxon.pk, display_name))
        
        self.fields['product_type'].choices = choices
    
    def clean(self):
        """フォーム全体のバリデーション"""
        cleaned_data = super().clean()
        opened_on = cleaned_data.get('opened_on')
        expires_on = cleaned_data.get('expires_on')
        
        if opened_on and expires_on:
            if opened_on > expires_on:
                raise ValidationError('使用期限は開封日以降の日付を設定してください。')
        
        return cleaned_data


class UserSettingsForm(forms.Form):
    """ユーザー設定フォーム"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ユーザーネーム（表示用）',
            'id': 'username'
        }),
        label='ユーザーネーム',
        help_text='変更後のユーザーネームを入力してください。',
        required=False
    )
    
    notifications_enabled = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'notifications_enabled',
            'role': 'switch'
        }),
        label='通知を受け取る',
        required=False
    )
    

class PasswordChangeForm(forms.Form):
    """パスワード変更フォーム"""
    
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '現在のパスワード',
            'id': 'current_password',
            'autocomplete': 'current-password'
        }),
        label='現在のパスワード'
    )
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '新しいパスワード',
            'id': 'new_password1',
            'autocomplete': 'new-password'
        }),
        label='新しいパスワード',
        help_text='8文字以上で、英数字を含む強固なパスワードを設定してください。'
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '新しいパスワード（確認用）',
            'id': 'new_password2',
            'autocomplete': 'new-password'
        }),
        label='新しいパスワード（確認用）',
        help_text='確認のため、同じパスワードを再度入力してください。'
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        """現在のパスワードの確認"""
        current_password = self.cleaned_data.get('current_password')
        if current_password and not self.user.check_password(current_password):
            raise ValidationError('現在のパスワードが正しくありません。')
        return current_password
    
    def clean_new_password1(self):
        """新しいパスワードの強度チェック"""
        password = self.cleaned_data.get('new_password1')
        
        if len(password) < 8:
            raise ValidationError('パスワードは8文字以上である必要があります。')
        
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError('パスワードには英字を含める必要があります。')
        
        if not re.search(r'\d', password):
            raise ValidationError('パスワードには数字を含める必要があります。')
        
        return password
    
    def clean(self):
        """パスワード確認のマッチング"""
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError('新しいパスワードが一致しません。')
        
        return cleaned_data