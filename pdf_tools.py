import os
import io
import json
from pypdf import PdfReader, PdfWriter
from PIL import Image

def process_pdf_tool(tool_name, input_path, output_path, *args, **kwargs):
    if tool_name == 'get_page_count':
        return get_pdf_page_count(input_path)
    elif tool_name == 'optimize':
        return optimize_pdf(input_path, output_path)
    elif tool_name == 'rotate':
        angle = kwargs.get('angle', 90)
        page_num = kwargs.get('page_num', 0)
        return rotate_single_page(input_path, output_path, page_num, angle)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

def extract_text_to_file(input_path, output_path):
    reader = PdfReader(input_path)
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def optimize_pdf(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

def merge_multiple_pdfs(pdf_list, output_path):
    writer = PdfWriter()
    for pdf in pdf_list:
        writer.append(pdf)
    with open(output_path, "wb") as f:
        writer.write(f)

def get_pdf_page_count(input_path):
    reader = PdfReader(input_path)
    return len(reader.pages)

def rotate_single_page(input_path, output_path, page_num, angle):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for idx, page in enumerate(reader.pages):
        if idx == page_num:
            page.rotate(angle)
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
