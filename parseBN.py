############################################################################################
############################################################################################
########
########    Title:      compare.py
########    Author:     Henry Steele, Library Technology Services, Tufts University
########    Date:       May 2019
########
########    Purpose:
########        Parse the raw output file Barnes & Noble provides, which is simply the text
########        output of a webpage, into a dataframe which can be exported to Excel and
########        sent to Collections.
########
########   Input:
########        - raw output from Barnes & Noble, usually from a person named "Boon"
########        - the name of this file has always been "qprint.txt"
########
########    Output:
########        - a text file and a spreadsheet containin the books in tabular form,
########          with a column for each field in the file.
########        - where there are multiple values per column, such as in the case for a book
########          for multiple courses, they're separated by a semicolon within the field.
########          The placement of these subfields is consistent, so if "Smith" is the second
########          subfield in the Professor column, then the value in the second subfield of the
########          course column will be the course for that professor
import re
from Tkinter import Tk
from tkFileDialog import askopenfilename

import pandas as pd
import numpy as np

import xlwt
import xlrd

import io

Tk().withdraw()

filename = askopenfilename(title = "Select Barnes & Noble reading list file")

outfile = open("Cleaned Barnes and Noble File.txt", "w+")

testfile = open("Test File.txt", "w+")
outfile.write("Author~Title~Edition~Publisher~Imprint~ISBN~Additional Barcodes or Material Type~Course~Section~Professor~Course Capacity~Actual Enrollment\n")


current_line_position = 0

