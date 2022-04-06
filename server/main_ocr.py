import os
import easyocr
import cv2

IMAGE_PATH = 'https://blog.aspose.com/wp-content/uploads/sites/2/2020/05/Perform-OCR-using-C.jpg'
reader = easyocr.Reader(['en'])
result = reader.readtext(IMAGE_PATH)
print (result)