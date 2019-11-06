# tufts-libraries-barnes-noble-reading-list
tufts-libraries-barnes-noble-reading-list

**Title:** Parse Barnes & Noble Reading Lists

**Author:** Henry Steele, Library Technology Services, Tufts University

**parseBN.py:**



	**Purpose:**

	-  Parse the raw output file Barnes & Noble provides, which is simply the text 
	   output of a webpage, into a dataframe which can be exported to Excel and
	   sent to Collections.

	**Input:**

	- raw output from Barnes & Noble, usually from a person named "Boon"
    - the name of this file has always been "qprint.txt"

	**Running:**

	- execute the script in Python by python parseBN.py
	- choose raw Barnes & Noble file in the file picker
	
	**Output:**
	- in script's main directory, there will be a file called "Cleaned Barnes and Noble File <date> .xls"
	- this file will be one of the input files for the next phase of this process, using compare.py
	
	
**compare.py**

	**Purpose:**
	- Determine which titles from the list of Barnes & Noble readings
	are not already in our collection (Tufts/Alma), to identify
	titles for puchase in the AS&E Textbook Initiative

	For each valid ISBN in the Barnes and Noble file, the script attempts
	to retrieve the bib record for this record from our Alma SRU 
	(Search/Retrieval by URL) endpoint.  
		
	**Input:**
	
    - output of parseBN.py "Cleaned Barnes and Noble File <date>.xls"
    - course subset
	  - this is the list of courses numbers that you wish to seek in
	    in the Barnes and Noble

	**Output:**
	
	- Books We Have.xlsx
        - If a record is retrieved from SRU, then
          we have the item in Alma, and information about the item including MMS ID,
          title, and course information, go in this file
    - Books to Order.xslx
        - Otherwise, the citation goes in this file, of thigns to be ordered
