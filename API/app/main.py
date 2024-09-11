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

@app.post("/auth")
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
    data = await request.json()
    auth_data = AuthRequest(**data)
    
    # Проверяем авторизацию
    if not database.validate_auth(auth_data.token, auth_data.uid):
        return {"status": "error", "error": ["Invalid token or uid"]}
    
    # Если авторизация прошла успешно, возвращаем корзину
    cart = database.get_cart(auth_data.uid)
    return {"status": "success", "cart": cart}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="100.66.163.103", port=8000)