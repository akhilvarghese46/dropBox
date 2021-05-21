from flask import Flask, render_template, request, redirect, Response
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
    #print("aaa")
    entity_key = datastore_client.key('UserDetails', user_data['email'])
    entity = datastore_client.get(entity_key)
    #print(entity)
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
    blobList = storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET, prefix=directory.dirname)
    blobNewList=[]
    for i in blobList:
        blobNewList.append(i)
    if(len(blobNewList) == 0):
        blob = bucket.blob(directory.dirname)
        blob.upload_from_string('', content_type='application/x-www-formurlencoded; charset=UTF-8')

        entity_key = datastore_client.key("Directory", directory.dirname)
        entity = datastore.Entity(key=entity_key)
        entity.update(directory.__dict__)
        datastore_client.put(entity)

    return len(blobNewList)

def addNewFile(file):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(file.parent + file.filename.filename)
    blobList = storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET, prefix=file.parent)
    blobNewList=[]
    for i in blobList:
        if(i.name == file.parent + file.filename.filename):
            blobNewList.append(i)
    if(len(blobNewList) == 0):
        blob.upload_from_file(file.filename)

    newFilename = file.parent + file.filename.filename
    file.filename = newFilename
    entity_key = datastore_client.key("file", newFilename)
    entity = datastore.Entity(key=entity_key)
    entity.update(file.__dict__)
    datastore_client.put(entity)

    return len(blobNewList)


def getBlobList(prefix):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    blobList = storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET, prefix=prefix.filename)

    dirqrlist=[]
    fileqrlist=[]
    dirrectryqry = datastore_client.query(kind="Directory")
    dirrectryqry = dirrectryqry.add_filter('owner', '=', prefix.owner)
    dirrectryqry = dirrectryqry.add_filter('parent', '=', prefix.filename).fetch()


    for k in dirrectryqry:
        dirqrlist.append(k)

    fileqry = datastore_client.query(kind="file")
    fileqry = fileqry.add_filter('owner', '=', prefix.owner)
    fileqry = fileqry.add_filter('parent', '=', prefix.filename).fetch()
    for j in fileqry:
        fileqrlist.append(j)
    directory_list = []
    file_list = []
    returnValue = {}
    try:
        for i in blobList:


            if i.name != prefix.filename:

                 dirData = (i.name.split(''+prefix.parent))[1].split('/')

                 if(len(dirData)==2 and dirData[1]==''):

                     for j in dirqrlist:

                         if(i.name==j["dirname"]):
                              j["name"] = i.name
                              directory_list.append(j)
                     """dirrectryqry = datastore_client.query(kind="Directory")
                     dirrectryqry = dirrectryqry.add_filter('owner', '=', prefix.owner)
                     dirrectryqry = dirrectryqry.add_filter('dirname', '=', i.name).fetch()
                     for j in dirrectryqry:
                         j["name"] = i.name
                         directory_list.append(j)"""
                 if(len(dirData)==1):
                     for l in fileqrlist:
                         if(i.name==l["filename"]):
                              l["name"] = i.name
                              file_list.append(l)

        returnValue["directoryList"] = directory_list
        returnValue["fileList"] = file_list
    except ValueError as exc:
        print(exc)
    return returnValue

def getAllDirList(prefix):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    blobList = storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET, prefix=prefix.filename)

    dirqrlist=[]
    fileqrlist=[]
    dirrectryqry = datastore_client.query(kind="Directory")
    dirrectryqry = dirrectryqry.add_filter('owner', '=', prefix.owner).fetch()

    for k in dirrectryqry:
        dirqrlist.append(k)
    fileqry = datastore_client.query(kind="file")
    fileqry = fileqry.add_filter('owner', '=', prefix.owner).fetch()
    for j in fileqry:
        fileqrlist.append(j)
    directory_list = []
    file_list = []
    returnValue = {}
    try:
        for i in blobList:

            if i.name != prefix.filename:
                 dirData = (i.name.split(''+prefix.parent))[1].split('/')
                 if(dirData[len(dirData)-1]==''):
                     for j in dirqrlist:
                         if(i.name==j["dirname"]):
                              j["name"] = i.name
                              directory_list.append(j)
                 else:
                     for l in fileqrlist:
                         if(i.name==l["filename"]):
                              l["name"] = i.name
                              file_list.append(l)

        returnValue["directoryList"] = directory_list
        returnValue["fileList"] = file_list
    except ValueError as exc:
        print(exc)
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
        entity_key = datastore_client.key("Directory", directoryDetails.dirname)
        datastore_client.delete(key=entity_key)
    return len(blobNewList)

