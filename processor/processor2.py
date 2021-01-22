import logging
import os
from datetime import datetime
from enum import Enum
import pandas as pd

import requests
from requests import RequestException, Timeout
import processor.exceptions

import base64
import cv2 
import numpy as np
import mtcnn
from io import BytesIO
from PIL import Image

from processor.architecture import *
from processor.train_v2 import normalize,l2_normalizer
from scipy.spatial.distance import cosine
from tensorflow.keras.models import load_model
import pickle

logger = logging.getLogger(__name__)
vectors_data = None
FULLTEXTKEY = "fulltext"

def load_pickle(path):
    with open(path, 'rb') as f:
        encoding_dict = pickle.load(f)
    return encoding_dict

face_encoder = InceptionResNetV2()
path_m = "./processor/model/facenet_keras_weights.h5"
face_encoder.load_weights(path_m)
logger.debug(f"Carga keras weight")
face_detector = mtcnn.MTCNN()
logger.debug(f"Carga mtcnn")
encodings_path = './processor/encodings/encodings.pkl'
encoding_dict = load_pickle(encodings_path)
logger.debug(f"Carga encodings")


class SupportedExtensions(Enum):
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    PDF = "pdf"


class DocType(Enum):
    Acta = "acta"
    Obra = "obra"

    @staticmethod
    def from_value(value):
        # noinspection PyTypeChecker
        value_to_enum = {x.value: x for x in list(DocType)}
        return value_to_enum[value]

confidence_t=0.99
recognition_t=0.4
required_size = (160,160)



def get_face(img, box):
    x1, y1, width, height = box
    x1, y1 = abs(x1), abs(y1)
    x2, y2 = x1 + width, y1 + height
    face = img[y1:y2, x1:x2]
    return face, (x1, y1), (x2, y2)

def get_encode(face_encoder, face, size):
    face = normalize(face)
    face = cv2.resize(face, size)
    encode = face_encoder.predict(np.expand_dims(face, axis=0))[0]
    return encode

def detect(img ,detector,encoder,encoding_dict):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = detector.detect_faces(img_rgb)
    for res in results:
        logger.debug(f"Run results")
        if res['confidence'] < confidence_t:
            continue
        face, pt_1, pt_2 = get_face(img_rgb, res['box'])
        #"""
        encode = get_encode(encoder, face, required_size)
        encode = l2_normalizer.transform(encode.reshape(1, -1))[0]
        name = 'unknown'

        
        distance = float("inf")
        for db_name, db_encode in encoding_dict.items():
            dist = cosine(db_encode, encode)
            if dist < recognition_t and dist < distance:
                name = db_name
                distance = dist

        if name == 'unknown':
            cv2.rectangle(img, pt_1, pt_2, (0, 0, 255), 2)
            cv2.putText(img, name, pt_1, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
        else:
            cv2.rectangle(img, pt_1, pt_2, (0, 255, 0), 2)
            cv2.putText(img, name + f'__{distance:.2f}', (pt_1[0], pt_1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 200, 200), 2)
        
        #"""
    return name 


def processa(filelist, doc_type, extract_meta=False, wdir="."):

    required_shape = (160,160)


    result = []
    logger.debug(f"wdir: {wdir}")

    
    #s result = list(zip(result, [os.path.join(wdir, x) for x in docx_filenames], messages))

    im = Image.open(BytesIO(base64.b64decode(filelist[0]["filebase64"])))
    savepath = wdir + '/elondecode.png'
    im.save(savepath, 'PNG')
    im = cv2.imread(savepath)
    position = detect(im , face_detector , face_encoder , encoding_dict)
    """
    savepath = wdir + '/output.jpg'
    cv2.imwrite(savepath, position)
    with open(savepath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()) 
    """
    return position

