import requests, json

def test_block():
    payload = {"result": {"src_ip": "198.51.100.25"}}
    r = requests.post("http://127.0.0.1:5000/webhook/block", json=payload)
    print("Response:", r.status_code, r.text)

if __name__ == "__main__":
    test_block()
