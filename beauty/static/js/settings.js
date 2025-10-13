/*!
 * コスメ期限管理アプリ - 設定ページスクリプト
 * パスワード強度チェックと入力値検証機能を実装
 */

document.addEventListener('DOMContentLoaded', function() {
    // フォーム要素を取得
    const passwordForm = document.getElementById('passwordForm');
    const profileForm = document.getElementById('profileForm');
    const currentPasswordField = document.getElementById('current_password');
    const newPassword1Field = document.getElementById('new_password1');
    const newPassword2Field = document.getElementById('new_password2');
    const changePasswordBtn = document.getElementById('changePasswordBtn');

    // パスワード強度インジケーターの要素を取得/作成
    let strengthIndicator = document.getElementById('passwordStrength');
    let matchIndicator = document.getElementById('passwordMatch');

    // パスワード強度チェック関数
    function checkPasswordStrength(password) {
        let strength = 0;
        let feedback = '';
        
        // 長さチェック
        if (password.length >= 8) strength += 1;
        else feedback += '8文字以上にしてください。 ';
        
        // 英文字チェック
        if (/[A-Za-z]/.test(password)) strength += 1;
        else feedback += '英文字を含めてください。 ';
        
        // 数字チェック
        if (/\d/.test(password)) strength += 1;
        else feedback += '数字を含めてください。 ';
        
        // 特殊文字チェック（ボーナス）
        if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
            strength += 1;
        }

        // 強度レベルの決定
        let level = 'weak';
        let levelText = '弱い';
        if (strength >= 3) {
            level = 'strong';
            levelText = '強い';
            feedback = 'パスワード強度は十分です。';
        } else if (strength >= 2) {
            level = 'medium';
            levelText = '普通';
        } else {
            levelText = '弱い';
        }

        return { level, levelText, feedback, strength };
    }

    // パスワード強度表示の更新
    function updatePasswordStrength(password) {
        if (!strengthIndicator) return;

        const result = checkPasswordStrength(password);
        
        // プログレスバーの作成/更新
        let progressBar = strengthIndicator.querySelector('.password-strength');
        if (!progressBar) {
            progressBar = document.createElement('div');
            progressBar.className = 'password-strength';
            strengthIndicator.appendChild(progressBar);
        }

        // フィードバックテキストの作成/更新
        let feedbackText = strengthIndicator.querySelector('.password-feedback');
        if (!feedbackText) {
            feedbackText = document.createElement('div');
            feedbackText.className = 'password-feedback';
            strengthIndicator.appendChild(feedbackText);
        }

        // スタイルの更新
        progressBar.className = `password-strength ${result.level}`;
        progressBar.style.width = `${(result.strength / 3) * 100}%`;
        
        feedbackText.className = `password-feedback ${result.level}`;
        feedbackText.innerHTML = `<i class="fas fa-shield-alt me-1"></i>強度: ${result.levelText} - ${result.feedback}`;
    }

    // パスワード一致チェック
    function updatePasswordMatch(password1, password2) {
        if (!matchIndicator || !password2) return;

        const isMatch = password1 === password2 && password2.length > 0;
        const isEmpty = password2.length === 0;
        
        if (isEmpty) {
            matchIndicator.innerHTML = '';
            return;
        }

        if (isMatch) {
            matchIndicator.innerHTML = '<i class="fas fa-check-circle me-1"></i>パスワードが一致しています';
            matchIndicator.className = 'password-match match';
        } else {
            matchIndicator.innerHTML = '<i class="fas fa-times-circle me-1"></i>パスワードが一致していません';
            matchIndicator.className = 'password-match no-match';
        }
    }

    // パスワードフィールドのイベントリスナー
    if (newPassword1Field) {
        newPassword1Field.addEventListener('input', function() {
            const password = this.value;
            updatePasswordStrength(password);
            updatePasswordMatch(password, newPassword2Field.value);
        });
    }

    if (newPassword2Field) {
        newPassword2Field.addEventListener('input', function() {
            updatePasswordMatch(newPassword1Field.value, this.value);
        });
    }

    // フォーム送信前の検証
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            const currentPassword = currentPasswordField.value;
            const newPassword1 = newPassword1Field.value;
            const newPassword2 = newPassword2Field.value;

            // バリデーションチェック
            let errors = [];

            if (!currentPassword) {
                errors.push('現在のパスワードを入力してください。');
            }

            if (!newPassword1) {
                errors.push('新しいパスワードを入力してください。');
            } else {
                const strength = checkPasswordStrength(newPassword1);
                if (strength.strength < 2) {
                    errors.push('より強いパスワードを設定してください。');
                }
            }

            if (!newPassword2) {
                errors.push('パスワードの確認入力をしてください。');
            } else if (newPassword1 !== newPassword2) {
                errors.push('パスワードが一致していません。');
            }

            if (errors.length > 0) {
                e.preventDefault();
                alert('以下のエラーを修正してください:\n\n' + errors.join('\n'));
                return false;
            }

            // 送信確認
            if (!confirm('パスワードを変更しますか？')) {
                e.preventDefault();
                return false;
            }
        });
    }

    // プロフィールフォームの送信確認
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            if (!confirm('プロフィール情報を更新しますか？')) {
                e.preventDefault();
                return false;
            }
        });
    }

    // 通知設定トグルの視覚的フィードバック
    const notificationToggle = document.getElementById('notifications_enabled');
    if (notificationToggle) {
        notificationToggle.addEventListener('change', function() {
            const label = this.nextElementSibling;
            if (this.checked) {
                label.innerHTML = '<i class="fas fa-bell me-2"></i>通知を受け取る';
            } else {
                label.innerHTML = '<i class="fas fa-bell-slash me-2"></i>通知を受け取る';
            }
        });

        // 初期状態の設定
        const label = notificationToggle.nextElementSibling;
        if (notificationToggle.checked) {
            label.innerHTML = '<i class="fas fa-bell me-2"></i>通知を受け取る';
        } else {
            label.innerHTML = '<i class="fas fa-bell-slash me-2"></i>通知を受け取る';
        }
    }

    // リアルタイムバリデーション
    function addRealtimeValidation(field, validator) {
        if (!field) return;

        field.addEventListener('blur', function() {
            const isValid = validator(this.value);
            if (isValid) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });

        field.addEventListener('input', function() {
            this.classList.remove('is-invalid', 'is-valid');
        });
    }

    // ユーザーネームの検証
    const usernameField = document.getElementById('username');
    if (usernameField) {
        addRealtimeValidation(usernameField, function(value) {
            return value.length >= 1 && value.length <= 150;
        });
    }

    // 現在のパスワードの検証
    if (currentPasswordField) {
        addRealtimeValidation(currentPasswordField, function(value) {
            return value.length > 0;
        });
    }

    // スムーズスクロール（エラーがある場合）
    function scrollToFirstError() {
        const firstError = document.querySelector('.is-invalid');
        if (firstError) {
            firstError.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
            firstError.focus();
        }
    }

    // ページ読み込み時にエラーがあるかチェック
    setTimeout(scrollToFirstError, 100);

    console.log('Settings page JavaScript loaded successfully');
});