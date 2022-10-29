from flask import Flask, request, make_response, jsonify, redirect, url_for
from functools import wraps
import secrets
import hashlib

APP_HOST = "127.0.0.1"
APP_PORT = "5050"
PSW = ""
COOKIE_KEY = "AUTHSECRET"
COOKIE_SECRET = secrets.token_hex(32)


app = Flask(__name__)

def is_auth(f):
    @wraps(f)
    def auth_check(*args, **kwargs):
        cookie = request.cookies.get(COOKIE_KEY)
        if cookie != None and cookie == COOKIE_SECRET:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login', next=request.url))
    return auth_check

@app.route("/home", methods=["GET"])
@is_auth
def home():
    return make_response("SCIAOBELO",200)

# TODO: make a login frontend page
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            data = request.get_json()
            resp = None
            if(hashlib.sha256(data["password"].encode('utf-8')).hexdigest() != PSW):
                respdata = {
                    "success":False,
                    "message":"Wrong password"
                }
                status_code = 400
                resp = make_response(jsonify(respdata), status_code)
            else:
                respdata = {
                    "success":True
                }
                status_code = 200
                resp = make_response(jsonify(respdata), status_code)
                resp.set_cookie(COOKIE_KEY, COOKIE_SECRET)
            return resp
        except:
            respdata = {
                "success":False,
                "message":"something went wrong"
            }
            return make_response(jsonify(respdata), 400)
    elif request.method == "GET":
        return make_response("Sciao belo ma non sei loggato", 200)

if __name__ == "__main__":
    PSW = input("Inserisci password di sistema: ")
    PSW = hashlib.sha256(PSW.encode('utf-8')).hexdigest()
    app.run(host = APP_HOST, port = APP_PORT)