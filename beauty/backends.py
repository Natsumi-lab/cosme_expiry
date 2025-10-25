from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    """メールアドレスで認証するバックエンド"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get("email") or username
        if not email or not password:
            return None

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            # 存在しない時も同程度の処理コストにしてタイミング攻撃を避ける
            dummy = User()
            dummy.set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
