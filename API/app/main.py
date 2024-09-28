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

@app.post("/login")
async def login(login: Login):
    """
    /login
    args:
        JSON:
            username: str
            password: str
    """
    try:
        if database.DatabaseUSER.check_valid_login(login.username, login.password):
            return {"status": "ok", "error": []}
        else:
            return {"status": "error", "error": ["Not valid password and username"]}
    except Exception as e:
        return {"status": "error", "error": ["Invalid input data", str(e)]}

# Маршрут для получения списка товаров
@app.get("/pods", response_model=list[Product])
async def get_products():
    db = database.DatabaseLITE("API/app/shop.db")  # Название базы данных
    # TODO: изменить работу базы данных на категории а не на просто запрос в pods
    products = db.get_products()
    db.close()

    # Преобразуем данные из базы в нужный формат
    return [{"id": id, "name": name, "imageUrl": APIUrl_images + imageUrl + formatimg, "price": price, "наличие": наличие}
            for id, name, imageUrl, price, наличие in products]

@app.post("/register")
async def register(register: Register):
    user = register.username
    mail = register.email
    password = register.password_hash
    hash_password = database.HashUtil.hash_password(password)
    token = database.HashUtil.token_generator(user, mail)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.31.51", port=8000)