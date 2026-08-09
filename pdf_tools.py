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

def rotate_pdf(input_path, output_path, angle):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(angle)
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

def encrypt_pdf(input_path, output_path, password):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    writer.encrypt(password)
    with open(output_path, "wb") as f:
        writer.write(f)

def decrypt_pdf(input_path, output_path, password):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    if reader.is_encrypted:
        reader.decrypt(password)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    with open(output_path, "wb") as f:
        writer.write(f)

def delete_page(input_path, output_path, page_num):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for index, page in enumerate(reader.pages):
        if index + 1 != page_num:
            writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

def duplicate_page(input_path, output_path, page_num):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for index, page in enumerate(reader.pages):
        writer.add_page(page)
        if index + 1 == page_num:
            writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

def reverse_pages(input_path, output_path):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reversed(reader.pages):
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

def extract_range(input_path, output_path, start_page, end_page):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for index in range(start_page - 1, end_page):
        if 0 <= index < len(reader.pages):
            writer.add_page(reader.pages[index])
    with open(output_path, "wb") as f:
        writer.write(f)

def extract_first_page(input_path, output_path):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    if len(reader.pages) > 0:
        writer.add_page(reader.pages[0])
    with open(output_path, "wb") as f:
        writer.write(f)

def update_metadata(input_path, output_path, new_title):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    metadata = reader.metadata
    author = metadata.author if metadata and metadata.author else ""
    writer.add_metadata({
        "/Title": new_title,
        "/Author": author
    })
    with open(output_path, "wb") as f:
        writer.write(f)

