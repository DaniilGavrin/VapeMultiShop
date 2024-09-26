document.addEventListener("DOMContentLoaded", async () => {
    const productsContainer = document.querySelector(".products-container");

    try {
        // Отправка GET-запроса
        const response = await fetch('http://127.0.0.1:8000/pods', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Проверка на успешность ответа
        if (!response.ok) {
            throw new Error('Ошибка сети');
        }

        // Преобразование ответа в JSON
        const data = await response.json();

        // Вывод товаров на страницу
        data.forEach(product => {
            const productElement = document.createElement("div");
            productElement.classList.add("product-card");
        
            const buttonClass = product.наличие ? "buy-button" : "buy-button disabled"; // Определяем класс кнопки
            const buttonDisabled = product.наличие ? "" : "disabled"; // Определяем атрибут disabled
        
            productElement.innerHTML = `
                <div class="product-image">
                    <img src="${product.imageUrl}" alt="${product.name}">
                </div>
                <h3 class="product-title">${product.name}</h3>
                <p class="product-id">ID товара: ${product.id}</p>
                <p class="product-availability">${product.наличие ? 'В наличии' : 'Нет в наличии'}</p>
                <p class="product-price">${product.price} ₽</p>
                <button class="${buttonClass}" ${buttonDisabled}>Купить</button>
            `;
        
            productsContainer.appendChild(productElement);
        });
    } catch (error) {
        console.error('Ошибка при запросе:', error);
    }
});
