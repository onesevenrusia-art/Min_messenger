    document.addEventListener('DOMContentLoaded', function() {
        const photoContainer = document.querySelector('.photo-container');
        const photoAdd = document.querySelector('.photo-add');
        const photoDelete = document.querySelector('.photo-delete');
        const photoUpload = document.getElementById('photo_upload');
        const myPhoto = document.getElementById('my_photo');

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