def deleteFile(fileDetails):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(fileDetails.filename)
    blob.delete()

    entity_key = datastore_client.key("file", fileDetails.filename)
    datastore_client.delete(key=entity_key)

def downloadFile(fileDetails):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(fileDetails.filename)
    return blob.download_as_bytes()

def overwriteUploadFile(file):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(file.parent + file.filename.filename)
    blobList = storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET, prefix=file.parent)
    blobNewList=[]
    for i in blobList:
        if(i.name == file.parent + file.filename.filename):
            blobNewList.append(i)

    #if(len(blobNewList) == 0):
        #blob.upload_from_file(file.filename)
    return len(blobNewList)

def shareDirectory(directoryDetails):
    userdata={}
    userdata["email"] = directoryDetails.owner
    userdata["name"] = directoryDetails.owner
    user_info = retrieveUserInfo(userdata)
    if user_info == None:
        createUserInfo(userdata)
        createDefaultDirectory(userdata)

    newDirectoryName = str(directoryDetails.owner)+'/'+ 'Shared/'
    directoryNewDetails = Directory(parent=directoryDetails.owner+'/', dirname=newDirectoryName, size=0, owner=directoryDetails.owner, isShared=0, sharedBy='')
    rvalue=addNewDirectory(directoryNewDetails)
    rvalue=addNewDirectory(directoryDetails)
    originalDirectory = directoryDetails.dirname.split(directoryDetails.owner+ '/Shared')
    orginalDirectory = str(directoryDetails.sharedBy) + originalDirectory[1]
    blobNewList=[]
    #rvalue = 1
    #print("0---------------0")
    #print(orginalDirectory)

    blobDetails = File(parent=orginalDirectory, filename=orginalDirectory,type=None, size=0, time=None,owner=directoryDetails.sharedBy, isShared=0, sharedBy='')
    #blobList = getBlobList(blobDetails)
    blobList = getAllDirList(blobDetails)

    #print(blobList["directoryList"])
    for i in blobList["directoryList"]:

        #thisdirparent = directoryDetails.dirname
        thisdirparent = i["parent"].split(directoryDetails.sharedBy+'/')
        thisdirparent= newDirectoryName+thisdirparent[1]
        thisdirname = i["dirname"].split(directoryDetails.sharedBy+'/')
        thisdirnameval= newDirectoryName+thisdirname[1]

        #print(thisdirnameval)
        dirNewDetails = Directory(parent=thisdirparent, dirname=thisdirnameval, size=0, owner=directoryDetails.owner, isShared=1, sharedBy=directoryDetails.sharedBy)
        rvalue = addNewDirectory(dirNewDetails)

    for j in blobList["fileList"]:

        thisdirparent = j["parent"].split(directoryDetails.sharedBy+'/')
        thisdirparent= newDirectoryName+thisdirparent[1]
        thisdirname = j["filename"].split(directoryDetails.sharedBy+'/')
        thisdirnameval= newDirectoryName+thisdirname[1]
        fileData = File(parent=thisdirparent, filename=j["filename"] ,type=j["type"], size=j["size"], time=j["time"] ,owner=directoryDetails.owner, isShared=1, sharedBy=directoryDetails.sharedBy)
        rvalue = copyFile(fileData)

    return rvalue

