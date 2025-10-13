/*!
 * アイテム一覧ページ - JavaScript
 * フィルタ機能、タブ切替、AJAX処理を実装
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM要素の取得
    const majorCategorySelect = document.getElementById('majorCategory');
    const middleCategorySelect = document.getElementById('middleCategory');
    const minorCategorySelect = document.getElementById('minorCategory');
    const statusSelect = document.getElementById('statusSelect');
    const sortSelect = document.getElementById('sortSelect');
    const productTypeInput = document.getElementById('productTypeInput');
    const applyFiltersBtn = document.getElementById('applyFilters');
    const clearFiltersBtn = document.getElementById('clearFilters');
    const searchForm = document.getElementById('searchForm');
    
    // タブボタンの取得
    const tabButtons = document.querySelectorAll('[data-tab]');
    
    // 現在選択されているカテゴリIDを管理
    let selectedCategories = {
        major: '',
        middle: '',
        minor: ''
    };

    // 初期化
    init();

    function init() {
        // 大カテゴリを読み込み
        loadMajorCategories();
        
        // イベントリスナーの設定
        setupEventListeners();
        
        // 現在のステータスを復元
        restoreCurrentStatus();
    }

    function setupEventListeners() {
        // カテゴリ選択の連動
        majorCategorySelect.addEventListener('change', onMajorCategoryChange);
        middleCategorySelect.addEventListener('change', onMiddleCategoryChange);
        minorCategorySelect.addEventListener('change', onMinorCategoryChange);
        
        // フィルタボタン
        applyFiltersBtn.addEventListener('click', applyFilters);
        clearFiltersBtn.addEventListener('click', clearFilters);
        
        // ソート変更
        sortSelect.addEventListener('change', function() {
            applyFilters();
        });
        
        // タブ切替
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tab = this.getAttribute('data-tab');
                switchTab(tab);
            });
        });
        
        // 検索フォーム送信
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            applyFilters();
        });
    }

    function restoreCurrentStatus() {
        // URLパラメータからステータスを復元
        const urlParams = new URLSearchParams(window.location.search);
        const currentStatus = urlParams.get('status');
        if (currentStatus) {
            statusSelect.value = currentStatus;
        }
    }

    async function loadMajorCategories() {
        try {
            const response = await fetch('/api/taxons/');
            const categories = await response.json();
            
            populateSelect(majorCategorySelect, categories);
        } catch (error) {
            console.error('大カテゴリの読み込みに失敗:', error);
        }
    }

    async function onMajorCategoryChange() {
        const selectedId = majorCategorySelect.value;
        selectedCategories.major = selectedId;
        selectedCategories.middle = '';
        selectedCategories.minor = '';
        
        // 中カテゴリと小カテゴリをリセット
        resetSelect(middleCategorySelect);
        resetSelect(minorCategorySelect);
        
        if (selectedId) {
            middleCategorySelect.disabled = false;
            await loadMiddleCategories(selectedId);
        } else {
            middleCategorySelect.disabled = true;
            minorCategorySelect.disabled = true;
        }
    }

    async function loadMiddleCategories(parentId) {
        try {
            const response = await fetch(`/api/taxons/?parent=${parentId}`);
            const categories = await response.json();
            
            populateSelect(middleCategorySelect, categories);
        } catch (error) {
            console.error('中カテゴリの読み込みに失敗:', error);
        }
    }

    async function onMiddleCategoryChange() {
        const selectedId = middleCategorySelect.value;
        selectedCategories.middle = selectedId;
        selectedCategories.minor = '';
        
        // 小カテゴリをリセット
        resetSelect(minorCategorySelect);
        
        if (selectedId) {
            minorCategorySelect.disabled = false;
            await loadMinorCategories(selectedId);
        } else {
            minorCategorySelect.disabled = true;
        }
    }

    async function loadMinorCategories(parentId) {
        try {
            const response = await fetch(`/api/taxons/?parent=${parentId}`);
            const categories = await response.json();
            
            populateSelect(minorCategorySelect, categories);
        } catch (error) {
            console.error('小カテゴリの読み込みに失敗:', error);
        }
    }

    function onMinorCategoryChange() {
        const selectedId = minorCategorySelect.value;
        selectedCategories.minor = selectedId;
    }

    function populateSelect(selectElement, options) {
        // 最初のオプション以外を削除
        selectElement.innerHTML = '<option value="">選択してください</option>';
        
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.id;
            optionElement.textContent = option.name;
            selectElement.appendChild(optionElement);
        });
    }

    function resetSelect(selectElement) {
        selectElement.innerHTML = '<option value="">選択してください</option>';
        selectElement.disabled = true;
    }

    function applyFilters() {
        // 選択されたカテゴリIDを決定（小 > 中 > 大の優先順位）
        let productTypeId = '';
        if (selectedCategories.minor) {
            productTypeId = selectedCategories.minor;
        } else if (selectedCategories.middle) {
            productTypeId = selectedCategories.middle;
        } else if (selectedCategories.major) {
            productTypeId = selectedCategories.major;
        }
        
        // 隠しフィールドに設定
        productTypeInput.value = productTypeId;
        
        // フォームを送信
        searchForm.submit();
    }

    function clearFilters() {
        // フォームをリセット
        searchForm.reset();
        
        // カテゴリ選択をリセット
        selectedCategories = {
            major: '',
            middle: '',
            minor: ''
        };
        
        resetSelect(middleCategorySelect);
        resetSelect(minorCategorySelect);
        minorCategorySelect.disabled = true;
        
        // 隠しフィールドをクリア
        productTypeInput.value = '';
        
        // フィルタを適用（すべてクリアした状態で検索）
        applyFilters();
    }

    function switchTab(tab) {
        // タブの外観を更新
        tabButtons.forEach(button => {
            button.classList.remove('active');
        });
        
        const activeButton = document.querySelector(`[data-tab="${tab}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
        
        // 隠しフィールドを更新
        const tabInput = document.querySelector('input[name="tab"]');
        if (tabInput) {
            tabInput.value = tab;
        }
        
        // フィルタを適用
        applyFilters();
    }

    // アイテムカードのホバーエフェクト
    document.querySelectorAll('.item-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // ローディング状態の管理
    function showLoading() {
        applyFiltersBtn.disabled = true;
        applyFiltersBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>読み込み中...';
    }

    function hideLoading() {
        applyFiltersBtn.disabled = false;
        applyFiltersBtn.innerHTML = '<i class="fas fa-filter me-1"></i>フィルタを適用';
    }

    // エラーハンドリング
    window.addEventListener('error', function(e) {
        console.error('JavaScript Error:', e.error);
        hideLoading();
    });
});