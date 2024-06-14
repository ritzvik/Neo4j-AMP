import requests

class CAIHostedModel:
    def __init__(self, model_endpoint: str, model_id: str, cdp_token: str):
        self.model_endpoint = model_endpoint
        self.model_id = model_id
        self.cdp_token = cdp_token

    def invoke(self, prompt: str, temperature: float = 0.2, max_tokens: int = 256):
        url = f"{self.model_endpoint}/v1/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.cdp_token}",
        }
        request_body = {
            "model": self.model_id,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        response = requests.post(url, headers=headers, json=request_body)
        print(response.json())
        response_text = response.json()["choices"][0]["text"]
        return response_text