def shareFile(flieDetails):
    try:
        userdata={}
        userdata["email"] = flieDetails.owner
        userdata["name"] = flieDetails.owner
        user_info = retrieveUserInfo(userdata)
        if user_info == None:
            createUserInfo(userdata)
            createDefaultDirectory(userdata)

        newDirectoryName = str(flieDetails.owner)+'/'+ 'Shared/'
        directoryNewDetails = Directory(parent=flieDetails.owner+'/', dirname=newDirectoryName, size=0, owner=flieDetails.owner, isShared=1, sharedBy='')
        rvalue=addNewDirectory(directoryNewDetails)
        #print(flieDetails.parent.split('/'))
        filedir=flieDetails.parent.split('/')
        filedirlen = len(filedir)
        creatednewdir = newDirectoryName
        #print(filedir[filedirlen-2])
        createddirdetails = directoryNewDetails

        a=2
        while a < filedirlen-1:
            createddirdetails.sharedBy = flieDetails.sharedBy
            createddirdetails.isShared = 1
            createddirdetails.parent = creatednewdir
            creatednewdir = creatednewdir+filedir[a]+"/"
            createddirdetails.dirname = creatednewdir
            rvalue=addNewDirectory(createddirdetails)

        thisFileName = flieDetails.filename.split(newDirectoryName)
        thisFileNameval= flieDetails.sharedBy+'/'+thisFileName[1]
        fileData = File(parent=flieDetails.parent, filename=thisFileNameval ,type=flieDetails.type, size=flieDetails.size, time=flieDetails.time ,owner=flieDetails.owner, isShared=1, sharedBy=flieDetails.sharedBy)
        rvalue = copyFile(fileData)

    except ValueError as exc:
        print(exc)
    return '0'

def copyFile(fileDetails):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    source_bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    source_blob = source_bucket.blob(fileDetails.filename)
    thisFileName = fileDetails.filename.split(fileDetails.sharedBy)
    thisFileNameval= fileDetails.owner+'/Shared'+thisFileName[1]
    fileDetails.filename =thisFileNameval
    destination_bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob_copy = source_bucket.copy_blob(source_blob, destination_bucket, thisFileNameval)


    entity_key = datastore_client.key("file", thisFileNameval)
    entity = datastore.Entity(key=entity_key)
    entity.update(fileDetails.__dict__)
    datastore_client.put(entity)