course = []
section = []
professor = []
capacity = []
actual_enrollment = []
with open(filename, 'rb') as infile:
    x = 1

    while True:
        lastLinePosition = infile.tell()
        line = infile.readline()
        if not line:
            break
        #print("CURRENTLY AT LINE " + str(x) + "\n")
        #print(line + "\n")
        current_line_position = infile.tell()
        #print("Current line position: " + str(current_line_position) + "\n")

        #print("Current line: " + line + "\n")
        data_string = ""
        line = line.replace("\r", "").replace("\n", "")
        line = re.sub(r'^[ ]{3}(\w)',r'\t\t\1', line)
        line = re.sub(r'^[ ]{9}(?=\w)', r'\t\t\t', line)
        line = re.sub(r'[ ]{2,}', r'\t', line)

        if re.match(r'^\t{2}([^\t]+)(\t)([^\t]+)?([\t ])?([^\t]+)?(\t)?([^\t]+)?(\t)?([^\t]+)?([\t ])(\d.+?)$', line):
            infile.seek(lastLinePosition)
            lastLine = infile.readline()
            if not re.match(r'^\t{3}([A-Z][^\t]+)(\t)([^\t]+)(\t)([^\t]+)(\t)([^\t]+)(\t)([^\t]+)$', lastLine) and course:
                courseString = ";".join(course)
                sectionString = ";".join(section)
                professorString = ";".join(professor)
                capacityString = ";".join(capacity)
                actual_enrollmentString = ";".join(actual_enrollment)


                course = []
                section = []
                professor = []
                capacity = []
                actual_enrollment = []


                outfile.write(courseString + "~" + sectionString + "~" + professorString + "~" + capacityString + "~" + actual_enrollmentString + "\n")
            infile.seek(current_line_position)
            if not re.match(r'^\t{2}Author', line) and not re.match(r'\t{2}Total Number of Books:', line):
                line1 = re.match(r'^\t{2}([^\t]+)(\t)([^\t]+)?([\t ])?([^\t]+)?(\t)?([^\t]+)?(\t)?([^\t]+)?([\t ])(\d.+?)$', line)
                #print("Row " + str(x) + " matched to 1st line: " + line + "\n")
                author = ""
                title = ""
                edition = ""
                publisher = ""
                imprint = ""
                isbn = ""

                author = line1.group(1)
                title = line1.group(3)
                if line1.group(5):
                    edition = line1.group(5)
                else:
                    edition = ""
                if line1.group(7):
                    publisher = line1.group(7)
                else:
                    publisher = ""

                if line1.group(9):
                    imprint = line1.group(9)

                else:
                    imprint = ""
                isbn = line1.group(11)

                if not imprint:
                    imprint = ""

                isbn = isbn.replace("-", "")
                data_string += author + "~" + title + "~" + edition + "~" + publisher + "~"  + imprint + "~" + isbn + "~"

                outfile.write(author + "~" + title + "~" + edition + "~" + publisher + "~"  + imprint + "~" + isbn + "~")





        elif re.match(r'^\t+(\*\*\s([\w ]+)\*\*).+None$|^\t(\d\S+?|None)\t+(\d\S+|None)', line):
            #print ("Row " + str(x) + " matched to 2nd line:" + line + "\n")
            matchString = ""
            material_type = ""
            additional_barcodes = ""
            line2 = re.match(r'^\t+(\*\*\s([\w ]+)\*\*).+None$|^\t(\d\S+?|None)\t+(\d\S+|None)', line)

            if re.match(r'^\t+(\*\*\s([\w ]+)\*\*).+None$', line):
                line2_1 = re.match(r'^\t+(\*\*\s([\w ]+)\*\*).+None$', line)
                material_type = line2_1.group(1)
                matchString += material_type

            if re.match('^\t(\d\S+?|None)\t+(\d\S+|None)?$', line):
                line2_2 = re.match('^\t(\d\S+?|None)\t+(\d\S+|None)$', line)
                addBarcode1 = line2_2.group(1).replace("-", "")
                addBarcode2 = line2_2.group(2).replace("-", "")
                additional_barcodes = addBarcode1 + "; " + addBarcode2
                matchString += additional_barcodes


            testfile.write("Next line: "  + line + "\n")
            testfile.write("Match: " + matchString + "\n")



            data_string += material_type + additional_barcodes + "~"
            outfile.write(material_type + additional_barcodes + "~")

        elif re.match(r'^\t{3}([A-Z][^\t]+)(\t)([^\t]+)(\t)([^\t]+)(\t)([^\t]+)(\t)([^\t]+)$', line):

            #print("Row " + str(x) + " matched to 3rd line: " + line + "\n")
            line3 = re.match(r'^\t{3}([A-Z][^\t]+)(\t)([^\t]+)(\t)([^\t]+)(\t)([^\t]+)(\t)([^\t]+)$', line)
            course.append(line3.group(1))
            section.append(line3.group(3))
            professor.append(line3.group(5))
            capacity.append(line3.group(7))
            actual_enrollment.append(line3.group(9))
            secondCourseLine = infile.readline()
            secondCourseLine = secondCourseLine.replace("\r", "").replace("\n", "")
            secondCourseLine = re.sub(r'^[ ]{3}(\w)',r'\t\t\1', secondCourseLine)
            secondCourseLine = re.sub(r'^[ ]{9}(?=\w)', r'\t\t\t', secondCourseLine)
            secondCourseLine = re.sub(r'[ ]{2,}', r'\t', secondCourseLine)


            # if re.match(r'^\t{3}([A-Z][^\t]+)(\t)([^\t]+)(\t)([^\t]+)(\t)([^\t]+)(\t)([^\t]+)$', secondCourseLine):
            #     print("Current line position after additional course: " + str(infile.tell()) + "\n")
            #     course = course.append(";")
            #     section = section.append("; ")
            #     professor = professor.append("; ")
            #     capacity = capacity.append("; ")
            #     actual_enrollment = actual_enrollment.append("; ")


            infile.seek(current_line_position)


            if re.match(r'^\t{2}([A-Z][^\t]+)(\t)([^\t]+)?([\t ])?([^\t]+)?(\t)?([^\t]+)?(\t)?([^\t]+)?([\t ])(\d.+?)$', secondCourseLine):


                courseString = ";".join(course)
                sectionString = ";".join(section)
                professorString = ";".join(professor)
                capacityString = ";".join(capacity)
                actual_enrollmentString = ";".join(actual_enrollment)

                course = []
                section = []
                professor = []
                capacity = []
                actual_enrollment = []


                outfile.write(courseString + "~" + sectionString + "~" + professorString + "~" + capacityString + "~" + actual_enrollmentString + '\n')

        #print("Current line position at end of loop: " + str(infile.tell()) + "\n")


        x += 1
infile.close()

outfile.close()
testfile.close()



filename = "Cleaned Barnes and Noble File.txt"
textFile = io.open(filename, 'r+', encoding='latin-1')
row_list = []
for row in textFile:
    row_list.append(row.split('~'))
column_list = zip(*row_list)
workbook = xlwt.Workbook()
worksheet = workbook.add_sheet('Sheet1')
i = 0
for column in column_list:
    for item in range(len(column)):
        value = column[item].strip()
        worksheet.write(item, i, value)
    i+=1
workbook.save(filename.replace('.txt', '.xls'))
