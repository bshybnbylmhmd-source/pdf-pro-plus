import os
import io
import json
from pypdf import PdfReader, PdfWriter
from PIL import Image

def extract_text_to_file(input_path, output_path):
    reader = PdfReader(input_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n--- صفحة جديدة ---\n"
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

def split_pdf(input_path, output_dir, chunk_size=1):
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
    images = [Image.open(img).convert("RGB") for img in image_paths]
    if images:
        images[0].save(output_path, save_all=True, append_images=images[1:])

def add_watermark(input_path, output_path, watermark_text):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

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
    reader = PdfReader(input_path)
    return len(reader.pages)

def extract_pdf_links(input_path):
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
    writer = PdfWriter()
    for pdf in pdf_list:
        writer.append(pdf)
    with open(output_path, "wb") as f:
        writer.write(f)

def reorder_pdf_pages(input_path, output_path, new_order):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page_num in new_order:
        if 0 <= page_num < len(reader.pages):
            writer.add_page(reader.pages[page_num])
    with open(output_path, "wb") as f:
        writer.write(f)

def is_pdf_encrypted(input_path):
    reader = PdfReader(input_path)
    return reader.is_encrypted

def set_pdf_author_subject(input_path, output_path, author, subject):
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
    reader = PdfReader(input_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(text)

def verify_pdf_not_empty(input_path):
    reader = PdfReader(input_path)
    return len(reader.pages) > 0

def rotate_single_page(input_path, output_path, page_num, angle):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for idx, page in enumerate(reader.pages):
        if idx == page_num:
            page.rotate(angle)
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

def remove_pdf_metadata(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    writer.append(reader)
    writer.add_metadata({})
    with open(output_path, "wb") as f:
        writer.write(f)

def search_text_in_pdf(input_path, keyword):
    reader = PdfReader(input_path)
    results = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and keyword.lower() in text.lower():
            results.append(idx + 1)
    return results

def extract_first_page(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    if len(reader.pages) > 0:
        writer.add_page(reader.pages[0])
    with open(output_path, "wb") as f:
        writer.write(f)

def count_pdf_images(input_path):
    reader = PdfReader(input_path)
    image_count = 0
    for page in reader.pages:
        image_count += len(page.images)
    return image_count

def list_pdf_attachments(input_path):
    reader = PdfReader(input_path)
    attachments = []
    if reader.attachments:
        for filename in reader.attachments:
            attachments.append(filename)
    return attachments

def reverse_pdf_pages(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reversed(reader.pages):
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

def extract_single_page_to_file(input_path, output_path, page_num):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    if 0 <= page_num < len(reader.pages):
        writer.add_page(reader.pages[page_num])
        with open(output_path, "wb") as f:
            writer.write(f)

def remove_pdf_cover(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    if len(reader.pages) > 1:
        for page in reader.pages[1:]:
            writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)

def export_pdf_info_json(input_path):
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
    reader = PdfReader(input_path)
    if 0 <= page_num < len(reader.pages):
        text = reader.pages[page_num].extract_text()
        return text if text else ""
    return ""

def verify_pdf_structure(input_path):
    try:
        reader = PdfReader(input_path)
        _ = len(reader.pages)
        return True
    except Exception:
        return False

def check_pdf_orientation(input_path, page_num=0):
    reader = PdfReader(input_path)
    if 0 <= page_num < len(reader.pages):
        page = reader.pages[page_num]
        rot = page.get("/Rotate", 0)
        return rot
    return 0

def get_pdf_version(input_path):
    reader = PdfReader(input_path)
    return reader.pdf_header

def check_pdf_page_count(input_path):
    reader = PdfReader(input_path)
    return len(reader.pages)

def get_pdf_summary_status(input_path):
    reader = PdfReader(input_path)
    return {
        "pages": len(reader.pages),
        "encrypted": reader.is_encrypted,
        "version": reader.pdf_header
    }
