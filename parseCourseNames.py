import re
from Tkinter import Tk
from tkFileDialog import askopenfilename

import pandas as pd
import numpy as np

import xlwt
import xlrd

import io

filename = askopenfilename(title = "Select the CSV file with course information")

course_df = pd.read_csv(filename)

course_df['Parsed Course Code'] = course_df['Course Code'].apply(lambda x: re.sub(r'^[A-Za-z]{2}\d{2}([A-Za-z]+)-([A-Za-z\d])+-[A-Za-z\d]+-', '', x))

print(course_df)

for column in course_df:

    course_df[column] = course_df[column].str.decode('iso-8859-1').str.encode('utf-8')

print(course_df)

course_df.to_csv("Parsed Course Names.csv", index=False)
