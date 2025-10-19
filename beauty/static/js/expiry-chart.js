/*!
 * 期限別アイテム数グラフ - JavaScript
 * 期限区分ごとのアイテム数を表示する棒グラフを実装
 */

document.addEventListener('DOMContentLoaded', function() {
    // Chart.jsとプラグインが読み込まれるまで待機
    if (typeof Chart !== 'undefined' && typeof ChartDataLabels !== 'undefined') {
        initExpiryChart();
    } else {
        // Chart.jsがまだ読み込まれていない場合は遅延実行
        const checkChartInterval = setInterval(function() {
            if (typeof Chart !== 'undefined' && typeof ChartDataLabels !== 'undefined') {
                clearInterval(checkChartInterval);
                initExpiryChart();
            }
        }, 100);
    }
});
document.addEventListener('DOMContentLoaded', initExpiryChart);

// 期限別統計グラフを初期化
function initExpiryChart() {
    const ctx = document.getElementById('expiryChart');
    if (!ctx) return;

    // APIからデータを取得
    fetchExpiryStats()
        .then(data => {
            renderExpiryChart(ctx, data);
        })
        .catch(error => {
            console.error('期限統計データの取得に失敗:', error);
            
            // エラー時はチャートにエラーメッセージを表示
            const errorMsg = document.createElement('div');
            errorMsg.className = 'text-center text-danger my-3';
            errorMsg.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>データの読み込みに失敗しました。';
            
            ctx.parentNode.insertBefore(errorMsg, ctx.nextSibling);
            
            // 空のチャートを表示（エラー状態を視覚化）
            renderExpiryChart(ctx, {
                expired: 0,
                week: 0,
                biweek: 0,
                month: 0,
                safe: 0
            });
        });
}

// APIから期限統計データを取得
async function fetchExpiryStats() {
    try {
        const response = await fetch('/api/expiry-stats/');
        if (!response.ok) {
            throw new Error(`APIエラー: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('期限統計APIのfetchに失敗:', error);
        throw error;
    }
}

// チャートをレンダリング
function renderExpiryChart(ctx, data) {
    // データとラベルを準備
    const chartData = [
        data.expired,  // 期限切れ
        data.week,     // 7日以内
        data.biweek,   // 14日以内
        data.month,    // 30日以内
        data.safe      // 余裕あり
    ];
    
    // 日本語ラベル
    const labels = [
        '期限切れ',
        '7日以内',
        '14日以内',
        '30日以内', 
        '余裕あり'
    ];
    
    // ステータス別カラーパレット（既存のscripts.jsから流用）
    const colors = [
        '#B91C1C', // 期限切れ（濃い赤・最も暗い）
        '#FDE047', // 期限7日以内（明るい黄色・最も明るい）
        '#FB923C', // 期限14日以内（鮮やかなオレンジ・中間の明るさ）
        '#22C55E', // 期限30日以内（鮮やかな緑・明るめ）
        '#0dcaf0'  // 余裕あり（鮮やかな青・明るめ）
    ];

    // 既存のチャートがあれば破棄
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }

    // 新しいチャートを作成
    new Chart(ctx, {
        type: 'bar',
        plugins: [ChartDataLabels], 
        data: {
            labels: labels,
            datasets: [{
                label: 'アイテム数',
                data: chartData,
                backgroundColor: colors,
                borderColor: colors,
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
                },
                // バーの上に数値を表示
                datalabels: {
                    color: '#333',
                    anchor: 'end',
                    align: 'top',
                    formatter: function(value) {
                        return value > 0 ? value : '';
                    },
                    font: {
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grace: '10%',
                    ticks: {
                        stepSize: 1,
                        precision: 0, // 整数値のみ表示
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

// ウィンドウリサイズ時の処理
window.addEventListener('resize', function() {
    // レスポンシブ対応のためにチャートをリサイズ
    const expiryChart = Chart.getChart('expiryChart');
    if (expiryChart) {
        expiryChart.resize();
    }
});