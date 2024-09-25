# Аутентификация. POST запрос.

Здесь представлена вся информация по маршруту аутенификации **/auth**.

#### Принимающие данные
- uid: str
- user_id: str
>uid и user_id являются не обязательными параметрами, и если данные пользовтаель использует только телеграмм то у него может не быть обычного uid. Но является хотя бы один параметр обязательным
- token: str
- hash: str

### Запросы

#### Правильный curl запрос

``` bash
curl -X POST http://127.0.0.1:8000/auth \
-H "Content-Type: application/json" \
-d "token": "valid_token", "uid": "valid_uid", "user_id": "valid_id", "password": "hashpassword"}'
```

#### Ответ json

``` json
{
    "error": "[]",
    "key": "aba4-an47-v4at-av4a-b7bs",
    "username": "JohnSino228",
    "FirstName": "John",
    "LastName": "Sino",
    "birthday": "09-08-2000",
    "cart": [

    ]
}
```

---

Пример неправильного запроса с отсутствующим токеном авторизации

#### Неправильный curl запрос

``` bash
curl -X POST http://127.0.0.1:8000/auth \
-H "Content-Type: application/json" \
-d "uid": "valid_uid", "user_id": "valid_id", "password": "hashpassword"}'
```

#### Ответ json

``` json
{
    "status": "error",
    "error": [
        "Invalid token"
    ]
}
```

---

> Пример неправильного запроса с отсутствующим id. Параметр user_id не является обязательным если аккаунт не был привязане в аккаунту телеграмм, но является обязательным, если его нету то просто отправляется пустая строка, так система поймет что user_id просто нету у пользователя, иначе запрос выдаст ошибку

#### Неправильный curl запрос

``` bash
curl -X POST http://127.0.0.1:8000/auth \
-H "Content-Type: application/json" \
-d "token": "validtoken", "uid": "valid_uid", "password": "hashpassword"}'
```

#### Ответ json

``` json
{
    "status": "error",
    "error": [
        "Invalid user_id"
    ]
}
```