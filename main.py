from flask import Flask, render_template, request, redirect
from google.auth.transport import requests
import google.oauth2.id_token
from datetime import datetime
import random
from google.cloud import datastore,storage
import json
from models import File,Directory,User
import local_constants


app = Flask(__name__)
datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()

def createUserInfo(user_data):
    entity_key = datastore_client.key("UserDetails", user_data["email"])
    entity = datastore.Entity(key=entity_key)
    userDetails = User(username=user_data["name"], email=user_data["email"])
    entity.update(userDetails.__dict__)
    datastore_client.put(entity)

def retrieveUserInfo(user_data):
    entity_key = datastore_client.key('UserInfo', user_data['email'])
    entity = datastore_client.get(entity_key)
    return entity

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
            print(claims)
    return claims

def createDefaultDirectory(user_data):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(user_data["email"]+'/')
    blob.upload_from_string('', content_type='application/x-www-formurlencoded; charset=UTF-8')

#root function is a default function
@app.route('/')
def root():
    user_data =checkUserData();
    if user_data == None:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)
    else:
        if user_data["email"] != None:
            user_info = retrieveUserInfo(user_data)
            if user_info == None:
                createUserInfo(user_data)
                createDefaultDirectory(user_data)
            return render_template("main.html", user_data=user_data)
        else:
            error_message = "Page not loaded! User Data is missing"
            return render_template("index.html", user_data=user_data, error_message=error_message)




@app.route("/singnout", methods=["GET", "POST"])
def signOut():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
