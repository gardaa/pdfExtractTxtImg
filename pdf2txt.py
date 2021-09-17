from genericpath import isfile
from io import StringIO
from dotenv.main import load_dotenv
import json

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from dotenv import dotenv_values

import numpy as np
import fitz
from PIL import Image
import io
import os
import os.path
from os import path
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
gauth = GoogleAuth()           
drive = GoogleDrive(gauth)

# Load environment variables from .env file
load_dotenv()

# Path of the file you want to extract from 
main_path = '' # Write path to directory if the file is in a different directory than this script
file_path = "" # Write name of the file
full_path = main_path + file_path

# THIS IS FOR RETURNING ALL THE TEXT FROM A PDF AND FORMATTING IT CORRECTLY

# Read every line from a PDF and save it to a variable 'txt'
output_string = StringIO()
with open(full_path, 'rb') as in_file:
    parser = PDFParser(in_file)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)

# Save the output as a string in 'txt' variable 
txt = output_string.getvalue()

#Split the 'txt' variable into a list
toSpreadsheet = txt.split("\n")
without_empty_strings = []
for string in toSpreadsheet:
    # Remove empty strings
    if (string != ""):
        # Remove whitespace at the beginning and end of string
        newString = string.strip(' ')
        without_empty_strings.append(newString)

# Creating an array of arrays
finalArray = np.array_split(without_empty_strings, len(without_empty_strings))
liste = np.array(finalArray).tolist()
articleNr = file_path[0:7] # Stores the first 7 characters of the file name

# THIS IS FOR WRITING TO LOCAL TXT FILE IN NEW FOLDER

if (path.exists(articleNr)): # Checks if the path already exists(file/folder), and exits if it does
    if (path.isfile(articleNr)):
        sys.exit('File already exists, exiting program')
    if (path.isfile(articleNr) == False):
        sys.exit('Directory already exists, exiting program')
    else:
        sys.exit('Program says either file or directory exists but it doesnt, im shutting down now.')

# This code decides where the directory will be made
newDir = os.mkdir(articleNr) # Create new directory
dir = os.path.join(os.getcwd() + '/', articleNr) # Store path to new directory in a variable 

f = open(dir + '/' + articleNr + '.txt', 'w') # Writing the text from the pdf to a specified txt file in specified folder
f.write(txt)
f.close()

# THIS IS FOR SPREADSHEET
# It connects to a Google Spreadsheet and writes the text to the spreadsheet

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = json.loads(os.getenv('KEYS').replace('/\\n/g', '\n')) # Load the keys from .env as JSON

creds = None
creds = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID of the spreadsheet.
SAMPLE_SPREADSHEET_ID = os.getenv('SPREADSHEET_ID') # THIS IS FOR THE SUMMERSPRINT

service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()

# Update/write to the spreadsheet
request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, 
                            range="Text!A1", valueInputOption="USER_ENTERED", body={"values":liste}).execute()

# Read/return the text from the spreadsheet
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="Text!A1:A1000").execute()
values = result.get('values', [])
articleNr = values[0][0][0:7] #gets the articlenr from the PDF(6 digits)
print(values)

# THIS IS FOR THE IMAGES, you can store it on the local disk and on Google Drive

pdf_file = fitz.open(full_path)

folder_id = os.getenv('FOLDER_ID') # Google Drive folder ID
# iterate over PDF pages
for page_index in range(len(pdf_file)):
    # get the page itself
    page = pdf_file[page_index]
    image_list = page.getImageList()
    # printing number of images found in this page
    if image_list:
        print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
    else:
        print("[!] No images found on page", page_index)
    for image_index, img in enumerate(page.getImageList(), start=1):
        # get the XREF of the image
        xref = img[0]
        # extract the image bytes
        base_image = pdf_file.extractImage(xref)
        image_bytes = base_image["image"]
        # get the image extension
        image_ext = base_image["ext"]
        # load it to PIL
        image = Image.open(io.BytesIO(image_bytes))
        # save it to local disk
        #image.save(open(articleNr + f"_{page_index+1}_{image_index}.{image_ext}", "wb")) # This is for saving to Google Spreadsheets
        image.save(open(dir + '/' + articleNr + f"_{page_index+1}_{image_index}.{image_ext}", 'wb')) # This is for saving to local disk
        # articleNr + f"_{page_index+1}_{image_index}.{image_ext}"

        # THIS IS FOR UPLOADING IMAGES TO GOOGLE DRIVE
    
        f = drive.CreateFile({'title': articleNr + f"_{page_index+1}_{image_index}.{image_ext}",
                            'mimeType': 'image/png',
                            'parents': [{'kind': 'drive#fileLink', 'id':folder_id}]})
        f.SetContentFile(articleNr + f"_{page_index+1}_{image_index}.{image_ext}")
        f.Upload()

        #os.remove(articleNr + f"_{page_index+1}_{image_index}.{image_ext}") # Removing the image from local disk after uploaded to Google Drive