def moveDirToNewLoc(directoryDetails):
    try:
        #rvalue=addNewDirectory(directoryDetails)
        newmaindir =directoryDetails.dirname.split("/")
        newmaindirlen = len(newmaindir)-2
        newmaindirdata = directoryDetails.parent+newmaindir[newmaindirlen]+'/'
        dirNewDetailsk = Directory(parent=directoryDetails.parent, dirname=newmaindirdata, size=0, owner=directoryDetails.owner, isShared=0, sharedBy="")
        rvalue=addNewDirectory(dirNewDetailsk)
        storage_client = storage.Client(project=local_constants.PROJECT_NAME)
        bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
        blob = bucket.blob(directoryDetails.dirname)

        entity_key = datastore_client.key("Directory", directoryDetails.dirname)
        datastore_client.delete(key=entity_key)
        blob.delete()

        blobDetails = File(parent=directoryDetails.dirname, filename=directoryDetails.dirname,type=None, size=0, time=None,owner=directoryDetails.owner, isShared=0, sharedBy='')
        blobList = getAllDirList(blobDetails)

        for i in blobList["directoryList"]:
            nameDirDt =directoryDetails.dirname.split("/")
            nameDirDtlen = len(nameDirDt)-2
            newParentDirectoryary = i["parent"].split(directoryDetails.dirname)
            newtDirectoryary = i["dirname"].split(directoryDetails.dirname)
            newParentDirectory =directoryDetails.parent+newParentDirectoryary[1]
            newtDirectory = directoryDetails.parent+newtDirectoryary[1]
            newParentDirectory =directoryDetails.parent+nameDirDt[nameDirDtlen]+'/'+newParentDirectoryary[1]
            newtDirectory = directoryDetails.parent+nameDirDt[nameDirDtlen]+'/'+newtDirectoryary[1]
            dirNewDetails = Directory(parent=newParentDirectory, dirname=newtDirectory, size=0, owner=directoryDetails.owner, isShared=0, sharedBy="")
            rvalue = addNewDirectory(dirNewDetails)

            entity_key = datastore_client.key("Directory", i["dirname"])
            datastore_client.delete(key=entity_key)
            storage_client = storage.Client(project=local_constants.PROJECT_NAME)
            bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
            blob = bucket.blob(i["dirname"])
            blob.delete()


        for j in blobList["fileList"]:
            nameDirDt =directoryDetails.dirname.split("/")
            nameDirDtlen = len(nameDirDt)-2
            newParentDirectoryary = j["parent"].split(directoryDetails.dirname)
            newtDirectoryary = j["filename"].split(directoryDetails.dirname)
            newParentDirectory =directoryDetails.parent+newParentDirectoryary[1]
            newtDirectory = directoryDetails.parent+newtDirectoryary[1]
            newParentDirectory =directoryDetails.parent+nameDirDt[nameDirDtlen]+'/'+newParentDirectoryary[1]
            newtDirectory = directoryDetails.parent+nameDirDt[nameDirDtlen]+'/'+newtDirectoryary[1]
            fileData = File(parent=newParentDirectory, filename=newtDirectory, type=j["type"], size=j["size"], time=j["time"] ,owner=directoryDetails.owner, isShared=0, sharedBy="")
            fileMoveTo(fileData, j["filename"])
            oldFileData = File(parent=j["parent"], filename=j["filename"], type=j["type"], size=j["size"], time=j["time"] ,owner=directoryDetails.owner, isShared=0, sharedBy="")
            deleteFile(oldFileData)


    except ValueError as exc:
        print(exc)
    return '1'

def fileMoveTo(fileDetails, oldname):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    source_bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    source_blob = source_bucket.blob(oldname)
    destination_bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob_copy = source_bucket.copy_blob(source_blob, destination_bucket, fileDetails.filename)

    entity_key = datastore_client.key("file", fileDetails.filename)
    entity = datastore.Entity(key=entity_key)
    entity.update(fileDetails.__dict__)
    datastore_client.put(entity)

