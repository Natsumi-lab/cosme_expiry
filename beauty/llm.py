# beauty/llm.py
import os, json
from typing import List, Dict, Any
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
あなたはコスメ商品のカテゴリ分類器です。
入力:
- item_text: 商品名やブランド名などの短いテキスト
- taxons: 候補Taxonのリスト（各要素に id, name, path を含む）。このリストは小カテゴリ（葉）のみ。
厳守:
- **必ず taxons の中から**最も適切な小カテゴリを上位3件まで選ぶこと。
- 適切な候補が無ければ空配列[]を返す（無理に推測しない）。
- 出力は JSON オブジェクト1つのみ:
{"candidates":[{"taxon_id":123,"path":"メイク用品 > マスカラ","confidence":0.9}]}
- 余計な文章は出力しないこと。

同義語の例:
- 化粧水 = ローション, トナー, toner, lotion
- マスカラ = mascara
- 口紅 = リップスティック, lipstick
- クレンジングオイル = cleansing oil

"""

def suggest_taxon_candidates(taxon_payload: List[Dict[str, Any]], item_text: str, top_k: int = 3):
    payload = {
        "item_text": item_text,
        "taxons": taxon_payload,
        "top_k": top_k
    }

    resp = client.chat.completions.create(
        model="gpt-5-nano",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
        ],
        timeout=25
    )

    # JSON取り出し（失敗時は空配列）
    text = resp.choices[0].message.content or "{}"
    try:
        data = json.loads(text)
    except Exception:
        data = {"candidates": []}

    out = []
    for c in data.get("candidates", [])[:top_k]:
        try:
            out.append({
                "taxon_id": int(c["taxon_id"]),
                "path": str(c.get("path", "")),
                "confidence": float(c.get("confidence", 0.5))
            })
        except Exception:
            continue
    return out