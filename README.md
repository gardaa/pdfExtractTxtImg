# Getting Started

To begin with, you have to add environment variables to the `.env` file. There is an `.env.example` file included in the repository as an example showing how it is done. This is done to hide sensitive information. You can get this information by creating a project and service account at the Google Cloud Platform (the Cloud Console). The `SPREADSHEET_ID` and `FOLDER_ID` is available in the URL of your Google Spreadsheet and Google Drive folder. You have to give your service account an editor role in the spreadsheet for the script to work.

# How it's built

This is a Python script made for extracting text and images from PDF files, giving you the opportunity to write and upload it to Google applications through the use of a Google API.

The extracted text gets written to a Google Spreadsheet of your choice. This is done by extracting the text from the PDF, formatting it as a nested array (because that's the way Google Spreadsheet accepts it).

The extracted images either gets uploaded to a Google Drive folder of your choice, or gets stored in a new folder on the local disk (or both). The images will be named the first 7 characters of the filename they got extracted from, followed by an underscore and the index of the page it is located on. Example: `1234567_3_2` means the second image on the third page of the file "1234567". As for the folder created on the local disk, the folder name will just be the first 7 characters of the filename. 

As for uploading text or images to a folder on the local disk, the script checks if the folder/file name already exists, and if it does, it exits without uploading.

# How to RUN

To run the script you have to enter `python3 pdf2txt.py` in the terminal. You will see the output of a nested array, which is just a copy of all the text written to the Google Spreadsheet. At the top of the `pdf2txt.py` file, you have to enter the file name (and path of the file if the file is in another directory than the script). In the future I will add the functionality to write the file name/path as a system argument when executing the code in the terminal like this: `python3 pdf2txt.py PATHEXAMPLE`.

# Known issues

# TODO

- [ ] Adding functionality to send the file as a system argument