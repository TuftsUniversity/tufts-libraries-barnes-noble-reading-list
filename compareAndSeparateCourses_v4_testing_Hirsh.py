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

today = datetime.datetime.now().date()
filename_date = today.strftime('%Y-%m-%d')


oDir = "./Output"
if not os.path.isdir(oDir) or not os.path.exists(oDir):
    os.makedirs(oDir)

pDir = "./Processing"
if not os.path.isdir(pDir) or not os.path.exists(pDir):
    os.makedirs(pDir)

bNFilename = askopenfilename(title = "Select the Excel file parsed from Barnes & Noble reading lists")

# managedSetFilename = askopenfilename(title = "Select the Excel file output from the Managed Set")

courseSubsetFilename = askopenfilename(title = "Select the Excel file containing courses in the textbook program.")

#courseNumberMappingFilename = askopenfilename(title = "Select the Excel file containing course number and ID mapping")

bndf = pd.read_excel(bNFilename)
# isbn_alma_df = pd.read_excel(managedSetFilename)
csdf = pd.read_excel(courseSubsetFilename)
#cmdf = pd.read_excel(courseNumberMappingFilename)



# isbn_alma_df = isbn_alma_df.loc[:,~isbn_alma_df.columns.duplicated()]


# print(bndf)

csdf['Course'] = csdf['Course'].apply(lambda x: smart_str(x))

# csdf['Course'] = csdf['Course'].apply(lambda x: x.encode("utf-8"))

csdf['Course'] = csdf['Course'].apply(lambda x: x.replace("-", " "))

csdf['Course'] = csdf['Course'].apply(lambda x: x.strip())

# print("\n\ncmdf: \n" + str(cmdf))
#
# print("\n\ncmdf Subject: \n" + str(cmdf['Subject']))
#
# print("\n\ncmdf Catalog: \n" + str(cmdf['Catalog']))
#
#
# cmdf['SIS Course Number'] = cmdf['Subject'] + " " + cmdf['Catalog'].map(str)
#
# cmdf['Alma Course Number'] = cmdf['Term'].map(str) + "-" + cmdf['Class Nbr'].map(str)
#
# cmdf = cmdf.loc[:, ['SIS Course Number', 'Alma Course Number']]
#
# print("\n\ncmdf: \n" + str(cmdf))



bndf['Additional Barcodes or Material Type'] = bndf['Additional Barcodes or Material Type'].str.replace(' ', '')
bndf['Additional Barcodes or Material Type'] = bndf['Additional Barcodes or Material Type'].str.split(';')

#bndf['Additional Barcodes or Material Type'] = bndf['Additional Barcodes or Material Type'].astype('int64')
bndf = bndf.fillna(0)
bndf['ISBN'] = bndf['ISBN'].astype('object')

# print(str(bndf) + "\n\n")


bndf = (bndf
    .set_index(['Author', 'Title', 'Edition', 'ISBN', 'Course', 'Section', 'Professor'])['Additional Barcodes or Material Type']
    .apply(pd.Series)
    .stack()
    .reset_index()
    .drop('level_7', axis=1)
    .rename(columns={0:'ISBN Additional'}))

# print(str(bndf) + "\n\n")






keys = [c for c in bndf if c.startswith('ISBN')]

print("\n\n" + str(keys))


bndf = pd.melt(bndf, id_vars=(['Author', 'Title', 'Edition', 'Section', 'Professor', 'Course']), value_vars=keys, value_name='ISBN').drop('variable', axis=1)

bndf['ISBN'] = bndf['ISBN'].astype('str')




bndf['Course'] = bndf['Course'].apply(lambda x: x.encode(encoding='ascii', errors='replace'))
bndf['Section'] = bndf['Section'].apply(lambda x: x.encode(encoding='ascii', errors='replace'))
bndf['Professor'] = bndf['Professor'].apply(lambda x: x.encode(encoding='ascii', errors='replace'))

courseSeries = bndf['Course'].str.split(';', expand=True).stack().str.strip().reset_index(level=1, drop=True)
sectionSeries = bndf['Section'].str.split(';', expand=True).stack().str.strip().reset_index(level=1, drop=True)
profSeries = bndf['Professor'].str.split(';', expand=True).stack().str.strip().reset_index(level=1, drop=True)

bndf1 = pd.concat([courseSeries, sectionSeries, profSeries], axis=1, keys=['Course', 'Section', 'Professor'])

