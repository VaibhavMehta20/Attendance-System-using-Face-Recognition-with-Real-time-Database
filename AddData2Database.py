import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://realtime-face-attendancesystem-default-rtdb.firebaseio.com/"})

ref=db.reference('Students')


data = {
    "1":
    {
        "Name":"Abhinav Adarsh",
        "Major": "Machine learning",
        "Starting_year":2021,
        "Total_Attendance":6,
        "Year":3,
        "last_attendance_time":"2023-06-13 00:54:34"

    },
    "2":
    {
        "Name":"Elon Musk",
        "Major": "CEO",
        "Starting_year":2008,
        "Total_Attendance":125,
        "Year":16,
        "last_attendance_time":"2023-06-13 00:54:34"

    },

    "3":
    {
        "Name":"Vinay Yadav",
        "Major": "Embedded System",
        "Starting_year":2021,
        "Total_Attendance":6,
        "Year":3,
        "last_attendance_time":"2023-06-13 00:54:34"

    },

    "4":
    {
        "Name":"Chamanjot",
        "Major": "Civil Engineer",
        "Starting_year":2021,
        "Total_Attendance":6,
        "Year":3,
        "last_attendance_time":"2023-06-13 00:54:34"

    }

}




for key,values in data.items():
    ref.child(key).set(values)


