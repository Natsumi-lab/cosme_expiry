document.addEventListener("DOMContentLoaded", function () {
  const imageInput = document.getElementById("image");
  const previewDiv = document.getElementById("image-preview");
  const previewImg = document.getElementById("preview-img");

  if (imageInput) {
    imageInput.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          previewImg.src = e.target.result;
          previewDiv.style.display = "block";
        };
        reader.readAsDataURL(file);
      } else {
        previewDiv.style.display = "none";
      }
    });
  }

  // Date validation
  const openedOnInput = document.getElementById("opened_on");
  const expiresOnInput = document.getElementById("expires_on");

  function validateDates() {
    if (openedOnInput.value && expiresOnInput.value) {
      const openedDate = new Date(openedOnInput.value);
      const expiresDate = new Date(expiresOnInput.value);

      if (openedDate > expiresDate) {
        expiresOnInput.setCustomValidity(
          "使用期限は開封日以降の日付を選択してください"
        );
      } else {
        expiresOnInput.setCustomValidity("");
      }
    }
  }

  if (openedOnInput && expiresOnInput) {
    openedOnInput.addEventListener("change", validateDates);
    expiresOnInput.addEventListener("change", validateDates);
  }
});

// ==================== AIカテゴリ候補 ====================

// CSRFトークン取得（Django公式パターン）
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2)
    return decodeURIComponent(parts.pop().split(";").shift());
  return null;
}
const csrftoken = getCookie("csrftoken");

// DOM参照
const aiBox = document.getElementById("ai-suggest");
const btnSuggest = document.getElementById("btn-suggest");
const listSuggest = document.getElementById("suggest-list");
const apiUrl = aiBox ? aiBox.dataset.apiUrl : null;

// Django の ModelChoiceField が生成する select は通常 id="id_product_type"
const selProductType =
  document.getElementById("id_product_type") ||
  document.getElementById("product_type") ||
  document.querySelector('select[name="product_type"]');

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
  // ▼ name属性ベースで安全に取得
  const formEl = document.getElementById("item-form");
  const getVal = (n) =>
    formEl?.querySelector(`[name="${n}"]`)?.value?.trim() || "";

  const payload = {
    name: getVal("name"), // ← 商品名
    brand: getVal("brand"), // ← ブランド名
  };

  // 連打防止＆スピナー
  btnSuggest.disabled = true;
  const oldText = btnSuggest.innerHTML;
  btnSuggest.innerHTML =
    '<span class="spinner-border spinner-border-sm me-1"></span>候補取得中...';

  try {
    const res = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken || "",
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const candidates = Array.isArray(data.candidates) ? data.candidates : [];

    if (!candidates.length) {
      listSuggest.innerHTML = `<li class="text-muted">候補が見つかりませんでした</li>`;
      return;
    }

    listSuggest.innerHTML = candidates
      .map(
        (c) => `
      <li class="d-flex align-items-center gap-2 mb-1">
        <span><strong>${escapeHtml(c.path || "")}</strong></span>
        <button type="button" class="btn btn-sm btn-outline-success pick ms-3" data-id="${
          c.taxon_id
        }">
          決定
        </button>
      </li>
    `
      )
      .join("");
  } catch (e) {
    console.error(e);
    listSuggest.innerHTML = `<li class="text-danger">候補取得に失敗しました。時間をおいて再試行してください。</li>`;
  } finally {
    btnSuggest.disabled = false;
    btnSuggest.innerHTML = oldText;
  }
}

function adoptCandidate(taxonId) {
  if (!selProductType) return;

  // 1. 文字列化して確実に一致させる
  const val = String(taxonId);

  // 2. 対応する<option>を探す
  const options = Array.from(selProductType.options);
  const opt = options.find((o) => String(o.value) === val);

  if (opt) {
    // 3. セレクト状態を強制的に更新
    opt.selected = true;
    selProductType.value = val;
    selProductType.selectedIndex = options.indexOf(opt);

    // 4. イベント発火（Bootstrapは見た目が自動で更新される）
    selProductType.dispatchEvent(new Event("input", { bubbles: true }));
    selProductType.dispatchEvent(new Event("change", { bubbles: true }));

    // 5. hiddenフィールドも同期（フォーム送信用）
    if (hiddenProductType) hiddenProductType.value = val;

    // 6. 決定ボタンUI更新
    const btn = [...listSuggest.querySelectorAll(".pick")].find(
      (b) => b.dataset.id === val
    );
    if (btn) {
      btn.textContent = "決定済み";
      btn.disabled = true;
    }

    // 7. 見やすくするためスクロール
    selProductType.scrollIntoView({ behavior: "smooth", block: "center" });
  } else {
    console.warn("[adoptCandidate] 該当する<option>が見つかりません:", val);
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
