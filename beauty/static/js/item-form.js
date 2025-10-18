document.addEventListener('DOMContentLoaded', function () {
    const imageInput = document.getElementById('image');
    const previewDiv = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');

    if (imageInput) {
        imageInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewImg.src = e.target.result;
                    previewDiv.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                previewDiv.style.display = 'none';
            }
        });
    }

    // Date validation
    const openedOnInput = document.getElementById('opened_on');
    const expiresOnInput = document.getElementById('expires_on');

    function validateDates() {
        if (openedOnInput.value && expiresOnInput.value) {
            const openedDate = new Date(openedOnInput.value);
            const expiresDate = new Date(expiresOnInput.value);

            if (openedDate > expiresDate) {
                expiresOnInput.setCustomValidity('使用期限は開封日以降の日付を選択してください');
            } else {
                expiresOnInput.setCustomValidity('');
            }
        }
    }

    if (openedOnInput && expiresOnInput) {
        openedOnInput.addEventListener('change', validateDates);
        expiresOnInput.addEventListener('change', validateDates);
    }
});

// ==================== AIカテゴリ候補 ====================

// CSRFトークン取得（Django公式パターン）
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return decodeURIComponent(parts.pop().split(";").shift());
  return null;
}
const csrftoken = getCookie("csrftoken");

// DOM参照
const aiBox = document.getElementById("ai-suggest");
const btnSuggest = document.getElementById("btn-suggest");
const listSuggest = document.getElementById("suggest-list");
const apiUrl = aiBox ? aiBox.dataset.apiUrl : null;

// Django の ModelChoiceField が生成する select は通常 id="id_product_type"
const selProductType = document.getElementById("id_product_type");
const hiddenProductType = document.getElementById("product_type_id");

// XSS対策の簡易エスケープ
function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function fetchCandidates() {
  // 入力値を収集
  const nameEl  = document.getElementById("id_name");
  const brandEl = document.getElementById("id_brand");

  const payload = {
    name:  nameEl  ? nameEl.value  : "",
    brand: brandEl ? brandEl.value : "",
  };

  btnSuggest.disabled = true;
  const oldText = btnSuggest.innerHTML;
  btnSuggest.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>候補取得中...';

  try {
    const res = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken || ""
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const candidates = Array.isArray(data.candidates) ? data.candidates : [];

    if (!candidates.length) {
      listSuggest.innerHTML = `<li class="text-muted">候補が見つかりませんでした</li>`;
      return;
    }

    listSuggest.innerHTML = candidates.map(c => `
      <li class="d-flex align-items-center gap-2 mb-1">
        <span><strong>${escapeHtml(c.path || "")}</strong>
          <small class="text-muted">（信頼度: ${Math.round((c.confidence || 0)*100)}%）</small>
        </span>
        <button type="button" class="btn btn-sm btn-outline-success pick" data-id="${c.taxon_id}">
          採用
        </button>
      </li>
    `).join("");

  } catch (e) {
    console.error(e);
    listSuggest.innerHTML = `<li class="text-danger">候補取得に失敗しました。時間をおいて再試行してください。</li>`;
  } finally {
    btnSuggest.disabled = false;
    btnSuggest.innerHTML = oldText;
  }
}

function adoptCandidate(taxonId) {
  if (selProductType) selProductType.value = taxonId;     // 見えるセレクトに反映
  if (hiddenProductType) hiddenProductType.value = taxonId; // 念のため hidden にも反映

  // 採用済みのフィードバック
  const pickedBtn = listSuggest.querySelector(`.pick[data-id="${CSS.escape(String(taxonId))}"]`);
  if (pickedBtn) {
    pickedBtn.textContent = "採用済み";
    pickedBtn.disabled = true;
  }
}

// イベント設定
if (btnSuggest && apiUrl) {
  btnSuggest.addEventListener("click", fetchCandidates);

  listSuggest.addEventListener("click", (e) => {
    const btn = e.target.closest(".pick");
    if (!btn) return;
    adoptCandidate(btn.dataset.id);
  });
}
// ==================== /AIカテゴリ候補 ====================