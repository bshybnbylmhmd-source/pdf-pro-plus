import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

def process_pdf_tool(tool, request_form, request_files, upload_folder):
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
    
    file = request_files.get('pdf')
    if not file: raise ValueError("الرجاء رفع ملف PDF")
    reader = PdfReader(file)
    writer = PdfWriter()

    if tool == 'rotate180':
        for page in reader.pages:
            page.rotate(180)
            writer.add_page(page)
        out_name = "rotated_180.pdf"
    elif tool == 'rotate90':
        for page in reader.pages:
            page.rotate(90)
            writer.add_page(page)
        out_name = "rotated_90.pdf"
    elif tool == 'rotate270':
        for page in reader.pages:
            page.rotate(270)
            writer.add_page(page)
        out_name = "rotated_270.pdf"
    elif tool == 'encrypt':
        pwd = request_form.get('password', '1234')
        for page in reader.pages: writer.add_page(page)
        writer.encrypt(pwd)
        out_name = "encrypted.pdf"
    elif tool == 'decrypt':
        pwd = request_form.get('password', '1234')
        if reader.is_encrypted:
            reader.decrypt(pwd)
        for page in reader.pages: writer.add_page(page)
        out_name = "decrypted.pdf"
    elif tool == 'delete':
        del_page = int(request_form.get('page', 1)) - 1
        for idx, page in enumerate(reader.pages):
            if idx != del_page: writer.add_page(page)
        out_name = "page_deleted.pdf"
    elif tool == 'reverse':
        for page in reversed(reader.pages):
            writer.add_page(page)
        out_name = "reversed.pdf"
    elif tool == 'extract_range':
        start = int(request_form.get('start', 1)) - 1
        end = int(request_form.get('end', len(reader.pages)))
        for idx in range(start, min(end, len(reader.pages))):
            writer.add_page(reader.pages[idx])
        out_name = "extracted_range.pdf"
    elif tool == 'split_first':
        if len(reader.pages) > 0:
            writer.add_page(reader.pages[0])
        out_name = "split_page_1.pdf"
    elif tool == 'metadata':
        title = request_form.get('title', 'PDF Pro+ Document')
        for page in reader.pages: writer.add_page(page)
        writer.add_metadata({'/Title': title})
        out_name = "metadata_updated.pdf"
    elif tool == 'compress_lite':
        for page in reader.pages:
            writer.add_page(page)
        out_name = "optimized.pdf"
    elif tool == 'duplicate_page':
        dup_idx = int(request_form.get('page', 1)) - 1
        for idx, page in enumerate(reader.pages):
            writer.add_page(page)
            if idx == dup_idx:
                writer.add_page(page) # تكرار الصفحة المحددة
        out_name = "page_duplicated.pdf"
    elif tool == 'text':
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text() + "\n--- صفحة جديدة ---\n"
        out_name = "extracted_text.txt"
        out_path = os.path.join(upload_folder, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        return out_name
    else:
        for page in reader.pages: writer.add_page(page)
        out_name = "processed.pdf"

    out_path = os.path.join(upload_folder, out_name)
    with open(out_path, "wb") as f:
        writer.write(f)
    return out_name
