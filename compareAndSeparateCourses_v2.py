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
from django.utils.encoding import smart_str, smart_unicode

bNFilename = askopenfilename(title = "Select the Excel File parsed from Barnes & Noble reading lists")

managedSetFilename = askopenfilename(title = "Select the Excel File output from the Managed Set")


bndf = pd.read_excel(bNFilename)
msdf = pd.read_excel(managedSetFilename)

msdf = msdf.loc[:,~msdf.columns.duplicated()]


print(bndf)




bndf['Additional Barcodes or Material Type'] = bndf['Additional Barcodes or Material Type'].str.replace(' ', '')
bndf['Additional Barcodes or Material Type'] = bndf['Additional Barcodes or Material Type'].str.split(';')

#bndf['Additional Barcodes or Material Type'] = bndf['Additional Barcodes or Material Type'].astype('int64')
bndf = bndf.fillna(0)
bndf['ISBN'] = bndf['ISBN'].astype('object')

print(str(bndf) + "\n\n")


bndf = (bndf
    .set_index(['Author', 'Title', 'Edition', 'ISBN', 'Course', 'Section', 'Professor'])['Additional Barcodes or Material Type']
    .apply(pd.Series)
    .stack()
    .reset_index()
    .drop('level_7', axis=1)
    .rename(columns={0:'ISBN Additional'}))

print(str(bndf) + "\n\n")






keys = [c for c in bndf if c.startswith('ISBN')]

print("\n\n" + str(keys))


bndf = pd.melt(bndf, id_vars=(['Author', 'Title', 'Edition', 'Section', 'Professor', 'Course']), value_vars=keys, value_name='ISBN').drop('variable', axis=1)

#
# bndf = (bndf
#     .set_index(['Author', 'Title', 'Edition', 'ISBN', 'Course', 'Professor'])['Course', 'Section']
#     .apply(pd.Series)
#     .stack()
#     .reset_index()
#     .drop('level_6', axis=1)
#     .rename(columns={0:'Course and Section'}))

bndf['Course'] = bndf['Course'].apply(lambda x: x.encode(encoding='ascii', errors='replace'))
bndf['Section'] = bndf['Section'].apply(lambda x: x.encode(encoding='ascii', errors='replace'))
bndf['Professor'] = bndf['Professor'].apply(lambda x: x.encode(encoding='ascii', errors='replace'))

courseSeries = bndf['Course'].str.split(';', expand=True).stack().str.strip().reset_index(level=1, drop=True)
sectionSeries = bndf['Section'].str.split(';', expand=True).stack().str.strip().reset_index(level=1, drop=True)
profSeries = bndf['Professor'].str.split(';', expand=True).stack().str.strip().reset_index(level=1, drop=True)

bndf1 = pd.concat([courseSeries, sectionSeries, profSeries], axis=1, keys=['Course', 'Section', 'Professor'])

bndf = bndf.drop(['Course', 'Section', 'Professor'], axis=1).join(bndf1).reset_index(drop=True)

# bndf['Course'] = bndf['Course'].str.split(';').tolist()
# bndf['Section'] = bndf['Section'].str.split(';').tolist()
# bndf['Professor'] = bndf['Professor'].str.split(';').tolist()
# bndf = pd.DataFrame(bndf['Course'].str.split(';').tolist(), index=bndf['Author', 'Title', 'Edition', 'ISBN', 'Section', 'Professor']).stack()
# bndf = bndf.reset_index()
# bndf = pd.melt(bndf, id_vars=(['Author', 'Title', 'Edition', 'ISBN', 'Section', 'Professor']), value_vars=['Course'], value_name='Course').drop('variable', axis=1)
#
# bndf['Course'] = bndf['Course'].astype('object')
# bndf['Section'] = bndf['Section'].astype('object')
# bndf['Professor'] = bndf['Professor'].astype('object')
# bndf = (bndf
#     .set_index(['Author', 'Title', 'Edition', 'ISBN', 'Section', 'Professor'])['Course', 'Section', 'Professor']
#     .apply(pd.Series)
#     .stack()
#     .reset_index()
#     .drop('level_4', axis=1)
#     .rename(columns={0:'Course', 1: 'Section', 2: 'Professor'}))


#bndf = pd.melt(bndf, id_vars=(['Author', 'Title', 'Edition', 'ISBN', 'Section', 'Professor']), value_vars=['Course'], value_name='Course').drop('variable', axis=1)



# bndf = (bndf
#     .set_index(['Author', 'Title', 'Edition', 'ISBN', 'Course', 'Professor'])['Section']
#     .apply(pd.Series)
#     .stack()
#     .reset_index()
#     .drop('level_6', axis=1)
#     .rename(columns={0:'Section'}))
#
#
#
# #bndf = pd.melt(bndf, id_vars=(['Author', 'Title', 'Edition', 'ISBN', 'Course', 'Professor']), value_vars=['Section'], value_name='Section').drop('variable', axis=1)
#
# bndf = (bndf
#     .set_index(['Author', 'Title', 'Edition', 'ISBN', 'Course', 'Section'])['Professor']
#     .apply(pd.Series)
#     .stack()
#     .reset_index()
#     .drop('level_6', axis=1)
#     .rename(columns={0:'Professor'}))
#
#
# # bndf = pd.melt(bndf, id_vars=(['Author', 'Title', 'Edition', 'ISBN', 'Section', 'Course']), value_vars=['Professor'], value_name='Professor').drop('variable', axis=1)
# #bndf = pd.melt(bndf, id_vars='Title', value_vars=keys, value_name='ISBN')
#

print("\n\n\n" + str(bndf))


bndf.to_excel("All Barnes & Noble - Separate Rows for Each ISBN - Fall 2019.xlsx", index=False)


msdf['ISBN'] = msdf['ISBN'].astype('str')
msdf['ISBN (13)'] = msdf['ISBN (13)'].astype('str')
msdf['ISBN'] = msdf['ISBN'].apply(lambda x: re.sub(r'\D', '', x))
msdf['ISBN (13)'] = msdf['ISBN (13)'].apply(lambda x: re.sub(r'\D', '', x))
msdf = msdf.fillna('Empty')

keys_m = [c for c in msdf if c.startswith('ISBN')]

print("\n\n" + str(keys))

msdf = pd.melt(msdf, id_vars=(['Title', 'Edition', 'MMS ID']), value_vars=keys_m, value_name='ISBN').drop('variable', axis=1)



print("\n\n\n" + str(msdf))


bndf['ISBN'] = bndf['ISBN'].astype(str)
bndf = pd.merge(bndf, msdf, on=['ISBN'], how='outer', indicator=True)

bndf = bndf[bndf['_merge']=='left_only']

bndf = bndf.drop(['Title_y', 'Edition_y', 'MMS ID', '_merge'], axis=1)
bndf = bndf.rename(columns={'Title_x':'Title', 'Edition_x': 'Edition'})
bndf = bndf.drop_duplicates(subset=['Author', 'Title', 'Edition', 'Course', 'Section', 'Professor', 'ISBN'], keep='first')
bndf = bndf.rename(columns={'Title_x':'Title'})


today = datetime.datetime.now().date()
filename_date = today.strftime('%Y-%m-%d')
bndf.to_excel('Books to Order ' + filename_date + '.xlsx', encoding='utf-8', index=False)