bndf = bndf.drop(['Course', 'Section', 'Professor'], axis=1).join(bndf1).reset_index(drop=True)
#
# bndf['ISBN'] = bndf['ISBN'].astype('str')


# print("\n\n\n" + str(bndf))

x = 0
sru_url = "https://tufts.alma.exlibrisgroup.com/view/sru/01TUN_INST?version=1.2&operation=searchRetrieve&recordSchema=marcxml&query=alma.isbn="
isbn_alma_df = pd.DataFrame(columns=['ISBN', 'MMS_ID'])

isbn_alma_df['ISBN'] = isbn_alma_df['ISBN'].astype('str')

bndf = bndf.merge(csdf, on='Course', how='inner')

print("BNDF limited to courses in list: " + str(bndf) + "\n\n")
csdf = csdf.dropna(subset=['Course'])
isbn_list = bndf['ISBN'].tolist()
matchInBNDF = pd.DataFrame(columns=['ISBN', 'MMS ID'])

matchInBNDF['ISBN'] = matchInBNDF['ISBN'].astype('str')


for isbn in isbn_list:
    if isbn.startswith("281"):
        x += 1
        continue
    sru_url_isbn = sru_url + str(isbn)

    print("Line number: " + str(x + 1) + "\nSRU URL: " + sru_url_isbn)
    try:
        result = requests.get(sru_url_isbn)

    except:
        matchInBNDF = matchInBNDF.append({'ISBN': "NO MATCH", 'MMS_ID': "NO MATCH"}, ignore_index=True)
        continue
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

matchInBNDF.to_excel(pDir + "/Initial Matched Alma ISBNs - All.xlsx", index=False)

bndf.to_excel(pDir + "/All Barnes & Noble - Separate Rows for Each ISBN - Fall 2019.xlsx", index=False)

today = datetime.datetime.now().date()
filename_date = today.strftime('%Y-%m-%d')


all_bn_df = pd.read_excel(pDir + "/All Barnes & Noble - Separate Rows for Each ISBN - Fall 2019.xlsx",  encoding='utf-8')

all_bn_df['ISBN'] = all_bn_df['ISBN'].apply(lambda x: smart_str(x))

matching_bn_df = pd.read_excel(pDir + '/Initial Matched Alma ISBNs - All.xlsx', encoding='utf-8')
matching_bn_df['ISBN'] = matching_bn_df['ISBN'].apply(lambda x: str(x))


master = pd.merge(all_bn_df, matching_bn_df, on=['ISBN'], how='outer', indicator=True)

master['MMS ID'] = master['MMS ID'].apply(lambda x: str(x))

books_to_order_df = master[master['_merge'] == 'left_only']

books_we_have = master[master['_merge'] == 'both']

books_to_order_df = books_to_order_df.sort_values('Course')
books_we_have = books_we_have.sort_values('Course')

books_we_have = books_we_have.drop_duplicates(['Course Code', 'ISBN'], keep='first')

books_we_have = (books_we_have.groupby(['Processing Department', 'Author', 'Title', 'Edition', 'ISBN', 'Course', 'MMS ID'], as_index=False)['Professor', 'Course Code', 'Section', 'Course Name'].agg(lambda x: '; '.join(x)))


books_to_order_df =  books_to_order_df.drop_duplicates(['Course Code', 'ISBN'], keep='first')

books_to_order_df = (books_to_order_df.groupby(['Processing Department', 'Author', 'Title', 'Edition', 'ISBN', 'Course', 'MMS ID'], as_index=False)['Professor', 'Course Code', 'Section', 'Course Name'].agg(lambda x: '; '.join(x)))
# books_we_have = (books_we_have.groupby(['Processing Department', 'Author', 'Title', 'Edition', 'ISBN', 'Course', 'MMS_ID', 'Professor', 'Course Name', 'Section'], as_index=False)['Course Code'].agg(lambda x: ', '.join(x)))
#
# books_we_have = (books_we_have.groupby(['Processing Department', 'Author', 'Title', 'Edition', 'ISBN', 'Course', 'MMS_ID', 'Professor', 'Course Name', 'Section'], as_index=False)['Course Code'].agg(lambda x: ', '.join(x)))


# isbn_alma_df.to_excel("ISBN file from Alma " + filename_date + ".xslx", encoding='utf-8', index=False)

books_to_order_df.to_excel(oDir + "/Books to Order " + filename_date + ".xlsx", encoding='utf-8', index=False)

books_we_have.to_excel(oDir + '/Books We Have ' + filename_date + '.xlsx', encoding='utf-8', index=False)
