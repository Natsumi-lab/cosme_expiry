from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


class SignUpForm(UserCreationForm):
    """ユーザー登録フォーム"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ユーザーネーム（表示用）',
            'id': 'username'
        }),
        label='ユーザーネーム',
        help_text='表示専用です。認証には使用されません。'
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