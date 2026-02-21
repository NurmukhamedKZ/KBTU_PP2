import requests

url = "https://raw.githubusercontent.com/Beisenbek/programming-principles-2/main/Practice%2004/exercices/json/sample-data.json"
response = requests.get(url)

json_data = response.json()

for item in json_data["imdata"]:
    attrs = item["l1PhysIf"]["attributes"]
    for key, val in attrs.items():
        print(f"{key}: {val}")
    print("-" * 40)