def moveFileNewLoc(flieDetails):
    try:
        newmaindir =flieDetails.filename.split("/")
        newmaindirlen = len(newmaindir)-1
        newFileData = flieDetails.parent+newmaindir[newmaindirlen]
        print(newFileData)
        fileData = File(parent=flieDetails.parent, filename=newFileData ,type=flieDetails.type, size=flieDetails.size, time=flieDetails.time ,owner=flieDetails.owner, isShared=0, sharedBy="")
        fileMoveTo(fileData, flieDetails.filename)
        deleteFile(flieDetails)

    except ValueError as exc:
        print(exc)
    return '1'


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

                blobDetails = File(parent=user_data["email"]+'/', filename=user_data["email"]+'/',type=None, size=0, time=None,owner=user_data["email"], isShared=0, sharedBy='')
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
            directoryDetails = Directory(parent=currentDirectoryName, dirname=newDirectoryName, size=0,owner=user_data["email"], isShared=0, sharedBy='')
            returnvalue = addNewDirectory(directoryDetails)
            error_message=''
            if returnvalue != 0:
                returnDirectoryName = currentDirectoryName
                error_message = "This folder name is already created."
            else:
                returnDirectoryName = currentDirectoryName

            blobDetails = File(parent=currentDirectoryName, filename=currentDirectoryName,type=None, size=0, time=None,owner=user_data["email"], isShared=0, sharedBy='')
            blobList = getBlobList(blobDetails)
            return render_template("main.html",error_message=error_message, user_data=user_data, directoryList=blobList["directoryList"], fileList=blobList["fileList"], currentDirectoryPath = returnDirectoryName)
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
        directoryDetails = Directory(parent=currentDirectoryName, dirname=currentDirectoryName, size=0,owner=user_data["email"], isShared=0, sharedBy='')
        returnValue = deleteDirectory(directoryDetails)
        if returnValue != 1:
            error_message = "This directory already has some folders or files. So user can't delete this folder"
            blobDetails = File(parent=currentDirectoryName, filename=currentDirectoryName,type=None, size=0, time=None,owner=user_data["email"], isShared=0, sharedBy='')
            blobList = getBlobList(blobDetails)
            return render_template("main.html",error_message=error_message, user_data=user_data, directoryList=blobList["directoryList"], fileList=blobList["fileList"], currentDirectoryPath = currentDirectoryName)
            #return render_template("error.html", error_message=error_message, return_url='/,\',currentDirectoryPath=currentDirectoryName,user_data=user_data)
        return redirect('/')
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route("/deletFile", methods=["GET", "POST"])
def deletFiles():
    user_data =checkUserData();
    if user_data != None:
        currentDirectoryName = request.args.get('fileName')
        fileDetails =File(parent=currentDirectoryName, filename=currentDirectoryName,type=None, size=0, time=None,owner=user_data["email"], isShared=0, sharedBy='')
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
                blobDetails = File(parent=currentDirectoryName, filename=currentDirectoryName,type=None, size=0, time=None,owner=user_data["email"], isShared=0, sharedBy='')
                blobList = getBlobList(blobDetails)
                return render_template("main.html", user_data=user_data, directoryList=blobList["directoryList"], fileList=blobList["fileList"], currentDirectoryPath = currentDirectoryName)
            else:
                error_message = "Page not loaded! User Data is missing"
                return render_template("index.html", user_data=user_data, error_message=error_message)
        except ValueError as exc:
            error_message = "Page not loaded! User Data is missing"
            return render_template("index.html", user_data=user_data, error_message=error_message)



@app.route("/uploadNewFile", methods=["GET", "POST"])
def uploadNewFile():
    user_data =checkUserData();
    if user_data != None:
        try:
            formData = dict(request.form)
            currentDirectoryName = formData.get("currentFileDirectoryPath")
            uploadFileName = formData.get("filename")
            fileData = request.files['filename']
            #if newDirectoryName[len(newDirectoryName) - 1] != '/':
            #newDirectoryName = currentDirectoryName + newDirectoryName + '/'

            fileDetails = File(parent=currentDirectoryName, filename=fileData ,type=None, size=0, time=None,owner=user_data["email"], isShared=0, sharedBy='')
            returnvalue = addNewFile(fileDetails)
            hiddenFileData = {}
            error_message=''
            overwrite = 0
            if returnvalue != 0:
                hiddenFileData["fileData"] = fileData
                hiddenFileData["fileName"] = uploadFileName
                hiddenFileData["currentDirectoryName"]=currentDirectoryName
                error_message = "This file is already exist. Do you want to overwrite?"
                overwrite = 1
            blobDetails = File(parent=currentDirectoryName, filename=currentDirectoryName,type=None, size=0, time=None,owner=user_data["email"], isShared=0, sharedBy='')
            blobList = getBlobList(blobDetails)
            return render_template("main.html",error_message=error_message, user_data=user_data, directoryList=blobList["directoryList"], fileList=blobList["fileList"], currentDirectoryPath = currentDirectoryName, overwrite=overwrite ,hiddenFileData=hiddenFileData)
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route("/downloadFileDetails", methods=["GET", "POST"])
def downloadFileDetails():
    user_data =checkUserData();
    if user_data != None:
        currentFileName = request.args.get('fileName')
        fileDetails =File(parent=currentFileName, filename=currentFileName,type=None, size=0, time=None,owner=user_data["email"], isShared=0, sharedBy='')
        rval = downloadFile(fileDetails)
        return Response(rval,mimetype='application/octet-stream')
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route("/overwriteFile", methods=["GET", "POST"])
def overwriteFile():
    user_data =checkUserData();
    if user_data != None:
        try:
            fileDataDetails = request.args.get('hiddenFileData')
            #fileDataDetails = fileDataDetails.replace("'", "\"")
            #fileDataDetails=json.loads(fileDataDetails)
            #print(fileDataDetails.fileData)
            #print('oooooooooooooooooooooooooooooooooooo')
            #if newDirectoryName[len(newDirectoryName) - 1] != '/':
            #newDirectoryName = currentDirectoryName + newDirectoryName + '/'

            fileDetails = File(parent=fileDataDetails.currentDirectoryName, filename=fileDataDetails.filedata ,type=None, size=0, time=None, owner=user_data["email"], isShared=0, sharedBy='')
            returnvalue = overwriteUploadFile(fileDetails)
            """hiddenFileData = {}
            error_message=''
            overwrite = 0
            if returnvalue != 0:
                hiddenFileData["fileData"] = fileData
                hiddenFileData["fileName"] = uploadFileName = formData.get("filename")
                error_message = "This file is already exist. Do you want to overwrite?"
                overwrite = 1
            blobDetails = File(parent=currentDirectoryName, filename=currentDirectoryName,type=None, size=0, time=None)
            blobList = getBlobList(blobDetails)
            return render_template("main.html",error_message=error_message, user_data=user_data, directoryList=blobList["directoryList"], fileList=blobList["fileList"], currentDirectoryPath = currentDirectoryName, overwrite=overwrite ,hiddenFileData=hiddenFileData)
                """
            error_message = "Page not loaded! User Data is missing"
            return render_template("index.html", user_data=user_data, error_message=error_message)
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)


