import os
from typing import Container
from io import BytesIO, StringIO

def fix_xml_format(text_str):
    """
    Parameters:
    -----------
    text_str: str
        decoded charcter string
    
    Returns:
    -----------
    text_str: str
        text that is fixed
    """
    map_dict    = {'u27a2': '?'}
    for key in map_dict:
        text_str= text_str.replace(key,map_dict[key])
    return text_str

def convert_pdf(path: str, format: str = "text", codec: str = "utf-8",
                password: str = "", maxpages: int = 0, caching: bool = True,
                pagenos: Container[int] = set(),) -> str:
    """Summary
    Parameters
    ----------
    path : str
        Path to the pdf file
    format : str, optional
        Format of output, must be one of: "text", "html", "xml".
        By default, "text" format is used
    codec : str, optional
        Encoding. By default "utf-8" is used
    password : str, optional
        Password
    maxpages : int, optional
        Max number of pages to convert. By default is 0, i.e. reads all pages.
    caching : bool, optional
        Caching. By default is True
    pagenos : Container[int], optional
        Provide a list with numbers of pages to convert
    Returns
    -------
    str
        Converted pdf file
    """
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter, XMLConverter, HTMLConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    laparams = LAParams()
    if format == "text":
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == "html":
        device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == "xml":
        device = XMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    else:
        raise ValueError("provide format, either text, html or xml!")
    with open(path, "rb") as fp:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(
            fp,
            pagenos,
            maxpages=maxpages,
            password=password,
            caching=caching,
            check_extractable=True, 
        ):
            interpreter.process_page(page)
        text = retstr.getvalue().decode(encoding=codec)#.encode('utf-8').decode()
    device.close()
    retstr.close()
    text    = fix_xml_format(text)
    return text
    
def pdf_to_text_pydf(input_file):
    import PyPDF2
    file        = open(input_file,'rb')
    pdfReader   = PyPDF2.PdfReader(file)
    #printing number of pages in pdf file. 
    print("Total number of pages in sample.pdf",len(pdfReader.pages))
    txt         = ''
    for page_num in range(len(pdfReader.pages)):
        # creating a page object    
        pageObj = pdfReader.pages[page_num]
        # extracting text from page
        txt_t   = pageObj.extract_text()
        txt     = txt +'\n'+ txt_t
    file.close()
    return txt

def xml_to_json(xml_str, jsonl=False):
    """ 
    Input:
        xml - xml string of the file output. Will be converted into jsonl format
        jsonl - boolean to determine if output needs to be in jsonl format
    Output:
        json - either pure json or jsonl format
    """  
    import json
    import re
    import xmltodict
    import xml.etree.ElementTree as ET
    # Clean up the xml file
    if xml_str[-1:] == '\n':
        xml_str     = xml_str[:-1]
        print(xml_str)
    # tree = ET.parse(xml_str)
    # root = tree.getroot()
    root    = ET.fromstring(xml_str)
    for child in root.iter():
        print(child.text)
    # Convert XML to dictionary object using xmltodict
    # data_dict   = xmltodict.parse(xml_str)  
    data_dict = {}
    print(data_dict)    
    

if __name__ == "__main__":
    # Set up root directory for pdf files. 
    base_dir    = "C:\\Test\\GPT\\raw_pdf"
    out_dir     = "C:\\Test\\GPT\\processed_pdf"
    json_format = 'json'
    # Loop over all the pdf files in the directory
    for pdf_file in os.listdir(base_dir):
        full_path   = os.path.join(base_dir,pdf_file)
        print(full_path)
        if '.pdf' in pdf_file:
            print("This is a pdf file.")
            # Method: PyPDF2
            # txt     = pdf_to_text_pydf(full_path)
            # print(f"Method PyPDF2:\n{txt}")
            
            # Method: pdfminer - I like this the best initially
            xml         = convert_pdf(full_path,
                                      format='xml',
                                      codec='utf-8')
            txt         = convert_pdf(full_path,
                                      format='text',
                                      codec='utf-8')
            # Save Text file as txt
            with open(os.path.join(out_dir,'TEXT',pdf_file.split('.')[0]+'.txt'),"w+") as file:
                file.write(txt)  
            # Save XML file as xml
            with open(os.path.join(out_dir,'XML',pdf_file.split('.')[0]+'.xml'),"w+") as file:
                file.write(xml)            
            # Convert to JSON
            json_data   = xml_to_json(xml, jsonl=False)
            # Store data in output location
            with open(os.path.join(out_dir,'JSON',pdf_file.split('.')[0]+json_format),"w+") as file:
                file.write(json_data)
            out_path    = os.path.join(out_path,pdf_file.split('.')[0]+'.json')
            print("Complete") 