def extract_text_to_file(input_path, output_path):
    from pypdf import PdfReader
    reader = PdfReader(input_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n--- صفحة جديدة ---\n"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def optimize_pdf(input_path, output_path):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

def split_pdf(input_path, output_dir, chunk_size=1):
    from pypdf import PdfReader, PdfWriter
    import os
    reader = PdfReader(input_path)
    os.makedirs(output_dir, exist_ok=True)
    for i in range(0, len(reader.pages), chunk_size):
        writer = PdfWriter()
        for j in range(i, min(i + chunk_size, len(reader.pages))):
            writer.add_page(reader.pages[j])
        output_path = os.path.join(output_dir, f"part_{i//chunk_size + 1}.pdf")
        with open(output_path, "wb") as f:
            writer.write(f)

def images_to_pdf(image_paths, output_path):
    from PIL import Image
    images = [Image.open(img).convert("RGB") for img in image_paths]
    if images:
        images[0].save(output_path, save_all=True, append_images=images[1:])

def add_watermark(input_path, output_path, watermark_text):
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    import io

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.drawString(100, 100, watermark_text)
    can.save()
    packet.seek(0)
    
    watermark_pdf = PdfReader(packet)
    watermark_page = watermark_pdf.pages[0]

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

def extract_images_from_pdf(input_path, output_dir):
    from pypdf import PdfReader
    import os
    reader = PdfReader(input_path)
    os.makedirs(output_dir, exist_ok=True)
    count = 0
    for i, page in enumerate(reader.pages):
        for image_file_object in page.images:
            count += 1
            image_path = os.path.join(output_dir, f"image_{count}_{image_file_object.name}")
            with open(image_path, "wb") as fp:
                fp.write(image_file_object.data)

def get_pdf_page_count(input_path):
    from pypdf import PdfReader
    reader = PdfReader(input_path)
    return len(reader.pages)

def extract_pdf_links(input_path):
    from pypdf import PdfReader
    reader = PdfReader(input_path)
    links = []
    for page in reader.pages:
        if "/Annots" in page:
            for annot in page["/Annots"]:
                obj = annot.get_object()
                if "/A" in obj and "/URI" in obj["/A"]:
                    links.append(obj["/A"]["/URI"])
    return list(set(links))

def merge_multiple_pdfs(pdf_list, output_path):
    from pypdf import PdfWriter
    writer = PdfWriter()
    for pdf in pdf_list:
        writer.append(pdf)
    with open(output_path, "wb") as f:
        writer.write(f)

def reorder_pdf_pages(input_path, output_path, new_order):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page_num in new_order:
        if 0 <= page_num < len(reader.pages):
            writer.add_page(reader.pages[page_num])
    with open(output_path, "wb") as f:
        writer.write(f)

def is_pdf_encrypted(input_path):
    from pypdf import PdfReader
    reader = PdfReader(input_path)
    return reader.is_encrypted

def set_pdf_author_subject(input_path, output_path, author, subject):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    writer.append(reader)
    writer.add_metadata({
        "/Author": author,
        "/Subject": subject
    })
    with open(output_path, "wb") as f:
        writer.write(f)

def export_pdf_to_txt(input_path, output_txt_path):
    from pypdf import PdfReader
    reader = PdfReader(input_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(text)

def verify_pdf_not_empty(input_path):
    from pypdf import PdfReader
    reader = PdfReader(input_path)
    return len(reader.pages) > 0

def rotate_single_page(input_path, output_path, page_num, angle):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for idx, page in enumerate(reader.pages):
        if idx == page_num:
            page.rotate(angle)
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

def remove_pdf_metadata(input_path, output_path):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    writer.append(reader)
    writer.add_metadata({})
    with open(output_path, "wb") as f:
        writer.write(f)

def search_text_in_pdf(input_path, keyword):
    from pypdf import PdfReader
    reader = PdfReader(input_path)
    results = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and keyword.lower() in text.lower():
            results.append(idx + 1)
    return results

def extract_first_page(input_path, output_path):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    if len(reader.pages) > 0:
        writer.add_page(reader.pages[0])
    with open(output_path, "wb") as f:
        writer.write(f)

def count_pdf_images(input_path):
    from pypdf import PdfReader
    reader = PdfReader(input_path)
    image_count = 0
    for page in reader.pages:
        image_count += len(page.images)
    return image_count

def list_pdf_attachments(input_path):
    from pypdf import PdfReader
    reader = PdfReader(input_path)
    attachments = []
    if reader.attachments:
        for filename in reader.attachments:
            attachments.append(filename)
    return attachments

def reverse_pdf_pages(input_path, output_path):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reversed(reader.pages):
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

def extract_single_page_to_file(input_path, output_path, page_num):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    if 0 <= page_num < len(reader.pages):
        writer.add_page(reader.pages[page_num])
        with open(output_path, "wb") as f:
            writer.write(f)

def remove_pdf_cover(input_path, output_path):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    if len(reader.pages) > 1:
        for page in reader.pages[1:]:
            writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)

def export_pdf_info_json(input_path):
    from pypdf import PdfReader
    import json
    reader = PdfReader(input_path)
    info = reader.metadata
    data = {
        "title": info.title if info and info.title else "",
        "author": info.author if info and info.author else "",
        "subject": info.subject if info and info.subject else "",
        "pages_count": len(reader.pages),
        "is_encrypted": reader.is_encrypted
    }
    return json.dumps(data, ensure_ascii=False)

def extract_specific_page_text(input_path, page_num):
    from pypdf import PdfReader
    reader = PdfReader(input_path)
    if 0 <= page_num < len(reader.pages):
        text = reader.pages[page_num].extract_text()
        return text if text else ""
    return ""

def verify_pdf_structure(input_path):
    try:
        from pypdf import PdfReader
        reader = PdfReader(input_path)
        _ = len(reader.pages)
        return True
    except Exception:
        return False

def check_pdf_orientation(input_path, page_num=0):
    from pypdf import PdfReader
    reader = PdfReader(input_path)
    if 0 <= page_num < len(reader.pages):
        page = reader.pages[page_num]
        rot = page.get("/Rotate", 0)
        return rot
    return 0

def get_pdf_version(input_path):
    from pypdf import PdfReader
    reader = PdfReader(input_path)
    return reader.pdf_header

def check_pdf_page_count(input_path):
    from pypdf import PdfReader
    reader = PdfReader(input_path)
    return len(reader.pages)

def get_pdf_summary_status(input_path):
    from pypdf import PdfReader
    reader = PdfReader(input_path)
    return {
        "pages": len(reader.pages),
        "encrypted": reader.is_encrypted,
        "version": reader.pdf_header
    }
