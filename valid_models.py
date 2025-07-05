import requests
API_KEY = "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"

resp = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {API_KEY}"}
)
print(resp.json())
