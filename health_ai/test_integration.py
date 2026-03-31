# health_ai/test_integration.py
import requests
import json

BASE_URL = "http://localhost:8000/api"
TOKEN = "YOUR_JWT_ACCESS_TOKEN"

def test_upload():
    url = f"{BASE_URL}/upload-report/"
    files = {'file': open('sample_report.pdf', 'rb')}
    data = {'report_type': 'Blood Test'}
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    response = requests.post(url, files=files, data=data, headers=headers)
    print("Upload Response:", response.json())

def test_query():
    url = f"{BASE_URL}/ai-query/"
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {"question": "What is my haemoglobin level?"}
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("Query Response:", response.json())

if __name__ == "__main__":
    print("Integration test mockup. Replace TOKEN and sample_report.pdf to run.")
    # test_upload()
    # test_query()
