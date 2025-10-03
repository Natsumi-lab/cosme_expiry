/*!
* コスメ期限管理アプリ - メインスクリプト
* 統計グラフと最近のアイテム表示機能を実装
*/

// サンプルデータ
const sampleData = {
    categories: {
        'ファンデーション': 12,
        'リップ': 8,
        'アイシャドウ': 15,
        'マスカラ': 6,
        'スキンケア': 20,
        'その他': 4
    },
    expiryStatus: {
        '期限切れ': 3,
        '期限間近(7日以内)': 5,
        '期限間近(30日以内)': 12,
        '安全': 45
    },
    recentItems: [
        {
            id: 1,
            name: 'NARS ナチュラルラディアント ロングウェア ファンデーション',
            category: 'ファンデーション',
            openedDate: '2024-09-15',
            expiryDate: '2025-09-15',
            daysLeft: 347,
            status: 'safe'
        },
        {
            id: 2,
            name: 'Dior アディクト リップスティック',
            category: 'リップ',
            openedDate: '2024-08-20',
            expiryDate: '2026-08-20',
            daysLeft: 687,
            status: 'safe'
        },
        {
            id: 3,
            name: 'Urban Decay Naked パレット',
            category: 'アイシャドウ',
            openedDate: '2024-07-10',
            expiryDate: '2026-07-10',
            daysLeft: 647,
            status: 'safe'
        },
        {
            id: 4,
            name: 'Maybelline ラッシュセンセーショナル マスカラ',
            category: 'マスカラ',
            openedDate: '2024-03-01',
            expiryDate: '2024-09-01',
            daysLeft: -32,
            status: 'expired'
        },
        {
            id: 5,
            name: 'SK-II フェイシャル トリートメント エッセンス',
            category: 'スキンケア',
            openedDate: '2024-09-01',
            expiryDate: '2025-03-01',
            daysLeft: 148,
            status: 'safe'
        },
        {
            id: 6,
            name: 'シャネル ルージュ ココ',
            category: 'リップ',
            openedDate: '2024-05-15',
            expiryDate: '2025-11-15',
            daysLeft: 408,
            status: 'safe'
        }
    ]
};

// Chart.jsのデフォルト設定
Chart.defaults.font.family = "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif";
Chart.defaults.color = '#6c757d';

// カテゴリ別統計グラフを初期化
function initCategoryChart() {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;

    const labels = Object.keys(sampleData.categories);
    const data = Object.values(sampleData.categories);
    
    // カラーパレット（メインカラーを使用）
    const colors = [
        '#d3859c',
        '#bdafb5',
        '#D8D4D5',
        '#a08d94',
        '#c4a4b1',
        '#e8d4d9'
    ];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderColor: '#ffffff',
                borderWidth: 3,
                hoverBorderWidth: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12,
                            weight: '500'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#d3859c',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed * 100) / total).toFixed(1);
                            return `${context.label}: ${context.parsed}個 (${percentage}%)`;
                        }
                    }
                }
            },
            interaction: {
                intersect: false
            },
            animation: {
                animateRotate: true,
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// 期限別統計グラフを初期化
function initExpiryChart() {
    const ctx = document.getElementById('expiryChart');
    if (!ctx) return;

    const labels = Object.keys(sampleData.expiryStatus);
    const data = Object.values(sampleData.expiryStatus);
    
    // ステータス別カラーパレット
    const colors = [
        '#dc3545', // 期限切れ（赤）
        '#ffc107', // 期限間近7日以内（黄）
        '#fd7e14', // 期限間近30日以内（オレンジ）
        '#198754'  // 安全（緑）
    ];

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'アイテム数',
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(color => color),
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#d3859c',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.y}個のアイテム`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 5,
                        color: '#6c757d',
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(108, 117, 125, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#6c757d',
                        font: {
                            size: 11,
                            weight: '500'
                        },
                        maxRotation: 45
                    },
                    grid: {
                        display: false
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// 期限ステータスを判定
function getExpiryStatus(daysLeft) {
    if (daysLeft < 0) return 'expired';
    if (daysLeft <= 7) return 'warning';
    return 'safe';
}

// 期限ステータスのテキストを取得
function getStatusText(status) {
    switch (status) {
        case 'expired': return '期限切れ';
        case 'warning': return '期限間近';
        case 'safe': return '使用可能';
        default: return '不明';
    }
}

// 日付フォーマット
function formatDate(dateString) {
    const date = new Date(dateString);
    return `${date.getFullYear()}/${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getDate().toString().padStart(2, '0')}`;
}

// 最近のアイテムを表示
function displayRecentItems() {
    const container = document.getElementById('recentItemsContainer');
    if (!container) return;

    // 最新の4つのアイテムを表示
    const recentItems = sampleData.recentItems.slice(0, 4);
    
    container.innerHTML = recentItems.map(item => `
        <div class="col-md-6 col-lg-3 mb-4">
            <div class="card item-card h-100">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <span class="item-category">${item.category}</span>
                        <span class="expiry-status ${item.status}">
                            ${getStatusText(item.status)}
                        </span>
                    </div>
                    <h6 class="card-title">${item.name}</h6>
                    <div class="mt-3">
                        <small class="text-muted d-block">
                            <i class="fas fa-calendar-alt me-1"></i>
                            開封日: ${formatDate(item.openedDate)}
                        </small>
                        <small class="text-muted d-block">
                            <i class="fas fa-clock me-1"></i>
                            ${item.daysLeft >= 0 ? `あと${item.daysLeft}日` : `${Math.abs(item.daysLeft)}日経過`}
                        </small>
                    </div>
                </div>
                <div class="card-footer bg-transparent border-0">
                    <div class="d-flex gap-1">
                        <button class="btn btn-outline-primary btn-sm flex-fill">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-secondary btn-sm flex-fill">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-sm flex-fill">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');

    // カードにアニメーションを追加
    const cards = container.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in-up');
        }, index * 100);
    });
}

// 通知バッジを更新
function updateNotificationBadge() {
    const badge = document.getElementById('notificationBadge');
    if (!badge) return;

    // 期限切れや期限間近のアイテム数を計算
    const urgentItems = sampleData.recentItems.filter(item => 
        item.status === 'expired' || item.status === 'warning'
    ).length;

    if (urgentItems > 0) {
        badge.textContent = urgentItems;
        badge.style.display = 'flex';
    } else {
        badge.style.display = 'none';
    }
}

// スムーススクロール
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ツールチップの初期化
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// メイン初期化関数
function initApp() {
    // Chart.jsが読み込まれるまで待機
    if (typeof Chart !== 'undefined') {
        initCategoryChart();
        initExpiryChart();
    } else {
        setTimeout(initApp, 100);
        return;
    }
    
    displayRecentItems();
    updateNotificationBadge();
    initSmoothScrolling();
    initTooltips();
    
    console.log('コスメ期限管理アプリが初期化されました');
}

// DOM読み込み完了後に初期化
document.addEventListener('DOMContentLoaded', initApp);

// ウィンドウリサイズ時の処理
window.addEventListener('resize', function() {
    // レスポンシブ対応のための処理
    const categoryChart = Chart.getChart('categoryChart');
    const expiryChart = Chart.getChart('expiryChart');
    
    if (categoryChart) {
        categoryChart.resize();
    }
    if (expiryChart) {
        expiryChart.resize();
    }
});

// サービスワーカーの登録（PWA化の準備）
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}