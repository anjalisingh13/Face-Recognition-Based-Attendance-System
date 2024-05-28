import cv2
import face_recognition
import pickle
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://facerecognitionattendanc-509cb-default-rtdb.firebaseio.com/",
    'storageBucket':"facerecognitionattendanc-509cb.appspot.com"
})

#importing the student images
folderPath = 'Images'
pathList = os.listdir(folderPath)
imgList= []
studentIds=[]
print(pathList) #print images name
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    studentIds.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob=bucket.blob(fileName)
    blob.upload_from_filename(fileName)




    #print(path)  # will print with png
    #print(os.path.splitext(path)[0])
#print(len(imgList)) #will print 3

print(studentIds)


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

print("Encoding Started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown,studentIds]
print("Encoding completed")


file=open("EncodeFile.p",'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()

