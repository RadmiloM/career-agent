import json
import urllib.request

payload = {
    'cv_text': 'Python developer with FastAPI and Docker',
    'job_description': 'Backend engineer with Python and cloud experience',
}

request = urllib.request.Request(
    'http://127.0.0.1:8000/api/analyze',
    data=json.dumps(payload).encode(),
    headers={'Content-Type': 'application/json'},
)

with urllib.request.urlopen(request) as response:
    print(response.read().decode())
