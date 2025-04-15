from fpdf import FPDF


# Define the PDF class
class PDFConverter(FPDF):

    def header(self):
        # Add a header (optional)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, ' ', 0, 1, 'C')

    def footer(self):
        # Add a footer (optional)
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    # Function to convert .txt to .pdf
    def txt_to_pdf(self, text_data, pdf_filename):
        self.add_page()

        # Do last minute text processing and output as the pdf file
        # Add the text to the PDF
        self.set_font("Arial", size=12)
        text_data = text_data.replace("?", "'") # replace some ? with ' that are mis-coded
        self.multi_cell(0, 10, text_data)

        # Output the PDF to a file
        self.output(pdf_filename)
