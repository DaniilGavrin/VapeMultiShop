from fastapi import FastAPI, Request
from pydantic import BaseModel
import json
import database

class AuthRequest(BaseModel):
    token: str
    uid: str
    class Config:
        schema_extra = {"example": {"token": "your_token", "uid": "your_uid"}}
        allow_population_by_field_name = True

# проверяем существование списка таблиц


app = FastAPI()

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="100.66.163.103", port=8000)