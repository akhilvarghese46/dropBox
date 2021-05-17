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
            return claims
        except ValueError as exc:
            return None
    return None

def addNewDirectory(directory):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(directory.dirname)
    blob.upload_from_string('', content_type='application/x-www-formurlencoded; charset=UTF-8')

def getBlobList(prefix):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    blobList = storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET, prefix=prefix.filename)
    directory_list = []
    file_list = []
    returnValue = {}
    for i in blobList:
        if i.name != prefix.filename:
             #print((i.name.split(''+prefix.parent))[1].split('/'))
             dirData = (i.name.split(''+prefix.parent))[1].split('/')
             if(len(dirData)==2 and dirData[1]==''):
                 directory_list.append(i)
             if(len(dirData)==1):
                 file_list.append(i)
             """ if i.name[len(i.name) - 1] == '/':
                 directory_list.append(i)
             else:
                 file_list.append(i)"""
    returnValue["directoryList"] = directory_list
    returnValue["fileList"] = file_list
    return returnValue

def createDefaultDirectory(user_data):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(user_data["email"]+'/')
    blob.upload_from_string('', content_type='application/x-www-formurlencoded; charset=UTF-8')

def deleteDirectory(directoryDetails):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(directoryDetails.dirname)
    blobList = storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET, prefix=directoryDetails.dirname)
    blobNewList=[]
    for i in blobList:
        blobNewList.append(i)
    if(len(blobNewList) == 1):
        blob.delete()
    return len(blobNewList)

def deleteFile(fileDetails):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(fileDetails.filename)
    blob.delete()

#root function is a default function
@app.route('/')
def root():
    user_data =checkUserData();
    if not user_data:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=None, error_message=error_message)
    else:
        try:
            if user_data:
                user_info = retrieveUserInfo(user_data)
                if user_info == None:
                    createUserInfo(user_data)
                    createDefaultDirectory(user_data)

                blobDetails = File(parent=user_data["email"]+'/', filename=user_data["email"]+'/',type=None, size=0, time=None)
                blobList = getBlobList(blobDetails)
                return render_template("main.html", user_data=user_data, directoryList=blobList["directoryList"], fileList=blobList["fileList"], currentDirectoryPath = user_data["email"]+'/')
            else:
                error_message = "Page not loaded! User Data is missing"
                return render_template("index.html", user_data=user_data, error_message=error_message)
        except ValueError as exc:
            error_message = "Page not loaded! User Data is missing"
            return render_template("index.html", user_data=user_data, error_message=error_message)


@app.route("/createNewFolder", methods=["GET", "POST"])
def createNewFolder():
    user_data =checkUserData();
    if user_data != None:
        try:
            formData = dict(request.form)
            newDirectoryName = formData.get("folderName")
            currentDirectoryName = formData.get("currentDirectoryPath")
            #if newDirectoryName[len(newDirectoryName) - 1] != '/':
            newDirectoryName = currentDirectoryName + newDirectoryName + '/'
            directoryDetails = Directory(parent=currentDirectoryName, dirname=newDirectoryName, size=0)
            addNewDirectory(directoryDetails)
            blobDetails = File(parent=currentDirectoryName, filename=currentDirectoryName,type=None, size=0, time=None)
            blobList = getBlobList(blobDetails)
            return render_template("main.html", user_data=user_data, directoryList=blobList["directoryList"], fileList=blobList["fileList"], currentDirectoryPath = newDirectoryName)
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route("/deletDir", methods=["GET", "POST"])
def deletDirectory():
    user_data =checkUserData();
    if user_data != None:
        currentDirectoryName = request.args.get('dirName')
        directoryDetails = Directory(parent=currentDirectoryName, dirname=currentDirectoryName, size=0)
        returnValue = deleteDirectory(directoryDetails)
        if returnValue != 1:
            error_message = "This directory already has some folders or files. So user can't delete this folder"
            return render_template("error.html", error_message=error_message,return_url='/')
        return redirect('/')
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route("/deletFile", methods=["GET", "POST"])
def deletFiles():
    user_data =checkUserData();
    if user_data != None:
        currentDirectoryName = request.args.get('fileName')
        fileDetails =File(parent=currentDirectoryName, filename=currentDirectoryName,type=None, size=0, time=None)
        deleteFile(fileDetails)
        return redirect('/')
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route('/openDirectory' , methods=["GET", "POST"])
def openDirectory():
    user_data =checkUserData();
    if not user_data:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=None, error_message=error_message)
    else:
        try:
            if user_data:
                currentDirectoryName = request.args.get('dirName')
                blobDetails = File(parent=currentDirectoryName, filename=currentDirectoryName,type=None, size=0, time=None)
                blobList = getBlobList(blobDetails)
                return render_template("main.html", user_data=user_data, directoryList=blobList["directoryList"], fileList=blobList["fileList"], currentDirectoryPath = currentDirectoryName)
            else:
                error_message = "Page not loaded! User Data is missing"
                return render_template("index.html", user_data=user_data, error_message=error_message)
        except ValueError as exc:
            error_message = "Page not loaded! User Data is missing"
            return render_template("index.html", user_data=user_data, error_message=error_message)


@app.route("/singnout", methods=["GET", "POST"])
def signOut():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
