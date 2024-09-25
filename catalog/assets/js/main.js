// script.js

// Получаем все кнопки с классом 'buy-button'
const buttons = document.querySelectorAll('.buy-button');

// Объект для сопоставления категорий с URL
const categoryMap = {
    'pod': '/category/pods',
    'liquid': '/category/liquids',
    'odnorazki': '/category/odnorazki',
    'zarubeschka': '/category/zarubeschka',
    'now': '/category/new',
    'raschodniki': '/category/raschodniki'
};

// Добавляем обработчик события для каждой кнопки
buttons.forEach(button => {
    button.addEventListener('click', function() {
        // Получаем значение атрибута data-category
        const category = button.getAttribute('data-category');
        
        // Находим соответствующий URL
        const url = categoryMap[category];

        // Если URL найден, переходим по нему
        if (url) {
            window.location.href = url;
        } else {
            alert('Категория не найдена!');
        }
    });
});