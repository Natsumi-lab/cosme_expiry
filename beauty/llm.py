# beauty/llm.py
import os, json
from typing import List, Dict, Any
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """あなたはコスメのカテゴリ分類器です。
与えられたTaxonツリー（id, name, parent_id）と商品テキストから、
最も適切な「葉ノード（小分類）」候補を上位3件まで返してください。
出力は必ず次のJSONのみ：
{
  "candidates": [
    {"taxon_id": 123, "path": "メイク用品 > ファンデーション > パウダーファンデ", "confidence": 0.85}
  ]
}
余計な文章は出力しないこと。"""

def _pack_taxons(taxons_qs) -> List[Dict[str, Any]]:
    # LLMに渡す最小情報（軽量化のためカラム限定で呼び出してください）
    return [{"id": t.id, "name": t.name, "parent": t.parent_id} for t in taxons_qs]

def suggest_taxon_candidates(taxons_qs, item_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
    payload = {"taxons": _pack_taxons(taxons_qs), "item_text": item_text, "top_k": top_k}

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",   
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
        ],
        timeout=15
    )
    text = resp.choices[0].message.content or "{}"
    try:
        data = json.loads(text)
    except Exception:
        # 先頭/末尾の余計な文字を落として再挑戦（簡易）
        left = text.find("{"); right = text.rfind("}")
        data = json.loads(text[left:right+1]) if left >= 0 and right >= 0 else {"candidates":[]}

    out = []
    for c in data.get("candidates", [])[:top_k]:
        try:
            out.append({
                "taxon_id": int(c["taxon_id"]),
                "path": str(c["path"]),
                "confidence": max(0.0, min(1.0, float(c.get("confidence", 0.5))))
            })
        except Exception:
            continue
    return out
