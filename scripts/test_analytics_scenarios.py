import requests
import json

url = "http://localhost:8001/analytics/analytics"

def run_test(name, payload):
    print(f"\n--- Running Test: {name} ---")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("Success!")
            print(f"Chart Type: {data['chart']['type']}")
            print(f"Summary: {data['summary']}")
            print(f"First 2 Grouped Rows: {data['grouped'][:2]}")
        else:
            print(f"FAILED (Status {response.status_code}):")
            print(response.text)
    except Exception as e:
        print(f"Exception: {e}")

# 1. Salary by Position
payload_salary_position = {
  "table_name": "employee_performance",
  "chart": {
    "type": "bar",
    "x": "position",
    "y": "salary",
    "x_table_name": "positions",
    "y_table_name": "employee_performance"
  }
}

# 2. Incentive by Department (Multi-hop join: Department -> Employee -> Incentive)
payload_incentive_dept = {
  "table_name": "employee_performance",
  "chart": {
    "type": "bar",
    "x": "department",
    "y": "incentive",
    "x_table_name": "departments", 
    "y_table_name": "incentives"  
  }
}

# 3. Performance by Department
payload_performance_dept = {
  "table_name": "employee_performance",
  "chart": {
    "type": "line",
    "x": "department",
    "y": "performance",
    "x_table_name": "departments",
    "y_table_name": "employee_performance"
  }
}

# 4. Incentive by Position (Multi-hop join: Position -> Employee -> Incentive)
payload_incentive_position = {
  "table_name": "employee_performance",
  "chart": {
    "type": "bar",
    "x": "position",
    "y": "incentive",
    "x_table_name": "positions",
    "y_table_name": "incentives"
  }
}

run_test("Salary by Position", payload_salary_position)
run_test("Incentive by Department", payload_incentive_dept)
run_test("Performance by Department", payload_performance_dept)
run_test("Incentive by Position", payload_incentive_position)
