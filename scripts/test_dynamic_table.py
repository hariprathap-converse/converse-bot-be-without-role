import requests
import json
import sys

BASE_URL = "http://localhost:8001"

def test_dynamic_table_config():
    print(f"Testing GET {BASE_URL}/salary-data...")
    
    try:
        # 1. Test Default Table (employee_performance)
        response = requests.get(f"{BASE_URL}/salary-data")
        response.raise_for_status()
        data = response.json()
        
        print("\n--- Response Overview ---")
        print(f"Title: {data.get('title')}")
        print(f"Table Name: {data.get('tableName')}")
        print(f"Columns Count: {len(data.get('columns'))}")
        print(f"Data Rows Count: {len(data.get('data'))}")
        
        # Verify Metadata Structure
        assert data.get("tableName") == "employee_performance"
        assert len(data.get("columns")) > 0
        assert "accessorKey" in data["columns"][0]
        
        # Verify Specific Column Config (e.g., dynamic color map)
        dept_col = next((c for c in data["columns"] if c["accessorKey"] == "department"), None)
        assert dept_col is not None
        assert "cellConfig" in dept_col
        assert "colorMap" in dept_col["cellConfig"]
        print("\n[SUCCESS] Dynamic color map resolution verified.")

        # 2. Test Invalid Table Name
        print(f"\nTesting GET {BASE_URL}/salary-data?table=non_existent...")
        response_invalid = requests.get(f"{BASE_URL}/salary-data?table=non_existent")
        assert response_invalid.status_code == 404
        print("[SUCCESS] Invalid table returned 404 as expected.")
        
        print("\n✅ All dynamic table tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_dynamic_table_config()
