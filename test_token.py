import requests

# 1. Логин
login_response = requests.post(
    "http://127.0.0.1:8000/auth/login",
    json={
        "email": "adeliya64775@gmail.com",
        "password": "Adelia123-"
    }
)

print("Login status:", login_response.status_code)
login_data = login_response.json()
print("Login response:", login_data)

token = login_data.get("access_token")
print(f"\nToken: {token[:50]}...")

# 2. Получение профиля (токен в заголовке)
profile_response = requests.get(
    "http://127.0.0.1:8000/auth/me",
    headers={"Authorization": f"Bearer {token}"}
)

print("\nProfile status:", profile_response.status_code)
print("Profile response:", profile_response.json())