from django.shortcuts import render


def home(request):
    """
    ホームページビュー
    統計データとサンプルアイテムを表示
    """
    return render(request, 'home.html')

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