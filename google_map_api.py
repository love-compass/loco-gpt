# -*- coding: utf-8 -*-
"""GOOGLE MAP API.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cfqoHY56jkKx2hPT20akpORBZZzN3i6s
"""

import requests
import cv2
from google.colab.patches import cv2_imshow
import numpy as np
import urllib.request
import json

key = "AIzaSyAcRNmLl5V8WpQDzJCn2zorQLh6FXeV9Dw"

def googlemap_search(place, key):
  url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + place + "&inputtype=textquery&" + "fields=formatted_address%2Cphotos%2Crating%2Ctypes" + "&key=" + key
  payload={}
  headers = {}
  response = requests.request("GET", url, headers=headers, data=payload)
  
  return response.text

def googlemap_photo(photo_reference, key):
  photo_url = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=" + photo_reference + "&key=" + key #width 숫자 크기 조절로 파일 크기 조정 가능
  photo = requests.get(photo_url)
  img = Image.open(BytesIO(photo.content))
  return img

test=json.loads(googlemap_search("Starbucks Bongeunsa Station Branch", key))

#주소 = test["candidates"][0]["formatted_address"]
photo_re = test["candidates"][0]["photos"][0]["photo_reference"]

googlemap_photo(photo_re, key)