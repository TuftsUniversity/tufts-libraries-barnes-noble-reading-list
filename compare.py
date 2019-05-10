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
from django.utils.encoding import smart_str, smart_unicode

bNFilename = askopenfilename(title = "Select the Excel File parsed from Barnes & Noble reading lists")

managedSetFilename = askopenfilename(title = "Select the Excel File output from the Managed Set")

#bndf = pd.read_excel(bNFilename, encoding = 'windows-1252', dtype={'MMS Id': 'str', 'Permanent Call Number': 'str', 'Barcode': 'str', 'Loan Fiscal Year':'str'}, converters={'Loan Date': pd.to_datetime, 'Loan Time': pd.to_datetime, 'Return Date': pd.to_datetime, 'Return Time': pd.to_datetime}, skipfooter=1)
bndf = pd.read_excel(bNFilename)
msdf = pd.read_excel(managedSetFilename)

msdf = msdf.loc[:,~msdf.columns.duplicated()]

print(bndf)

#print("\n\n\n")
#print(bndf)
#print("\n\n\n\n\n")
#print(msdf)
#print("\n\n\n")


bndf['Additional Barcodes or Material Type'] = bndf['Additional Barcodes or Material Type'].str.replace(' ', '')
bndf['Additional Barcodes or Material Type'] = bndf['Additional Barcodes or Material Type'].str.split(';')

print(str(bndf) + "\n\n")


bndf = (bndf
    .set_index(['Author', 'Title', 'Edition', 'Publisher', 'Imprint', 'ISBN', 'Course', 'Section', 'Professor', 'Course Capacity', 'Actual Enrollment'])['Additional Barcodes or Material Type']
    .apply(pd.Series)
    .stack()
    .reset_index()
    .drop('level_11', axis=1)
    .rename(columns={0:'Additional ISBN'}))

print(str(bndf) + "\n\n")






keys = [c for c in bndf if c.startswith('ISBN')]

print("\n\n" + str(keys))

bndf = pd.melt(bndf, id_vars=(['Author', 'Title', 'Edition', 'Publisher', 'Imprint', 'Course', 'Section', 'Professor', 'Course Capacity', 'Actual Enrollment']), value_vars=keys, value_name='ISBN').drop('variable', axis=1)

#bndf = pd.melt(bndf, id_vars='Title', value_vars=keys, value_name='ISBN')

print("\n\n\n" + str(bndf))

bndf = bndf.drop('variable', axis=1)

bndf.to_excel("Books to Order Fall 2019.xlsx", index=False)
# # bndf = bndf.rename(columns={'Additional ISBN': 'ISBN.2', 'ISBN: ISBN.1'})
# # msdf = msdf.rename(columns={'ISBN': 'ISBN.1', 'ISBN (13)': 'ISBN.2'})
# #bndf = pd.DataFrame(bndf['Additional Barcodes or Material Type'].str.split(';').tolist()).stack()
# #bndf_series = bndf.apply(lambda x: pd.Series(x['Additional Barcodes or Material Type']).str.split(';').tolist(), axis=1).stack().reset_index(level=1, drop=True)
# #bndf_series.name = 'Other ISBN'
# #print("\n\n" + str(bndf_series) + "\n\n")
# #bdnf = bndf.drop('Additional Barcodes or Material Type', axis=1).join(bndf_series)
# print(bndf)
# print("\n\n")
#
# #bndf.to_excel("Books to Order Fall 2019.xlsx", index=False)
#
#
# msdf = msdf.fillna("Empty")
# msdf['ISBN'] = msdf['ISBN'].apply(lambda x: re.sub(r'\D', '', x))
# msdf['ISBN (13)'] = msdf['ISBN (13)'].apply(lambda x: re.sub(r'\D', '', x))
#
#
#
# #bndf = pd.DataFrame(bndf['Additional Barcodes or Material Type'].str.split(';').tolist()).stack()
# #bndf_series = bndf.apply(lambda x: pd.Series(x['Additional Barcodes or Material Type']).str.split(';').tolist(), axis=1).stack().reset_index(level=1, drop=True)
# #bndf_series.name = 'Other ISBN'
# #print("\n\n" + str(bndf_series) + "\n\n")
# #bdnf = bndf.drop('Additional Barcodes or Material Type', axis=1).join(bndf_series)
# print(msdf)
# print("\n\n")
#
# # orderdf = pd.concat([pd.merge(bndf, msdf, on='ISBN', how='outer', indicator=True),
# #                     pd.merge(bndf, msdf, left_on='ISBN', right_on='ISBN (13)', how='outer', indicator=True),
# #                     pd.merge(bndf, msdf, left_on='Additional ISBN', right_on='ISBN', how='outer', indicator=True),
# #                     pd.merge(bndf, msdf, left_on='Additional ISBN', right_on='ISBN (13)', how='outer', indicator=True)])
#
# orderdf = pd.concat([pd.merge(bndf, msdf, left_on='ISBN', how='outer', indicator=True),
#                     pd.merge(bndf, msdf, left_on='ISBN', right_on='ISBN (13)', how='outer', indicator=True)])
#
# orderdf = orderdf[orderdf['_merge'] == 'left_only']
#
#
#
#
#
# orderdf.to_excel("Books to Order Fall 2019.xlsx", index=False)
#
# print(orderdf)
