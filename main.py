from flask import Flask, render_template, request, redirect
from google.auth.transport import requests
import google.oauth2.id_token
from datetime import datetime
import random
from google.cloud import datastore
import json
from models import Room,Booking,User

app = Flask(__name__)
datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()

def checkUserData():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    addresses = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            return render_template("error.html", error_message=str(exc))
    return claims

#root function is a default function
@app.route('/')
def root():
    user_data =checkUserData();
    if user_data == None:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)
    else:
        todayDate= datetime.today().strftime('%Y-%m-%d')
        return render_template("main.html", user_data=user_data, todayDate=todayDate)


@app.route("/singnout", methods=["GET", "POST"])
def signOut():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
