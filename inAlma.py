############################################################################################
############################################################################################
########
########    Title:      compare.py
########    Author:     Henry Steele, Library Technology Services, Tufts University
########    Date:       May 2019
########
########    Purpose:
########        Determine which titles from the list of Barnes & Noble readings
########        are not already in our collection (Tufts/Alma), to identify
########        titles for puchase in the AS&E Textbook Initiative
########
########   Input:
########        - output of parseBN.py
########            - parse out all the ISBNs from this output file, using regex in
########              Notepad++ ( at this point).  Get a one column list--some books
########              have multiple ISBNs.  Enter "ISBN" as a header for this one
########              column of data.
########        - use the ISBN list from the B&N output file noted above to create a Managed
########          Set in Alma.  Simply upload the file above into an itemized Managed Set.
########          the members of this Managed Set is the second input

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# for >= Python 2.7 < Python 3
from tkFileDialog import askopenfilename

#for Python 3
# from tkinter import Tk
# from tkinter import filedialog
# from tkinter import *


import os
import xlwt
import xlsxwriter
import openpyxl
import re
import datetime
import requests
from django.utils.encoding import smart_str, smart_unicode

bNFilename = askopenfilename(title = "Select the Excel file parsed from Barnes & Noble reading lists")

bndf = pd.read_excel(bNFilename)

x = 0
sru_url = "https://tufts.alma.exlibrisgroup.com/view/sru/01TUN_INST?version=1.2&operation=searchRetrieve&recordSchema=marcxml&query=alma.isbn="
isbn_alma_df = pd.DataFrame(columns=['ISBN', 'MMS_ID'])

isbn_alma_df['ISBN'] = isbn_alma_df['ISBN'].astype('str')

isbn_list = bndf['ISBN'].tolist()
matchInBNDF = pd.DataFrame(columns=['ISBN', 'MMS ID'])

matchInBNDF['ISBN'] = matchInBNDF['ISBN'].astype('str')
for isbn in isbn_list:
    sru_url_isbn = sru_url + str(isbn)

    print("Line number: " + str(x + 1) + "\nSRU URL: " + sru_url_isbn)
    result = requests.get(sru_url_isbn)

    print("\n" + smart_str(result.content) + "\n")

    resultString = smart_str(result.content)


    print("\nData type result.text: " + str(type(resultString)))
    if re.search(r'\<datafield[ ]tag\=\"020\"[\s\S]+?\<\/datafield\>', resultString):
        #
        # print("\n\n\n\n\n **********IN LOOP**********\n\n\n\n\n")
        mms_id_match = re.search(r'\<controlfield[ ]tag\=\"001\">(\d+)\<\/controlfield\>', resultString)
        mms_id = re.sub(r'\>(\d+)\>', r'$1', mms_id_match.group(1))

        print("\nMMS ID:" + str(mms_id))
        oTwentyMatches = re.findall(r'\<datafield[ ]tag\=\"020\"[\s\S]+?\<\/datafield\>', resultString)


        for datafield in oTwentyMatches:
            print("\nDatafield: " + datafield)
            try:
                isbnMatch = re.search(r'\<subfield[ ]code\=\"[azq]\"\>(\d+)', datafield)
                isbnAlma = isbnMatch.group(1)
            except:
                isbnAlma = ""

            matchInBNDF = matchInBNDF.append({'ISBN': isbnAlma, 'MMS_ID': mms_id}, ignore_index=True)
            print("\n\n" + str(isbn_alma_df))
            print("\n\n" + str(bndf))
            print("\n\nType isbn_alma_df[ISBN]: " + str(type(isbnAlma)) + "\n")
            print("\nType bndf[ISBN]: " +  str(type(bndf.loc[0,'ISBN'])) + "\n")

            # matchInBNDF.append(bndf[bndf['ISBN'] == smart_str(isbnAlma)])
            print("\nMatching row from bndf: \n" + str(matchInBNDF) + "\n\n")

            print("\nISBN Alma: " + isbnAlma + "\n")
            print("\nISBN B & N: " + bndf.loc[0,'ISBN'] + "\n")

    x += 1

matchInBNDF.to_excel("Initial Matched Alma ISBNs - All.xlsx", encoding='utf-8', index=False)
isbn_alma_df['ISBN'] = isbn_alma_df['ISBN'].astype('str')
# isbn_alma_df['ISBN (13)'] = isbn_alma_df['ISBN (13)'].astype('str')
# isbn_alma_df['ISBN'] = isbn_alma_df['ISBN'].apply(lambda x: re.sub(r'\D', '', x))
# isbn_alma_df['ISBN (13)'] = isbn_alma_df['ISBN (13)'].apply(lambda x: re.sub(r'\D', '', x))
# isbn_alma_df = isbn_alma_df.fillna('Empty')
#
# keys_m = [c for c in isbn_alma_df if c.startswith('ISBN')]

# print("\n\n" + str(keys))

# isbn_alma_df = pd.melt(isbn_alma_df, id_vars=(['Title', 'Edition', 'MMS ID']), value_vars=keys_m, value_name='ISBN').drop('variable', axis=1)



# print("\n\n\n" + str(isbn_alma_df))

print("\n\nbndf: \n" + str(bndf))

print("\n\ncsdf: \n" + str(csdf))
bndf['ISBN'] = bndf['ISBN'].astype(str)
bndf2 = bndf.copy()

matchInBNDF = pd.merge(matchInBNDF, bndf2, on=['ISBN'], how='inner')

matchInBNDF = matchInBNDF.sort_values('Course')

matchInBNDF.to_excel('Books We Have ' + filename_date + '.xlsx', encoding='utf-8', index=False)
