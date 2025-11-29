    document.addEventListener('DOMContentLoaded', function() {


        let currentPhotoFile = null;

        // Обработчик клика на "+" - открыть проводник
        photoAdd.addEventListener('click', function(e) {
            e.preventDefault();
            photoUpload.click();
        });

        // Обработчик выбора файла
        photoUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Проверяем тип файла
                if (!file.type.startsWith('image/')) {
                    alert('Пожалуйста, выберите файл изображения');
                    return;
                }

                // Проверяем размер файла (максимум 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    alert('Размер файла не должен превышать 5MB');
                    return;
                }

                currentPhotoFile = file;

                // Показываем превью
                const reader = new FileReader();
                reader.onload = function(e) {
                    myPhoto.src = e.target.result;
                    // Показываем иконку удаления
                    photoDelete.style.display = 'flex';
                };
                reader.readAsDataURL(file);
            }
        });

        // Обработчик клика на корзину - удалить фото
        photoDelete.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            // Сбрасываем фото
            myPhoto.src = '';
            currentPhotoFile = null;
            photoUpload.value = '';

            // Скрываем иконку удаления
            photoDelete.style.display = 'none';
        });

        // Drag and Drop функционал
        photoContainer.addEventListener('dragover', function(e) {
            e.preventDefault();
            photoContainer.style.borderColor = '#007bff';
        });

        photoContainer.addEventListener('dragleave', function(e) {
            e.preventDefault();
            photoContainer.style.borderColor = '#ccc';
        });

        photoContainer.addEventListener('drop', function(e) {
            e.preventDefault();
            photoContainer.style.borderColor = '#ccc';

            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                if (file.size > 5 * 1024 * 1024) {
                    alert('Размер файла не должен превышать 5MB');
                    return;
                }

                currentPhotoFile = file;

                const reader = new FileReader();
                reader.onload = function(e) {
                    myPhoto.src = e.target.result;
                    photoDelete.style.display = 'flex';
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Функция для получения данных фото (для сохранения)
    function getProfilePhotoData() {
        if (currentPhotoFile) {
            return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = function(e) {
                    resolve(e.target.result); // возвращает base64
                };
                reader.readAsDataURL(currentPhotoFile);
            });
        }
        return Promise.resolve(null);
    }

    // В функции сохранения профиля используйте:
    async function saveProfile() {
        try {
            const photoData = await getProfilePhotoData();

            const profileData = {
                name: document.getElementById('Name_input').value,
                gender: getSelectedGender(), // ваша функция
                age: document.getElementById('AgeINP').value,
                birthday: document.getElementById('DR').value,
                about: document.getElementById('AboutMe').value,
                photo: photoData // base64 строка или null
            };

            // Отправка данных на сервер
            // ... ваш код отправки ...

        } catch (error) {
            console.error('Ошибка сохранения профиля:', error);
        }
    }

    // Функция загрузки существующего фото
    function loadExistingPhoto(photoBase64) {
        if (photoBase64) {
            myPhoto.src = photoBase64;
            photoDelete.style.display = 'flex';
            currentPhotoFile = null; // сбрасываем файл, т.к. используем base64
        }
    }



    Received: { "type": "newdevice", "fingerprint": {}, "email": "dedoutsider@gmail.com", "device": "chrome-c70WJQGxaB1yWg1T#0d6yQc270_nmlVL", "publickey": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA9mnhra6uUH/2laCMZ+ZqPbHzy95V6LPhoe2k4ie+DrA1wXwHFuPdEG1YHOm/YX1Ki3RZhNuQbS/DUAHtsKMedqmEHECFYJNPX10CDYedmJFHcxAzQz1kgYPiz3JOPthYFeoIX1GeocdAVA8MTWbS3xISTWYyj98VeEdhGpKGQgzVhj5jSyB4T25utc63ix8j6a5iZbSaiEnyfOIxqUR+DNT8bCvQqkUFUVJxOkFtMYij92YpX1F3mhSCnL+7Odn0f3GCgJMSEHqeeeMXHLV+huY6xWGV6aD8Z16wc/Uo14+1csx75VvkNzkA7BAzuF8aodcum1pSIQPN+uLoGaDzNQIDAQAB", "ip": "192.168.1.64" }










    .runline {
        display: block;
        width: 200 px;
        background: gray;
        overflow: hidden;
        padding: 5 px;
    }
    .runline > span {
            display: inline - block;
            white - space: nowrap;
            animation: runline 20 s linear infinite 1 s both;
        }
        .runline: hover > span {
            animation - play - state: paused;
        }
    @keyframes runline {
        to { transform: translateX(-100 % ); }
    } <
    div class = "runline" >
        <
        span > Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum < /span> < /
            div >