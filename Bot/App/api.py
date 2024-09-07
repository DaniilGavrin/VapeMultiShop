import requests

class API:
    def __init__(self, token):
        self.token = token
        self.url = "https://api.bytewizard.ru"

    def get_products(self):
        response = requests.get(f"{self.url}/products", headers={"Authorization": f"Bearer {self.token}"})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка получения продуктов: {response.text}")
            return None
        
    def get_profile(self, user_id):
        response = requests.get(f"{self.url}/profile", headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json", "user": user_id})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка получения профиля: {response.text}")
            return None