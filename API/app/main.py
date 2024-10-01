from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json
import database
import os

print(os.getcwd())

APIUrl_images = "http://192.168.31.51:8000/images/"
formatimg = ".webp"

class AuthFold(BaseModel):
    username: str
    token: str

class testdata(BaseModel):
    username: str

class AuthRequest(BaseModel):
    token: str
    uid: str
    class Config:
        schema_extra = {"example": {"token": "your_token", "uid": "your_uid"}}
        allow_population_by_field_name = True

# Модель для товара
class Product(BaseModel):
    id: int
    name: str
    imageUrl: str
    price: float
    наличие: bool
    categories: str

# Модель для входа
class Login(BaseModel):
    username: str
    password: str

class Register(BaseModel):
    username: str
    email: str
    password_hash: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory="API/app/static/images"), name="images")

@app.get("/")
async def root():
    # возвращаем 404
    return {"message": "Not Found"}

# Маршрут для получения списка товаров
@app.get("/pods", response_model=list[Product])
async def get_products():
    db = database.DatabaseUSER("API/app/shop.db")  # Название базы данных
    # TODO: изменить работу базы данных на категории а не на просто запрос в pods
    products = db.get_pods()
    db.close()

    # Преобразуем данные из базы в нужный формат
    return [{"id": id, "name": name, "imageUrl": APIUrl_images + imageUrl + formatimg, "price": price, "наличие": наличие}
            for id, name, imageUrl, price, наличие in products]

@app.post("/login")
async def logins(login: Login):
    """
    /login
    args:
        JSON:
            username: str
            password: str
    """
    db_user = database.DatabaseUSER("API/app/shop.db")
    username = login.username
    password = login.password
    try:
        if db_user.check_valid_login(username, password):
            db_user = database.DatabaseUSER("API/app/shop.db")
            user_data = db_user.get_data(username)
            # Формируем ответ с учетом возможных null значений
            response = {
                "status": "ok",
                "data": {
                    "id": user_data[0],
                    "user_id": user_data[1],
                    "username": user_data[2],
                    "email": user_data[3],
                    "token": user_data[5],
                    "user_id": user_data[6],  # Включаем даже если None
                    "cart_id": user_data[7]  # Включаем даже если None
                }
            }
            print(response)
            return response
        else:
            return {"status": "error", "error": ["Not valid password and username"]}
    except Exception as e:
        return {"status": "error", "error": ["Invalid input data", str(e)]}

@app.post("/register")
async def register(register: Register):
    user = register.username
    mail = register.email
    password = register.password_hash

    print(user, mail, password)

    # Создание экземпляра базы данных
    db = database.DatabaseUSER("API/app/shop.db")

    # Проверка на существование пользователя
    if db.user_exists(register.username, register.email):
        return {"status": "error", "error": ["Пользователь с таким именем или почтой уже существует"]}
    
    hash_password = database.HashUtil.hash_password(password)

    token = database.HashUtil.token_generator(user, mail)

    # Регистрация пользователя
    try:
        db.register_user(register.username, register.email, hash_password, token)
        # Получаем данные пользователя из базы
        user_data = db.get_data(user)
        # Формируем ответ с учетом возможных null значений
        response = {
            "status": "ok",
            "data": {
                "id": user_data[0],
                "user_id": user_data[1],
                "username": user_data[2],
                "email": user_data[3],
                "token": user_data[5],
                "user_id": user_data[6],  # Включаем даже если None
                "cart_id": user_data[7]  # Включаем даже если None
            }
        }
        print(response)
        return response
    except Exception as e:
        return {"status": "error", "error": ["Ошибка при регистрации", str(e)]}
    finally:
        db.close()

@app.post("authfold")
async def authfold(auth: AuthFold):
    username = auth.username
    token = auth.token
    db = database.DatabaseUSER("API/app/shop.db")
    crypt = database.HashUtil.token_check_fold(token)

    # Проверка администратора
    try:
        if db.check_admin(username, crypt):
            return {"status": "ok", "message": "Авторизация успешна"}
        else:
            return {"status": "error", "message": "Пользователь не является администратором или неверный токен"}
    except Exception as e:
        return {"status": "error", "message": "Ошибка проверки администратора", "details": str(e)}
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    database.DatabaseUSER("API/app/shop.db")
    uvicorn.run(app, host="192.168.31.51", port=8000)