@app.route('/shareDir' , methods=["GET", "POST"])
def shareDir():
    user_data =checkUserData();
    if not user_data:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=None, error_message=error_message)
    else:
        try:
            formData = dict(request.form)
            currentDirectoryName = formData.get("currentDirectoryPath")
            userId = formData.get("userEmailId")
            hiddendir = formData.get("hiddendir")
            isDirectory = formData.get("isDirectory")
            #print(isDirectory)
            if isDirectory == '1':
                shareddirectory = currentDirectoryName.split(user_data["email"])
                newShareDirectory = userId+ '/Shared'+shareddirectory[1]
                changedDirectory = hiddendir.split(user_data["email"])
                newchangedDirectory = userId+ '/Shared'+changedDirectory[1]
                directoryDetails = Directory(parent=newShareDirectory, dirname=newchangedDirectory, size=0,owner=userId, isShared=1, sharedBy=user_data["email"])
                returnvalue = shareDirectory(directoryDetails)
                error_message=''
                if returnvalue != 0:
                    returnDirectoryName = currentDirectoryName
                    error_message = "This folder is already shared."
                else:
                    returnDirectoryName = currentDirectoryName
            elif isDirectory == '2':
                shareddirectory = currentDirectoryName.split(user_data["email"])
                newShareDirectory = userId+ '/Shared'+shareddirectory[1]
                changedDirectory = hiddendir.split(user_data["email"])
                newchangedDirectory = userId+ '/Shared'+changedDirectory[1]

                fileDetails = File(parent=newShareDirectory, filename=newchangedDirectory,type=None, size=0, time=None,owner=userId, isShared=1, sharedBy=user_data["email"])
                returnvalue = shareFile(fileDetails)
                error_message=''
                if returnvalue != 0:
                    returnDirectoryName = currentDirectoryName
                    error_message = "This File is already shared."
                else:
                    returnDirectoryName = currentDirectoryName
            blobDetails = File(parent=currentDirectoryName, filename=currentDirectoryName,type=None, size=0, time=None,owner=user_data["email"], isShared=0, sharedBy='')
            blobList = getBlobList(blobDetails)
            return render_template("main.html",error_message=error_message, user_data=user_data, directoryList=blobList["directoryList"], fileList=blobList["fileList"], currentDirectoryPath = returnDirectoryName)
        except ValueError as exc:
            error_message = "Page not loaded! User Data is missing"
            return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route('/moveDir' , methods=["GET", "POST"])
