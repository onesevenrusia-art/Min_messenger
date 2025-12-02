document.addEventListener('DOMContentLoaded', function() {
    const authBox = document.getElementById('authBox');
    const registerBox = document.getElementById('registerBox');
    const registerBtn = document.getElementById('registerBtn');
    const backBtn = document.getElementById('backBtn');
    const registerForm = document.getElementById('registerForm');
    const nextBtn = document.getElementById('nextBtn');
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');

    // Переход к регистрации
    registerBtn.addEventListener('click', function(e) {
        e.preventDefault();
        authBox.style.display = 'none';
        registerBox.style.display = 'block';
    });

    // Возврат назад
    backBtn.addEventListener('click', function(e) {
        e.preventDefault();
        registerBox.style.display = 'none';
        authBox.style.display = 'block';
    });

    // Проверка заполнения полей
    function checkFormValidity() {
        const isNameValid = nameInput.value.trim().length > 0;
        const isEmailValid = emailInput.value.trim().length > 0 &&
            emailInput.value.includes('@');

        nextBtn.disabled = !(isNameValid && isEmailValid);
    }

    // Слушаем изменения в полях ввода
    nameInput.addEventListener('input', checkFormValidity);
    emailInput.addEventListener('input', checkFormValidity);

    // Обработка отправки формы
    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();

        if (!nextBtn.disabled) {
            const formData = {
                name: nameInput.value.trim(),
                email: emailInput.value.trim(),
                phone: document.getElementById('phone').value.trim()
            };

            console.log('Данные для регистрации:', formData);
            // Здесь будет отправка данных на сервер
            //alert('Регистрация продолжается! Данные: ' + JSON.stringify(formData));
            fetch("/registrform", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData),
            });
        }
    });

    // Плавное появление элементов
    setTimeout(() => {
        document.querySelectorAll('.auth-box').forEach(box => {
            box.style.opacity = '1';
            box.style.transform = 'translateY(0)';
        });
    }, 100);
});

fetch("/", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({}),
    })
    .then(response => response.json())
    .then(result => {


    })
    .catch(error => {
        console.error("Ошибка сети:", error);
    });