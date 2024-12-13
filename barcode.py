import cv2 
from pyzbar.pyzbar import decode
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import undetected_chromedriver as webdriver
import re
from openai import OpenAI
import os
import requests
import subprocess
import json
# cap = cv2.VideoCapture(0)

# storedBarcodes = []

# while cap.isOpened():
#     success,frame = cap.read()
    
#     # get mirror image
#     frame  = cv2.flip(frame,1)

#     # detect the barcode 
#     detectedBarcode = decode(frame)
    
#     # codes in barcode 
#     for barcode in detectedBarcode:
#         # if barcode is not blank 
#         if barcode.data != "" and barcode.data not in storedBarcodes:
#             storedBarcodes.append(re.findall(r'\d+', str(barcode.data)))
#             print(storedBarcodes)
#     cv2.imshow('Scan Barcode' , frame)
#     # close webcam once barcode scanned
#     if len(storedBarcodes) == 1:
#         cap.release()
#         cv2.destroyAllWindows()
    
#     if cv2.waitKey(1) == ord('q'):
#         break

# OPEN https://go-upc.com/search?q=0030772101254 replacing numbers at end with barcode results
# def getData(barcode):
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--use_subprocess")

#     driver = webdriver.Chrome(options=chrome_options)

#     driver.get(f"https://go-upc.com/search?q={barcode}")
#     brandName = driver.find_element(By.XPATH, '//*[@id="resultPageContainer"]/div/div[1]/div[1]/table/tbody/tr[4]/td[2]').text
#     print(brandName)
#     ingredients = (driver.find_element(By.XPATH, '//*[@id="resultPageContainer"]/div/div[1]/div[3]/span').text).split(',')
#     print(ingredients)
# #getData("0030772101254")

#response = subprocess.check_output(['curl', '-s', f"https://go-upc.com/api/v1/code/{storedBarcodes[0][0]}?key=&format=true"])
response = subprocess.check_output(['curl', '-s', f"https://go-upc.com/api/v1/code/0030772101254?key=&format=true"])
jsonResponse = json.loads(response.decode('utf-8'))

cleaned = []

for key in jsonResponse['product']:
    cleaned.append(jsonResponse['product'][key])

productName = cleaned[0]
productDescription = cleaned[1]
productIngredients = []
print(cleaned)
print(cleaned[8])

if isinstance(cleaned[8], dict):
    for item in cleaned[8]:
        productIngredients.append(cleaned[8]['text'].split(','))
else:
    print("PRODUCT INGREDIENTS CANNOT BE ACCESSED")

OPENAI_API_KEY = ""

# #OPENROUTERAPI
OPENROUTER_API_KEY = ""

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=""
)

scores = []

def getScore(ingredient):
    completion = client.chat.completions.create(
    model="meta-llama/llama-3.2-11b-vision-instruct:free",
    messages=[
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "You are a environmental assisant that deems ingredients of a given item environmentally friendly or not. You will not be coding.\
                Given an ingredient, look into its background and see if its environmentally safe or not. Give this ingredient a score from 0-100, with 0\
                    being not environmentally friendly, and 100 being environmentally friendly. Keep in mind that Water scores 100.\
                        Just output the numerical 0-100 score ONCE please (without explanation)."
            },
            {
            "type": "text",
            "text": f"{ingredient}r"
            },  
        ]
        }
    ]
    )

    numbers = ""

    for char in completion.choices[0].message.content:
        if char.isdigit():
            numbers += char

    scores.append(int(numbers))

for ingredient in productIngredients[0]:
    getScore(ingredient)

print(scores)

average = round(sum(scores) / len(scores), 1)

print(average)