def moveDirectory():
    user_data =checkUserData();
    if not user_data:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=None, error_message=error_message)
    else:
        try:
            currentDirName = request.args.get('dirName')
            isDir = request.args.get('isDir')
            currentDirectoryPath =  request.args.get('currentDirectoryPath')
            blobDetails = File(parent=user_data["email"]+"/", filename=user_data["email"]+"/",type=None, size=0, time=None,owner=user_data["email"], isShared=0, sharedBy='')
            blobList = getAllDirList(blobDetails)
            return render_template("movedir.html", user_data=user_data, directoryList=blobList["directoryList"], currentFile = currentDirName, isDir=isDir, currentDirectoryPath=currentDirectoryPath)
        except ValueError as exc:
            error_message = "Page not loaded! User Data is missing"
            return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route('/moveDirectoryto' , methods=["GET", "POST"])
def moveDirectoryto():
    user_data =checkUserData();
    if not user_data:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=None, error_message=error_message)
    else:
        try:
            currentDirectory = request.args.get('currentfile')
            isDir = request.args.get('isDir')
            currentDirectoryPath =  request.args.get('currentDirectoryPath')
            formData = dict(request.form)
            moveLocation = formData.get("movediractory")

            if isDir == '1':
                directoryDetails = Directory(parent=moveLocation, dirname=currentDirectory, size=0,owner=user_data["email"], isShared=0, sharedBy="")
                returnvalue = moveDirToNewLoc(directoryDetails)
                error_message=''
                if returnvalue != 0:
                    returnDirectoryName = currentDirectory
                    error_message = "This folder is successfully moved!"
                else:
                    returnDirectoryName = currentDirectory
            elif isDir == '2':

                fileDetails = File(parent=moveLocation, filename=currentDirectory,type=None, size=0, time=None,owner=user_data["email"], isShared=0, sharedBy="")
                returnvalue = moveFileNewLoc(fileDetails)
                error_message=''
                if returnvalue != 0:
                    returnDirectoryName = currentDirectory
                    error_message = "This File is successfully moved!"
                else:
                    returnDirectoryName = currentDirectory
            #blobDetails = File(parent=moveLocation, filename=moveLocation,type=None, size=0, time=None,owner=user_data["email"], isShared=0, sharedBy='')
            #blobList = getBlobList(blobDetails)
            #return render_template("main.html",error_message=error_message, user_data=user_data, directoryList=blobList["directoryList"], fileList=blobList["fileList"], currentDirectoryPath = moveLocation)
            return redirect('/')
        except ValueError as exc:
            error_message = "Page not loaded! User Data is missing"
            return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route("/goUpDirect", methods=["GET", "POST"])
def goUpDirect():
    user_data =checkUserData();
    if user_data != None:
        try:
            currentDirectoryPath = request.args.get('currentDirectoryPath')
            currentDirectoryPathary = currentDirectoryPath.split("/")
            backcurrentDirectoryPath = currentDirectoryPath.replace(currentDirectoryPathary[len(currentDirectoryPathary)-2],"*/*")
            newcurrentDirectoryName = backcurrentDirectoryPath.split("*/*/")[0]

            blobDetails = File(parent=newcurrentDirectoryName, filename=newcurrentDirectoryName,type=None, size=0, time=None,owner=user_data["email"], isShared=0, sharedBy='')
            blobList = getBlobList(blobDetails)
            return render_template("main.html",error_message="", user_data=user_data, directoryList=blobList["directoryList"], fileList=blobList["fileList"], currentDirectoryPath = newcurrentDirectoryName)
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)



@app.route("/singnout", methods=["GET", "POST"])
def signOut():
    return render_template("index.html", signoutdata="true")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
