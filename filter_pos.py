import cv2
import numpy as np
import math
import pathlib
import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
import PIL
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, OperationStatusType

from emotions import FilterEmotions, emotion_mapping

class faceFilter():
    def __init__(self):
        KEY = "e375844ce0d2420db056914e11ccee2f"
        ENDPOINT = "https://facefilters.cognitiveservices.azure.com/"
        self.face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))
        # assumes filters are in a folder named "filters" in the current folder
        # and that they are further separated into subfolders
        path_to_file = pathlib.Path().cwd() / "filters"
        list_of_paths = glob.glob(os.path.join(path_to_file, '*'))
        self.filter_list = []
        for file in list_of_paths:
            temp_set = glob.glob(os.path.join(file, '*.png'))
            self.filter_list.append([])
            for i in range(len(temp_set)):
                img_path = temp_set[i]
                if img_path.find("2") != -1:
                    self.filter_list[len(self.filter_list)-1][i-1].addFilter(Image.open(img_path))
                else:
                    filt = filterImage(Image.open(img_path))
                    self.filter_list[len(self.filter_list)-1].append(filt)
        
    # returns approximate headgear position
    def getHeadPos(self, face, tilt, size):
        landmarks = face.face_landmarks
        if tilt >= 0:
            x_offset = landmarks.eyebrow_right_outer.x+(landmarks.eye_right_outer.x-landmarks.eye_right_inner.x)
            x_pos = x_offset-size[0]
            y_offset = landmarks.eyebrow_left_outer.y
            y_pos = y_offset-size[1]
        else:
            x_offset = landmarks.eyebrow_left_outer.x-(landmarks.eye_left_inner.x-landmarks.eye_left_outer.x)
            x_pos = x_offset
            y_offset = landmarks.eyebrow_right_outer.y
            y_pos = y_offset-size[1]
        return int(x_pos), int(y_pos)
    
    # returns relative headband size
    def getHeadbandSize(self, face, filt):
        landmarks = face.face_landmarks
        f_size = filt.size
        x_size = face.face_rectangle.width+(landmarks.eye_left_inner.x-landmarks.eye_left_outer.x)
        size = (int(x_size), int(x_size/f_size[0] * f_size[1]))
        return size
    
    # returns approximate eyewear position
    def getEyePos(self, face, tilt, size):
        landmarks = face.face_landmarks
        if tilt >= 0:
            x_offset = landmarks.eyebrow_right_outer.x+(landmarks.eye_right_outer.x-landmarks.eye_right_inner.x)
            x_pos = x_offset-size[0]
            y_offset = landmarks.nose_left_alar_out_tip.y
            y_pos = y_offset-size[1]
        else:
            x_offset = landmarks.eyebrow_left_outer.x-(landmarks.eye_left_inner.x-landmarks.eye_left_outer.x)
            x_pos = x_offset
            y_offset = landmarks.nose_right_alar_out_tip.y
            y_pos = y_offset-size[1]
        return int(x_pos), int(y_pos)
    
    # returns relative glasses size
    def getGlassesSize(self, face, filt):
        landmarks = face.face_landmarks
        f_size = filt.size
        x_size = face.face_rectangle.width+(landmarks.eye_left_inner.x-landmarks.eye_left_outer.x)
        size = (int(x_size), int(x_size/f_size[0] * f_size[1]))
        return size
    
    # returns approximate neck accessory position
    def getNeckPos(self, face, tilt, size):
        landmarks = face.face_landmarks
        if tilt >= 10:
            x_offset = landmarks.eyebrow_right_outer.x+(landmarks.nose_left_alar_out_tip.x-landmarks.eye_left_outer.x)
            x_pos = x_offset-size[0]
            y_offset = landmarks.under_lip_bottom.y+(landmarks.under_lip_bottom.y-landmarks.eye_left_outer.y)
            y_pos = y_offset-size[1]
        elif tilt >= 0:
            x_offset = landmarks.eyebrow_right_outer.x
            x_pos = x_offset-size[0]
            y_offset = landmarks.under_lip_bottom.y+(landmarks.under_lip_bottom.y-landmarks.eye_left_outer.y)
            y_pos = y_offset-size[1]
        elif tilt > -10:
            x_offset = landmarks.eyebrow_left_outer.x
            x_pos = x_offset
            y_offset = landmarks.under_lip_bottom.y+(landmarks.under_lip_bottom.y-landmarks.eye_right_outer.y)
            y_pos = y_offset-size[1]
        else:
            x_offset = landmarks.eyebrow_left_outer.x-(landmarks.eye_right_outer.x-landmarks.nose_right_alar_out_tip.x)
            x_pos = x_offset
            y_offset = landmarks.under_lip_bottom.y+(landmarks.under_lip_bottom.y-landmarks.eye_right_outer.y)
            y_pos = y_offset-size[1]
        return int(x_pos), int(y_pos)
    
    # returns relative necklace size
    def getNecklaceSize(self, face, filt):
        landmarks = face.face_landmarks
        f_size = filt.size
        x_size = landmarks.eyebrow_right_outer.x-landmarks.eyebrow_left_outer.x
        size = (int(x_size), int(x_size/f_size[0] * f_size[1]))
        return size
    
    def getEarsPos(self, face, tilt, size):
        landmarks = face.face_landmarks
        if tilt >= 0:
            x_offset = landmarks.eyebrow_right_outer.x+(landmarks.pupil_right.x-landmarks.eyebrow_left_inner.x)
            x_pos = x_offset-size[0]
            y_offset = landmarks.eye_left_outer.y+(landmarks.eye_left_outer.y-landmarks.eye_right_outer.y)
            y_pos = y_offset-size[1]
        else:
            x_offset = landmarks.eyebrow_left_outer.x-(landmarks.pupil_right.x-landmarks.eyebrow_left_inner.x)
            x_pos = x_offset
            y_offset = landmarks.eye_right_outer.y-(landmarks.eye_right_outer.y-landmarks.eye_left_outer.y)
            y_pos = y_offset-size[1]
        return int(x_pos), int(y_pos)
    
    def getEarsSize(self, face, filt):
        landmarks = face.face_landmarks
        f_size = filt.size
        x_size = (landmarks.eyebrow_right_outer.x-landmarks.eyebrow_left_outer.x)*1.65
        size = (int(x_size), int(x_size/f_size[0] * f_size[1]))
        return size
    
    def getMouthPos(self, face, tilt, size):
        landmarks = face.face_landmarks
        return int(landmarks.mouth_left.x), int(landmarks.mouth_left.y)
    
    def getMouthSize(self, face, filt):
        landmarks = face.face_landmarks
        f_size = filt.size
        x_size = (landmarks.mouth_right.x-landmarks.mouth_left.x)
        size = (int(x_size), int(x_size/f_size[0] * f_size[1]))
        return size
    
    def getNosePos(self, face, tilt, size):
        landmarks = face.face_landmarks
        return int(landmarks.nose_left_alar_top.x), int(landmarks.nose_left_alar_top.y)
    
    def getNoseSize(self, face, filt):
        landmarks = face.face_landmarks
        f_size = filt.size
        x_size = (landmarks.nose_right_alar_out_tip.x-landmarks.nose_left_alar_out_tip.x)
        size = (int(x_size), int(x_size/f_size[0] * f_size[1]))
        return size
    
    
    def assignPos(self, face, tilt, size, key):
        if key == 0:
            return self.getEarsPos(face, tilt, size)
        elif key == 1:
            return self.getEyePos(face, tilt, size)
        elif key == 2:
            return self.getHeadPos(face, tilt, size)
        elif key == 3:
            return self.getMouthPos(face, tilt, size)
        elif key == 4:
            return self.getNeckPos(face, tilt, size)
        elif key == 5:
            return self.getNosePos(face, tilt, size)
        
    
    def assignSize(self, face, filt, key):
        if key == 0:
            return self.getEarsSize(face, filt)
        elif key == 1:
            return self.getGlassesSize(face, filt)
        elif key == 2:
            return self.getHeadbandSize(face, filt)
        elif key == 3:
            return self.getMouthSize(face, filt)
        elif key == 4:
            return self.getNecklaceSize(face, filt)
        elif key == 5:
            return self.getNoseSize(face, filt)
        
    # adds filter given a numpy.ndarray type image (OpenCV)
    def addFilterURL(self, imageURL, ind, getEmotion=False):  
        filtN = 0
        if ind = 0:
            filtCat = 0
        elif ind = 1:
            filtCat = 1
        elif ind = 2:
            filtCat = 2
        elif ind = 3:
            filtCat = 2
            filtN = 1
        elif ind = 4:
            filtCat = 3
        elif ind = 5:
            filtCat = 4:
        elif ind = 6:
            filtCat = 5
        ret, buf = cv2.imencode('.png', image)
        stream = io.BytesIO(buf)
        detected_faces = self.face_client.face.detect_with_stream(stream, return_face_landmarks = True, return_face_attributes = ["emotion"])
        img = Image.open(stream)
        top_emotions = self.addFilterHelper(img, detected_faces, filtCat, filtN, getEmotion)
        # Invert colors back to normal
        open_cv_image = np.array(img)[:, :, ::-1]
        return open_cv_image, top_emotions
    
    # adds filter given an image URL
    def addFilterURL(self, imageURL, filtCat, filtN, getEmotion=False):  
        detected_faces = self.face_client.face.detect_with_url(imageURL, return_face_landmarks = True, return_face_attributes = ["emotion"])
        response = requests.get(imageURL)
        img = Image.open(BytesIO(response.content))
        top_emotions = self.addFilterHelper(img, detected_faces, filtCat, filtN, getEmotion)
        # Invert colors back to normal
        open_cv_image = np.array(img)[:, :, ::-1]
        return open_cv_image, top_emotions
    
    def addFilterHelper(self, img, detected_faces, filtCat, filtN, getEmotion):
        top_emotions = []

        for face in detected_faces:
            if getEmotion:
                emote_ident = FilterEmotions(face)
                top_emotion = emote_ident.get_top_emotion_name()
                top_emotions.append(top_emotion)
                top_emotion_id = emotion_mapping[top_emotion]
                # Assumes we have 8 folders for the different the 8 different emotions
                filt_list = self.filter_list[top_emotion_id][filtN].getFilters()
            else:
                filt_list = self.filter_list[filtCat][filtN].getFilters()
            
            for i in range(len(filt_list)):
                filt = filt_list[i]
                landmarks = face.face_landmarks
                x = landmarks.eye_right_top.x-landmarks.eye_left_top.x
                y = landmarks.eye_right_top.y-landmarks.eye_left_top.y
                tilt = -math.atan(y/x)
                tilt = tilt / np.pi * 180.0
                f = filt.rotate(tilt, expand=1)
                if i == 1:
                    if filtCat == 5:
                        size = self.assignSize(face, f, 2)
                elif getEmotion:
                    size = self.assignSize(face, f, 1)
                else:
                    size = self.assignSize(face, f, filtCat)
                f = f.resize(size, resample=PIL.Image.ANTIALIAS)
                if i == 1:
                    if filtCat == 5:
                        x_pos, y_pos = self.assignPos(face, tilt, size, 2)
                elif getEmotion:
                    x_pos, y_pos = self.assignPos(face, tilt, size, 1)
                else:
                    x_pos, y_pos = self.assignPos(face, tilt, size, filtCat)
                img.paste(f, (x_pos, y_pos), f)
        return top_emotions
    
class filterImage():
    def __init__(self, image):
        self.image_list = [image]
    
    def addFilter(self, image):
        self.image_list.append(image)
    
    def getFilters(self):
        return self.image_list
