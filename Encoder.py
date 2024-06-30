import cv2
import face_recognition
import pickle
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://realtime-face-attendancesystem-default-rtdb.firebaseio.com/",
    'storageBucket':"realtime-face-attendancesystem.appspot.com"
    })



#Importing the Images
folderpath='Images'
modeList=os.listdir(folderpath)
imgList=[]
StudentIds=[]
for path in modeList:
    img=cv2.imread(os.path.join(folderpath,path))
    print(os.path.join(folderpath,path))
    # print(img.shape)
    imgList.append(img)
    img=cv2.resize(img,(216,216))
    # print(img.shape)
    StudentIds.append(os.path.splitext(path)[0])

    #Uploading the Images to firebase Storage:
    fileName = f'{folderpath}/{path}'
    # print(fileName)
    bucket = storage.bucket()
    blob=bucket.blob(fileName)
    blob.upload_from_filename(fileName)



#Encoding Part:

def findEncoding(imageslist):
    encode_list=[]
    for img in imageslist:
        cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode=face_recognition.face_encodings(img)[0]
        encode_list.append(encode)


    return encode_list

print("Encoding Started..........")
encodelist_Known=findEncoding(imgList)
encoderlistKnow_withIDS=[encodelist_Known,StudentIds]
print("Encoding Completed")


file = open("EncodeFile.pickle",'wb') 
pickle.dump(encoderlistKnow_withIDS,file)
file.close()
print("Encoder list Saved in EncoderFile")
