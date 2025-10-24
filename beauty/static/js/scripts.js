/*!
 * コスメ期限管理アプリ - メインスクリプト
 * 統計グラフと最近のアイテム表示機能を実装
 */

// サンプルデータ
const sampleData = {
  categories: {
    ファンデーション: 12,
    リップ: 8,
    アイシャドウ: 15,
    マスカラ: 6,
    スキンケア: 20,
    その他: 4,
  },
  expiryStatus: {
    期限切れ: 3,
    期限7日以内: 5,
    期限14日以内: 8,
    期限30日以内: 12,
    余裕あり: 45,
  },
  recentItems: [
    {
      id: 1,
      name: "NARS ナチュラルラディアント ロングウェア ファンデーション",
      category: "ファンデーション",
      openedDate: "2024-09-15",
      expiryDate: "2025-09-15",
      daysLeft: 347,
      status: "safe",
    },
    {
      id: 2,
      name: "Dior アディクト リップスティック",
      category: "リップ",
      openedDate: "2024-08-20",
      expiryDate: "2026-08-20",
      daysLeft: 687,
      status: "safe",
    },
    {
      id: 3,
      name: "Urban Decay Naked パレット",
      category: "アイシャドウ",
      openedDate: "2024-07-10",
      expiryDate: "2026-07-10",
      daysLeft: 647,
      status: "safe",
    },
    {
      id: 4,
      name: "Maybelline ラッシュセンセーショナル マスカラ",
      category: "マスカラ",
      openedDate: "2024-03-01",
      expiryDate: "2024-09-01",
      daysLeft: -32,
      status: "expired",
    },
    {
      id: 5,
      name: "SK-II フェイシャル トリートメント エッセンス",
      category: "スキンケア",
      openedDate: "2024-09-01",
      expiryDate: "2025-03-01",
      daysLeft: 148,
      status: "safe",
    },
    {
      id: 6,
      name: "シャネル ルージュ ココ",
      category: "リップ",
      openedDate: "2024-05-15",
      expiryDate: "2025-11-15",
      daysLeft: 408,
      status: "safe",
    },
  ],
};

// Chart.jsのデフォルト設定
Chart.defaults.font.family =
  "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif";
Chart.defaults.color = "#6c757d";

// カテゴリ別統計グラフを初期化
function initCategoryChart() {
  const el = document.getElementById("categoryChart");
  if (!el) return;

  if (initCategoryChart._loading) return;
  initCategoryChart._loading = true;

  const existing = Chart.getChart(el);
  if (existing) existing.destroy();

  fetch("/api/category-stats/", { credentials: "same-origin" })
    .then((r) => (r.ok ? r.json() : Promise.reject(r)))
    .then((json) => {
      const labels = json.labels || [];
      const data = json.counts || [];

      const palette = [
        "#d3859c",
        "#bdafb5",
        "#D8D4D5",
        "#a08d94",
        "#c4a4b1",
        "#e8d4d9",
      ];
      const colors = labels.map((_, i) => palette[i % palette.length]);

      const ex = Chart.getChart(el);
      if (ex) ex.destroy();

      new Chart(el.getContext("2d"), {
        type: "doughnut",
        data: {
          labels,
          datasets: [
            {
              data,
              backgroundColor: colors,
              borderColor: "#fff",
              borderWidth: 3,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "55%",
          plugins: {
            legend: {
              position: "bottom",
              labels: { usePointStyle: true, padding: 20 },
            },
            tooltip: {
              callbacks: {
                label: (ctx) => {
                  const total =
                    ctx.dataset.data.reduce((a, b) => a + b, 0) || 1;
                  const val = ctx.parsed || 0;
                  const pct = ((val * 100) / total).toFixed(1);
                  return `${ctx.label}: ${val}個 (${pct}%)`;
                },
              },
            },
          },
        },
      });
    })
    .catch((err) => {
      console.error("category-stats fetch error:", err);
      // フェイルセーフ（読み込み失敗表示）
      const ex = Chart.getChart(el);
      if (ex) ex.destroy();
      new Chart(el.getContext("2d"), {
        type: "doughnut",
        data: {
          labels: ["読み込み失敗"],
          datasets: [
            {
              data: [1],
              backgroundColor: ["#eee"],
              borderColor: "#fff",
              borderWidth: 3,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: "bottom" } },
        },
      });
    })
    .finally(() => {
      initCategoryChart._loading = false;
    });
}

document.addEventListener("DOMContentLoaded", initApp);

// 期限別統計グラフを初期化
function initExpiryChart() {
  const ctx = document.getElementById("expiryChart");
  if (!ctx) return;

  const labels = Object.keys(sampleData.expiryStatus);
  const data = Object.values(sampleData.expiryStatus);

  // ステータス別カラーパレット
  const colors = [
    "#B91C1C", // 期限切れ（濃い赤・最も暗い）
    "#FDE047", // 期限7日以内（明るい黄色・最も明るい）
    "#FB923C", // 期限14日以内（鮮やかなオレンジ・中間の明るさ）
    "#22C55E", // 期限30日以内（鮮やかな緑・明るめ）
    "#0dcaf0", //余裕あり（鮮やかな青・明るめ）
  ];

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "アイテム数",
          data: data,
          backgroundColor: colors,
          borderColor: colors.map((color) => color),
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: "rgba(0, 0, 0, 0.8)",
          titleColor: "#ffffff",
          bodyColor: "#ffffff",
          borderColor: "#d3859c",
          borderWidth: 1,
          callbacks: {
            label: function (context) {
              return `${context.parsed.y}個のアイテム`;
            },
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 5,
            color: "#6c757d",
            font: {
              size: 12,
            },
          },
          grid: {
            color: "rgba(108, 117, 125, 0.1)",
          },
        },
        x: {
          ticks: {
            color: "#6c757d",
            font: {
              size: 11,
              weight: "500",
            },
            maxRotation: 45,
          },
          grid: {
            display: false,
          },
        },
      },
      animation: {
        duration: 1000,
        easing: "easeInOutQuart",
      },
    },
  });
}

