/**
 * 通知機能のJavaScript
 * - 未読通知バッジの更新
 * - アコーディオン見出しクリック時の既読処理
 * - ページ遷移処理
 */

document.addEventListener('DOMContentLoaded', function() {
    // 通知サマリーを取得してバッジを更新
    loadNotificationSummary();
    
    // 通知ヘッダーのクリックイベントを設定
    setupNotificationHandlers();
});

/**
 * 通知サマリーを取得してバッジを更新
 */
function loadNotificationSummary() {
    fetch('/api/notifications/summary/')
        .then(response => response.json())
        .then(data => {
            updateNotificationBadge(data.total_unread);
        })
        .catch(error => {
            console.error('通知サマリー取得エラー:', error);
        });
}

/**
 * 通知バッジを更新
 * @param {number} totalUnread - 未読総数
 */
function updateNotificationBadge(totalUnread) {
    const badge = document.getElementById('notificationBadge');
    if (!badge) return;
    
    if (totalUnread > 0) {
        badge.textContent = totalUnread;
        badge.classList.remove('d-none');
    } else {
        badge.classList.add('d-none');
    }
}

/**
 * 通知ヘッダーのクリックイベントを設定
 */
function setupNotificationHandlers() {
    const notificationHeaders = document.querySelectorAll('.notification-header');
    
    notificationHeaders.forEach(header => {
        header.addEventListener('click', function(e) {
            e.preventDefault();
            
            const notificationType = this.dataset.notificationType;
            const filterUrl = this.dataset.filterUrl;
            
            // 既読化処理
            markNotificationsRead(notificationType)
                .then(() => {
                    // 成功時はページ遷移
                    window.location.href = filterUrl;
                })
                .catch(error => {
                    console.error('既読化エラー:', error);
                    // エラー時でもページ遷移
                    window.location.href = filterUrl;
                });
        });
    });
}

/**
 * 指定タイプの通知を既読にする
 * @param {string} notificationType - 通知タイプ
 * @returns {Promise}
 */
function markNotificationsRead(notificationType) {
    const formData = new FormData();
    formData.append('type', notificationType);
    
    // CSRFトークンを取得
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                     document.querySelector('meta[name="csrf-token"]')?.content;
    
    if (csrfToken) {
        formData.append('csrfmiddlewaretoken', csrfToken);
    }
    
    return fetch('/api/notifications/mark-read/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // バッジを更新
            updateNotificationBadge(data.unread_total);
            return data;
        } else {
            throw new Error('既読化に失敗しました');
        }
    });
}