import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://facerecognitionattendanc-509cb-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students') #this will create the students directory in database

#giving name and other info to the pictures in folder
data = {
    "963852": {
        "name" : "Elon Musk",
        "major": "Qualified",
        "stary_year":1990,
        "total_attendance":6,
        "standing":"B",
        "Duration":4,
        "last_attendance_time":"2024-02-08 12:20:00"
    },
    "102030": {
        "name": "Mr. Narendra Modi",
        "major": "Prime Minister",
        "start_year": 2014,
        "total_attendance": 100,
        "standing": "A++",
        "Duration": 20,
        "last_attendance_time": "2024-02-08 12:20:00"
    },
    "133780": {
        "name": "Kunwar Abhishek Singh",
        "major": "CSE",
        "start_year": 2018,
        "total_attendance": 100,
        "standing": "A++",
        "Duration": 4,
        "last_attendance_time": "2024-02-09 12:20:00"
    }
}

for key,value in data.items():
    ref.child(key).set(value)