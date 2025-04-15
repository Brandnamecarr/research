''' this file is going to be used to replace placeholder text in a template cover letter with name of company provided in command line.'''

import sys
import os
from PDFConverter import PDFConverter

# get the company name from command line
company_name = sys.argv[1]

# want to remove old files before we create a new cover letter
source_directory = os.getcwd()

current_files = os.listdir(source_directory)
for file in current_files:
    if file.find("Brandon_Carr") != -1:
        filename = source_directory + "/{}".format(file)
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f'Removed {filename}')
            except FileNotFoundError:
                print(f'File not Found')
            except:
                print(f'Something went wrong while deleting {filename}')

# read in the template
lines = None
template_file = open("template_cl.txt", "r", encoding='utf-8')
lines = template_file.readlines()

# find the placeholder markins <COMPANY NAME>

PLACEHOLDER = "<COMPANY NAME>"
for i in range(0, len(lines)):
    lines[i] = lines[i].replace(PLACEHOLDER, company_name)

finalized_text_data = "".join(lines)
safe_text = finalized_text_data.encode('latin-1', 'replace').decode('utf-8')


# output cover letter as a text file.
outfile_name = "Brandon_Carr_{}".format(company_name)
outfile_txt_name = outfile_name + '.txt'
outfile_pdf_name = outfile_name + '.pdf'
outfile = open(outfile_txt_name, "w")
outfile.writelines(lines)

pdfConverter = PDFConverter()
pdfConverter.txt_to_pdf(safe_text, outfile_pdf_name)

