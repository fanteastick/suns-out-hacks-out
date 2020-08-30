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
            for img_path in temp_set:
                self.filter_list[len(self.filter_list)-1].append(Image.open(img_path))
        
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
        
    # adds filter given a numpy.ndarray type image (OpenCV)
    def addFilter(self, image, filtCat, filtN):  
        ret, buf = cv2.imencode('.png', image)
        stream = io.BytesIO(buf)
        detected_faces = self.face_client.face.detect_with_stream(stream, return_face_landmarks = True, return_face_attributes = ["emotion"])
        img = Image.open(stream)
        self.addFilterHelper(img, detected_faces, filtCat, filtN)
        # Invert colors back to normal
        open_cv_image = np.array(img)[:, :, ::-1]
        return open_cv_image
    
    # adds filter given an image URL
    def addFilterURL(self, imageURL, filtCat, filtN=0):  
        detected_faces = self.face_client.face.detect_with_url(imageURL, return_face_landmarks = True, return_face_attributes = ["emotion"])
        response = requests.get(imageURL)
        img = Image.open(BytesIO(response.content))
        self.addFilterHelper(img, detected_faces, filtCat, filtN)
        # Invert colors back to normal
        open_cv_image = np.array(img)[:, :, ::-1]
        return open_cv_image
    
    def addFilterHelper(self, img, detected_faces, filtCat, filtN=0):
        for face in detected_faces:
            emote_ident = FilterEmotions(face)
            top_emotion = emote_ident.get_top_emotion_name()
            top_emotion_id = emotion_mapping[top_emotion]
            # Assumes we have 8 folders for the different the 8 different emotions
            filt = self.filter_list[top_emotion_id][filtN]
            
            landmarks = face.face_landmarks
            x = landmarks.eye_right_top.x-landmarks.eye_left_top.x
            y = landmarks.eye_right_top.y-landmarks.eye_left_top.y
            tilt = -math.atan(y/x)
            tilt = tilt / np.pi * 180.0
            f = filt.rotate(tilt, expand=1)
            size = self.getGlassesSize(face, f)
            f = f.resize(size, resample=PIL.Image.ANTIALIAS)
            x_pos, y_pos = self.getEyePos(face, tilt, size)
            img.paste(f, (x_pos, y_pos), f)
