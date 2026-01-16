import requests

response = requests.get("https://http.cat/status/404")

propiedades = {"status": response.status_code,
               "content/body": response.content}

print(f"Response de la peticion : {propiedades}")