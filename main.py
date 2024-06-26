import cv2
import os
import pickle
import numpy as np
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://.....enter database url",
    'storageBucket':"add address"
})

bucket = storage.bucket()
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

#importing the mode images to a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList= []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))
#print(len(imgModeList)) #will print 4


#IMPORT THE ENCODING FILE
file = open('EncodeFile.p','rb')
encodeListKnownWithIds =pickle.load(file)
file.close()
encodeListKnown,studentIds = encodeListKnownWithIds
#print(studentIds)
print("Encode file loaded")

modeType=0
counter = 0
id = -1
imgStudent = []


#camera operning operations
while True:
    success, img = cap.read()

    #squeezing image to smaller size
    imgS = cv2.resize(img,(0, 0),None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)


    #overlapping the background and my webcam
    #maintaing the stating-end points and dimensions of webcam and background
    imgBackground[162:162+480,55:55+640] = img

    #adding the modes to background
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:

        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            # getting the index of matched images based on distance
            matchIndex = np.argmin(faceDis)
            #print("Match Index",matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4,  y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground,bbox,rt=0)
                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading",(275,400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType=1

        if counter != 0:
            if counter ==  1:
                #Get the data
                studentInfo = db.reference(f'Students/{id}').get()
                #will print the matched student data in terminal
                print(studentInfo)

                #Get the Images from the storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

                #update the data--attendance count
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                  "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                #print(secondsElapsed)

                #timer to stop repetitive marking
                if secondsElapsed > 60:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] +=1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType=3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:
                #check to we need to update or attendance is taken now only
                if 20<counter<30:
                    modeType=2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                #to make counter work to show active and already mark transition
                if counter<=20:
                    #to put the info of identified student over the background image
                    cv2.putText(imgBackground,str(studentInfo['total_attendance']),(850,125),#these are (x,y)dimenssion point
                                cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)


                    (w,h),_ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)

                    #width of image use for background in 414
                    offset= (414-w)//2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445),  # these are (x,y)dimenssion point
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 2)

                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),  # these are (x,y)dimenssion point
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

                    cv2.putText(imgBackground, str(id), (1006, 493),  # these are (x,y)dimenssion point
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

                    cv2.putText(imgBackground, str(studentInfo['standing']), (910,625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    cv2.putText(imgBackground, str(studentInfo['Duration']), (1025, 625),  # these are (x,y)dimenssion point
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    cv2.putText(imgBackground, str(studentInfo['start_year']), (1125, 625),  # these are (x,y)dimenssion point
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    #putting matched student image over background
                    imgBackground[175:175+216,909:909+216] = imgStudent


            counter+=1

            #resetting the data to marks new attendance
            if counter>=30:
                counter = 0
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        modeType = 0
        counter = 0


    # cv2.imshow("Webcam for Attendance", img)

    cv2.imshow("Face Attendance", imgBackground)
    if cv2.waitKey(1) & 0xFF == ord('q'): #q will stop the all windows
        break

cap.release()
cv2.destroyAllWindows()
