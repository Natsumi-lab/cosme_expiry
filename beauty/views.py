from django.shortcuts import render


def home(request):
    """
    ホームページビュー
    統計データとサンプルアイテムを表示
    """
    return render(request, 'home.html')