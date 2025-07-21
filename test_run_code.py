import requests

url = "http://127.0.0.1:5000/run"
data = {
    "code": "print('Hello World!')",
    "language": "python"
}

response = requests.post(url, json=data)
print(response.json())
