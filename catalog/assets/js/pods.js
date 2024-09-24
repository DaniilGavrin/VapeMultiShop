// Функция для создания карточки товара
function createProductCard(product) {
    const productCard = document.createElement('div');
    productCard.classList.add('category');

    // Блок с изображением товара
    const productImage = document.createElement('div');
    productImage.classList.add('category-image');
    const img = document.createElement('img');
    img.src = product.imageUrl; // Используем URL изображения из данных API
    img.alt = product.name;     // Название товара
    img.classList.add('image');
    productImage.appendChild(img);

    const productInfo = document.createElement('div');
    productInfo.classList.add('game-info');

    // Название товара
    const title = document.createElement('h3');
    title.classList.add('title');
    title.textContent = product.name;
    productInfo.appendChild(title);

    // Цена товара
    const price = document.createElement('p');
    price.classList.add('price');
    price.textContent = `Цена: ${product.price}₽`;
    productInfo.appendChild(price);

    // Наличие товара
    const availability = document.createElement('p');
    availability.classList.add('availability');
    availability.textContent = product.наличие ? 'В наличии' : 'Нет в наличии';
    availability.style.color = product.наличие ? 'green' : 'red';
    productInfo.appendChild(availability);

    // Кнопка "Открыть"
    const button = document.createElement('button');
    button.classList.add('buy-button');
    button.textContent = 'Открыть';
    button.dataset.productId = product.id;  // ID товара для будущих действий
    button.addEventListener('click', function () {
        // Здесь можно добавить обработку нажатия кнопки
        console.log(`Открыт продукт ID: ${product.id}`);
    });
    productInfo.appendChild(button);

    productCard.appendChild(productImage);
    productCard.appendChild(productInfo);

    return productCard;
}

// Функция для загрузки товаров с API
function loadProducts() {
    fetch('https://api.example.com/pods') // Замените на реальный URL API
        .then(response => response.json())
        .then(data => {
            const productList = document.getElementById('product-list');
            productList.innerHTML = '';  // Очищаем контейнер перед добавлением товаров
            data.forEach(product => {
                const productCard = createProductCard(product);
                productList.appendChild(productCard);
            });
        })
        .catch(error => {
            console.error('Ошибка загрузки данных:', error);
        });
}

// Запуск функции при загрузке страницы
document.addEventListener('DOMContentLoaded', loadProducts);
