from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json
import database

APIUrl_images = "http://127.0.0.1/images/"

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

# Пример данных
products = [
    {
        "id": 1,
        "name": "Vaporesso xros 4 mini",
        "imageUrl": f"{APIUrl_images}/vaporesso4mini.webp",
        "price": 1899.00,
        "наличие": True
    },
    {
        "id": 2,
        "name": "Vaporesso xros 4",
        "imageUrl": f"{APIUrl_images}/vaporesso4mini.webp",
        "price": 2100.00,
        "наличие": False
    }
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory="static/images"), name="images")

@app.get("/")
async def root():
    # возвращаем 404
    return {"message": "Not Found"}

@app.get("/auth")
async def auth(request: Request):
    """
    /auth
    args:
        JSON:
            token: str
            uid: str

    return:
        JSON:
            status: str
            error: list
            cart:
    """
    # Получаем данные из тела запроса и проверяем валидность
    # Получаем данные из тела запроса
    try:
        data = await request.json()
        auth_data = AuthRequest(**data)
    except Exception as e:
        return {"status": "error", "error": ["Invalid input data", str(e)]}

    # Подключаемся к базе данных и проверяем авторизацию
    db = database.Database(host="localhost", user="root", password="your_password", database="your_database")
    db.connect()
    
    if not db.validate_auth(auth_data.token, auth_data.uid):
        db.close()
        return {"status": "error", "error": ["Invalid token or uid"]}
    
    #заправшиваем товары из базы данных
    products = db.get_products()
    
    # Если авторизация успешна, получаем корзину
    cart = db.get_cart(auth_data.uid)

    db.close()
    # возвращаем ответ
    return {"status": "success", "products": products, "cart": cart}

# Маршрут для получения списка товаров
@app.get("/pods", response_model=list[Product])
async def get_products():
    return products


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)