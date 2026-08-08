import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

def process_pdf_tool(tool, request_form, request_files, upload_folder):
    # دالة الدمج
    if tool == 'merge':
        files = request_files.getlist('pdfs')
        merger = PdfMerger()
        for f in files:
            if f.filename: merger.append(f)
        out_name = "merged.pdf"
        out_path = os.path.join(upload_folder, out_name)
        merger.write(out_path)
        merger.close()
        return out_name
    
    # باقي الأدوات
    file = request_files.get('pdf')
    if not file: raise ValueError("الرجاء رفع ملف PDF")
    reader = PdfReader(file)
    writer = PdfWriter()

    if tool == 'rotate180':
        for page in reader.pages:
            page.rotate(180)
            writer.add_page(page)
        out_name = "rotated_180.pdf"
    elif tool == 'encrypt':
        pwd = request_form.get('password', '1234')
        for page in reader.pages: writer.add_page(page)
        writer.encrypt(pwd)
        out_name = "encrypted.pdf"
    else:
        for page in reader.pages: writer.add_page(page)
        out_name = "processed.pdf"

    out_path = os.path.join(upload_folder, out_name)
    with open(out_path, "wb") as f:
        writer.write(f)
    return out_name