// 期限ステータスを判定
function getExpiryStatus(daysLeft) {
  if (daysLeft < 0) return "expired";
  if (daysLeft <= 7) return "warning";
  return "safe";
}

// 期限ステータスのテキストを取得
function getStatusText(status) {
  switch (status) {
    case "expired":
      return "期限切れ";
    case "warning":
      return "期限間近";
    case "safe":
      return "使用可能";
    default:
      return "不明";
  }
}

// 日付フォーマット
function formatDate(dateString) {
  const date = new Date(dateString);
  return `${date.getFullYear()}/${(date.getMonth() + 1)
    .toString()
    .padStart(2, "0")}/${date.getDate().toString().padStart(2, "0")}`;
}

// 最近のアイテムを表示
function displayRecentItems() {
  // サーバーからデータが渡されるようになったため、この関数は使用しない
  // 実データは Djangoテンプレートから直接描画されます
  const container = document.getElementById("recentItemsContainer");
  if (!container) return;

  // カードにアニメーションを追加するのみ
  const cards = container.querySelectorAll(".card");
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.classList.add("fade-in-up");
    }, index * 100);
  });
}

// 通知バッジを更新
function updateNotificationBadge() {
  const badge = document.getElementById("notificationBadge");
  if (!badge) return;

  // 期限切れや期限間近のアイテム数を計算
  const urgentItems = sampleData.recentItems.filter(
    (item) => item.status === "expired" || item.status === "warning"
  ).length;

  if (urgentItems > 0) {
    badge.textContent = urgentItems;
    badge.style.display = "flex";
  } else {
    badge.style.display = "none";
  }
}

// スムーススクロール
function initSmoothScrolling() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const href = this.getAttribute("href");

      // href="#" や href="" はスキップして何もしない
      if (!href || href === "#") return;

      e.preventDefault();
      const target = document.querySelector("href");
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });
}

// ツールチップの初期化
function initTooltips() {
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

// メイン初期化関数
function initApp() {
  // Chart.jsが読み込まれるまで待機
  if (typeof Chart !== "undefined") {
    initCategoryChart();
    initExpiryChart();
  } else {
    setTimeout(initApp, 100);
    return;
  }

  // 最近のアイテムのアニメーションを追加
  displayRecentItems();
  updateNotificationBadge();
  initSmoothScrolling();
  initTooltips();

  console.log("コスメ期限管理アプリが初期化されました");
}

// DOM読み込み完了後に初期化
document.addEventListener("DOMContentLoaded", initApp);

// ウィンドウリサイズ時の処理
window.addEventListener("resize", function () {
  // レスポンシブ対応のための処理
  const categoryChart = Chart.getChart("categoryChart");
  const expiryChart = Chart.getChart("expiryChart");

  if (categoryChart) {
    categoryChart.resize();
  }
  if (expiryChart) {
    expiryChart.resize();
  }
});
