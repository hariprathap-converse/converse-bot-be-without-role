import json

import requests

url = "http://localhost:8001/analytics/analytics"

# Simplified payload structure
payload = {
    "table_name": "employee_performance",
    "chart": {
        "type": "bar",
        "x": "department",
        "y": "salary",
        "x_table_name": "departments",
        "y_table_name": "employee_performance",
    },
}

print("Testing Clean Analytics Payload (Department vs Salary)...")
try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    else:
        print("Error Response:")
        print(response.text)
except Exception as e:
    print(f"Request failed: {e}")
