import cv2
import os
import pickle
import numpy as np
import face_recognition
import cvzone
import numpy as np
from datetime import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://realtime-face-attendancesystem-default-rtdb.firebaseio.com/",
    'storageBucket':"realtime-face-attendancesystem.appspot.com"
    })

bucket=storage.bucket()


cap=cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

img_Background=cv2.imread("Resources/background.png")


#Importing the Img stoored in Modes into List..
folderModepath='Resources/Modes'
modePathList=os.listdir(folderModepath)
imgModeList=[]
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModepath,path)))
# print(len(imgModeList))


#Load the Encoding File:
print("Loading Encode File....")
file=open('EncodeFile.pickle', 'rb')
encoderlistKnow_withIDS=pickle.load(file)
encodelist_Known , StudentIds =encoderlistKnow_withIDS  
print("Loading Encoded File Completed")
print(StudentIds)



mode_type=0
counter=0
id=0
Student_img=[]
while True:
    success , img = cap.read()

    imgS=cv2.resize(img, (0,0), None , 0.25, 0.25)
    imgS=cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

    facecurr_Frame= face_recognition.face_locations(imgS)
    encodercurr_Frame =face_recognition.face_encodings(imgS,facecurr_Frame)

    img_Background[162:162+480,55:55+640]=img
    img_Background[44:44+633,808:808+414]=imgModeList[mode_type]



    if facecurr_Frame:
        for encodeFace , faceLoc in zip(encodercurr_Frame, facecurr_Frame):
            matches= face_recognition.compare_faces(encodelist_Known, encodeFace)
            facedis=face_recognition.face_distance(encodelist_Known,encodeFace)
            # print("matches",matches)
            # print("facedis", facedis)

            match_index= np.argmin(facedis)

            if matches[match_index]:
                # print("Face Detected")
                y1 , x2 , y2 , x1 = faceLoc
                y1 , x2 , y2 , x1 = y1*4 , x2*4 , y2*4 , x1*4 
                bbox = 55 + x1, 162 + y1 , x2 - x1 , y2 - y1
                img_Background=cv2.rectangle(img_Background, bbox , color=(255,255,255), thickness=1)

                id=StudentIds[match_index]
                if counter==0:
                    cvzone.putTextRect(img_Background,"Loading...",(275,400))
                    cv2.imshow('Face Recognition',img_Background)
                    cv2.waitKey(1)
                    counter=1
                    mode_type=1
        
        if counter!=0:
            if counter==1:
                #Extracting the data form Firebase Database:
                stud_info=db.reference(f'Students/{id}').get()

                #Extracting the Images from Firebase Storage:
                blob=bucket.get_blob(f'Images/{id}.jpeg')
                array=np.frombuffer(blob.download_as_string(), np.uint8)
                Student_img=cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                Student_img.resize(216,216,3)

                #Updateb the data of Attendance:
                datetime_object= datetime.strptime(stud_info['last_attendance_time'],
                                                    "%Y-%m-%d %H:%M:%S")
                
                Seconds_Elapsed=(datetime.now()-datetime_object).total_seconds()
                print(Seconds_Elapsed)

                if Seconds_Elapsed>30:
                    ref=db.reference(f'Students/{id}')
                    stud_info['Total_Attendance']+=1
                    ref.child('Total_Attendance').set(stud_info['Total_Attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                else:
                    mode_type=3
                    counter=0
                    img_Background[44:44+633,808:808+414]=imgModeList[mode_type]


            if mode_type !=3:

                if 10<counter<20:
                    mode_type=2

                img_Background[44:44+633,808:808+414]=imgModeList[mode_type]


                if counter<=10:

                    cv2.putText(img_Background,str(stud_info['Total_Attendance']),
                                (861,125),cv2.FONT_HERSHEY_COMPLEX,0.9,(255,255,255),1)    
                    cv2.putText(img_Background,str(stud_info['Major']),
                                (1006,550),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1) 
                    cv2.putText(img_Background,str(id),
                                (1006,493),cv2.FONT_HERSHEY_COMPLEX,0.6,(255,255,255),1)    
                    cv2.putText(img_Background,str(stud_info['Year']),
                                (1025,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(191,64,191),1)
                    cv2.putText(img_Background,str(stud_info['Starting_year']),
                                (1125,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(191,64,191),1) 
                    
                    (w,h), _ = cv2.getTextSize(stud_info['Name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset=(414-w)//2
                    cv2.putText(img_Background,str(stud_info['Name']),
                                (808+offset,445),cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1) 
                    img_Background[175:175+216,909:909+216]=Student_img

                
                counter+=1

                if counter>=20:
                    counter=0
                    mode_type=0
                    stud_info=[]
                    Student_img=[]
                    img_Background[44:44+633,808:808+414]=imgModeList[mode_type]    

    else:
        mode_type=0
        counter=0


    # cv2.imshow('Webcam',img)
    cv2.imshow('Face Recognition',img_Background)
    if (cv2.waitKey(1) & 0xff==ord('q')):
        break

    
