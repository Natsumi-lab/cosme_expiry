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