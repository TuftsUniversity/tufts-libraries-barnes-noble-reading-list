############################################################################################
############################################################################################
########
########    Title:      finishCompare.py
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
import os

from tkFileDialog import askopenfilename

from django.utils.encoding import smart_str, smart_unicode



pDir = "./Processing"
if not os.path.isdir(pDir) or not os.path.exists(pDir):
    os.makedirs(pDir)

oDir = './Output'
if not os.path.isdir(oDir) or not os.path.exists(oDir):
    os.makedirs(oDir)



today = datetime.now().date()
filename_date = today.strftime('%Y-%m-%d')


all_bn_df = pd.read_excel(pDir + "/All Barnes & Noble - Separate Rows for Each ISBN - Fall 2019.xlsx",  encoding='utf-8')

all_bn_df['ISBN'] = all_bn_df['ISBN'].apply(lambda x: smart_str(x))

matching_bn_df = pd.read_excel(pDir + '/Initial Matched Alma ISBNs - All.xlsx', encoding='utf-8')


#
# courseSubsetFilename = askopenfilename(title = "Select the Excel file containing courses in the textbook program.")
#
# csdf = pd.read_excel(courseSubsetFilename, encoding='utf-8')
#
#
# csdf2 = csdf.copy()
#
# csdf2['Course'] = csdf2['Course'].apply(lambda x: smart_str(x))
#
# # csdf['Course'] = csdf['Course'].apply(lambda x: x.encode("utf-8"))
#
# csdf2['Course'] = csdf2['Course'].apply(lambda x: x.replace("-", " "))
#
# csdf2['Course'] = csdf2['Course'].apply(lambda x: x.strip())
#
# matching_bn_df = matching_bn_df.drop('MMS ID', axis=1)
#
# matching_bn_df = matching_bn_df.rename(columns={"MMS_ID": "MMS ID"})
#
#
# master = pd.merge(all_bn_df, csdf2, on=['Course'], how='inner')


# master.to_excel(oDir + "/Master List for Testing " + filename_date + ".xlsx", encoding='utf-8', index=False)


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
