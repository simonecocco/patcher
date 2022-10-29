import requests

SERVER_URL = "127.0.0.1"
SERVER_PORT = "5050"
COOKIE_KEY = "AUTHSECRET"

final_url = f"http://{SERVER_URL}:{SERVER_PORT}"
PSW = ""

def login(data= None, debug=False):
    global PSW
    if not data:
        data = {"password":PSW}
    s = requests.Session()
    headers = {
        "Content-Type":"application/json"
    }
    r = s.post(f"{final_url}/login", headers=headers, json=data)
    if(debug):
        print(r.text, r.cookies)
    return s

# TODO: Enrich this test
def test_login():
    print("Testing login when password is correct...")
    login(debug=True)
    print("Done!")
    return

# TODO: Implement this test
def test_is_auth():
    pass
    


def main():
    test_login()
    test_is_auth()

if __name__ == "__main__":
    PSW = input("Inserisci password: ")
    main()