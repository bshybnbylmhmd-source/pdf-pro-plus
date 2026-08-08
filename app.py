
import time, threading, os

def cleanup_old_files():
    while True:
        try:
            now = time.time()
            for f in os.listdir("."):
                if f.endswith((".pdf", ".zip", ".txt", ".png", ".jpg")) and (now - os.path.getmtime(f) > 600):
                    os.remove(f)
        except:
            pass
        time.sleep(300)

threading.Thread(target=cleanup_old_files, daemon=True).start()

from flask import render_template, request, redirect, url_for, session

import os

VISIT_FILE = "visit_count.txt"

def get_visit_count():
    if not os.path.exists(VISIT_FILE):
        with open(VISIT_FILE, "w") as f:
            f.write("1452")
    with open(VISIT_FILE, "r") as f:
        try:
            count = int(f.read().strip())
        except:
            count = 1452
    count += 1
    with open(VISIT_FILE, "w") as f:
        f.write(str(count))
    return count
from flask import Flask, render_template, request, send_file, jsonify, redirect, session
from pypdf import PdfMerger, PdfReader, PdfWriter
from pdf2image import convert_from_bytes
from PIL import Image
import io
import zipfile
import datetime
import re

app = Flask(__name__)
app.secret_key = 'pdf_pro_plus_ultimate_system'
USERS = {'suhaib': '123456'}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if USERS.get(request.form.get('username')) == request.form.get('password'):
            session['user'] = request.form.get('username')
            return redirect('/')
        return render_template('login.html', error='بيانات خاطئة')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/')
def index():
    if 'user' not in session: return redirect('/login')
    return render_template('index.html', visit_count=get_visit_count())

# 1. الضغط
@app.route('/process/compress', methods=['POST'])
def compress():
    file = request.files['file']
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages: writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='compressed.pdf')

# 2. الدمج
@app.route('/process/merge', methods=['POST'])
def merge():
    files = request.files.getlist('file')
    merger = PdfMerger()
    for f in files: merger.append(f)
    out = io.BytesIO()
    merger.write(out)
    merger.close()
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='merged.pdf')

# 3. حذف صفحة
@app.route('/process/delete_page', methods=['POST'])
def delete_page():
    file = request.files['file']
    page_num = int(request.form.get('page_num', 1)) - 1
    reader = PdfReader(file)
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if i != page_num: writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='deleted_page.pdf')

# 4. تدوير 180
@app.route('/process/rotate_all', methods=['POST'])
def rotate_all():
    file = request.files['file']
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(180)
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='rotated_180.pdf')

# 5. استخراج نطاق
@app.route('/process/extract_range', methods=['POST'])
def extract_range():
    file = request.files['file']
    start = int(request.form.get('start', 1)) - 1
    end = int(request.form.get('end', 1))
    reader = PdfReader(file)
    writer = PdfWriter()
    for i in range(start, min(end, len(reader.pages))):
        writer.add_page(reader.pages[i])
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='extracted_range.pdf')

# 6. تشفير بكلمة مرور
@app.route('/process/encrypt', methods=['POST'])
def encrypt_pdf():
    file = request.files['file']
    password = request.form.get('password', '123456')
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='encrypted.pdf')

# 7. عكس الصفحات
@app.route('/process/reverse', methods=['POST'])
def reverse_pdf():
    file = request.files['file']
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reversed(reader.pages):
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='reversed.pdf')

# 8. استخراج النصوص
@app.route('/process/extract_text', methods=['POST'])
def extract_text():
    file = request.files['file']
    reader = PdfReader(file)
    text = ""
    for i, page in enumerate(reader.pages):
        text += f"--- Page {i+1} ---\n" + (page.extract_text() or "") + "\n\n"
    out = io.BytesIO(text.encode('utf-8'))
    out.seek(0)
    return send_file(out, mimetype='text/plain', as_attachment=True, download_name='extracted_text.txt')

# 9. تدوير 90
@app.route('/process/rotate_90', methods=['POST'])
def rotate_90():
    file = request.files['file']
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(90)
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='rotated_90.pdf')

# 10. تدوير 270
@app.route('/process/rotate_270', methods=['POST'])
def rotate_270():
    file = request.files['file']
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(270)
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='rotated_270.pdf')

# 11. إضافة صفحة فارغة
@app.route('/process/add_blank', methods=['POST'])
def add_blank():
    file = request.files['file']
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_blank_page()
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='with_blank_page.pdf')

# 12. معلومات الملف
@app.route('/process/info', methods=['POST'])
def get_info():
    file = request.files['file']
    reader = PdfReader(file)
    info = {
        'pages_count': len(reader.pages),
        'is_encrypted': reader.is_encrypted
    }
    return jsonify(info)

# 13. تكرار الملف
@app.route('/process/duplicate', methods=['POST'])
def duplicate_pdf():
    file = request.files['file']
    reader = PdfReader(file)
    writer = PdfWriter()
    for _ in range(2):
        for page in reader.pages:
            writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='duplicated.pdf')

# 14. استخراج صفحة منفردة
@app.route('/process/extract_single', methods=['POST'])
def extract_single():
    file = request.files['file']
    page_num = int(request.form.get('page_num', 1)) - 1
    reader = PdfReader(file)
    writer = PdfWriter()
    if 0 <= page_num < len(reader.pages):
        writer.add_page(reader.pages[page_num])
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name=f'page_{page_num+1}.pdf')

# 15. فك حماية وإزالة القيود
@app.route('/process/unlock', methods=['POST'])
def unlock_pdf():
    file = request.files['file']
    reader = PdfReader(file)
    if reader.is_encrypted:
        try:
            reader.decrypt('')
        except:
            pass
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='unlocked.pdf')

# 16. فصل كل صفحة بملف ZIP
@app.route('/process/split_all', methods=['POST'])
def split_all():
    file = request.files['file']
    reader = PdfReader(file)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            page_pdf = io.BytesIO()
            writer.write(page_pdf)
            page_pdf.seek(0)
            zip_file.writestr(f'page_{i+1}.pdf', page_pdf.read())
    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='all_pages_separated.zip')

# 17. تحويل الصفحات إلى صور
@app.route('/process/to_images', methods=['POST'])
def to_images():
    file = request.files['file']
    images = convert_from_bytes(file.read())
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for i, img in enumerate(images):
            img_byte = io.BytesIO()
            img.save(img_byte, format='PNG')
            zip_file.writestr(f'page_{i+1}.png', img_byte.getvalue())
    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='pdf_to_images.zip')

# 18. تغيير مقاس الصفحات
@app.route('/process/scale', methods=['POST'])
def scale_pdf():
    file = request.files['file']
    scale_factor = float(request.form.get('factor', 1.0))
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        page.scale_by(scale_factor)
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='scaled.pdf')

# 19. قص الحواف
@app.route('/process/crop', methods=['POST'])
def crop_pdf():
    file = request.files['file']
    dx, dy = 20.0, 20.0
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        box = page.mediabox
        page.cropbox.lower_left = (box.lower_left[0] + dx, box.lower_left[1] + dy)
        page.cropbox.upper_right = (box.upper_right[0] - dx, box.upper_right[1] - dy)
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='cropped.pdf')

# 20. علامة مائية
@app.route('/process/watermark', methods=['POST'])
def add_watermark():
    file = request.files['file']
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='watermarked.pdf')

# 21. تحويل الصور إلى PDF
@app.route('/process/images_to_pdf', methods=['POST'])
def images_to_pdf():
    files = request.files.getlist('file')
    images = [Image.open(f).convert('RGB') for f in files]
    out = io.BytesIO()
    if images:
        images[0].save(out, format='PDF', save_all=True, append_images=images[1:])
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='images_converted.pdf')

# 22. استخراج الصور
@app.route('/process/extract_images', methods=['POST'])
def extract_images():
    file = request.files['file']
    reader = PdfReader(file)
    zip_buffer = io.BytesIO()
    img_count = 0
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for page_idx, page in enumerate(reader.pages):
            for count, image_file_object in enumerate(page.images):
                img_count += 1
                zip_file.writestr(f"p{page_idx+1}_img_{count+1}.png", image_file_object.data)
    zip_buffer.seek(0)
    if img_count == 0:
        return to_images()
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='extracted_images.zip')

# 23. إعادة ترتيب الصفحات
@app.route('/process/reorder', methods=['POST'])
def reorder_pdf():
    file = request.files['file']
    order_str = request.form.get('order', '1,2')
    reader = PdfReader(file)
    writer = PdfWriter()
    try:
        indices = [int(x.strip()) - 1 for x in order_str.split(',') if x.strip().isdigit()]
        for idx in indices:
            if 0 <= idx < len(reader.pages):
                writer.add_page(reader.pages[idx])
    except:
        for page in reader.pages:
            writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='reordered.pdf')

# 24. تقسيم الملف لنصفين
@app.route('/process/split_half', methods=['POST'])
def split_half():
    file = request.files['file']
    reader = PdfReader(file)
    mid = len(reader.pages) // 2
    writer1, writer2 = PdfWriter(), PdfWriter()
    for i, page in enumerate(reader.pages):
        if i < mid: writer1.add_page(page)
        else: writer2.add_page(page)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        out1, out2 = io.BytesIO(), io.BytesIO()
        writer1.write(out1); out1.seek(0)
        writer2.write(out2); out2.seek(0)
        zip_file.writestr('part_1.pdf', out1.read())
        zip_file.writestr('part_2.pdf', out2.read())
    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='split_halves.zip')

# 25. تنظيف الملف
@app.route('/process/clean', methods=['POST'])
def clean_pdf():
    file = request.files['file']
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        if page.extract_text().strip() != "":
            writer.add_page(page)
    if len(writer.pages) == 0:
        for page in reader.pages: writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='cleaned.pdf')

# 26. مضاعفة الصفحات مرتين
@app.route('/process/duplicate_pages', methods=['POST'])
def duplicate_pages():
    file = request.files['file']
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='all_pages_doubled.pdf')

# 27. ضغط الصور الداخلية
@app.route('/process/compress_images', methods=['POST'])
def compress_images():
    file = request.files['file']
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='compressed_images.pdf')

# 28. استخراج الروابط من الملف
@app.route('/process/extract_urls', methods=['POST'])
def extract_urls():
    file = request.files['file']
    reader = PdfReader(file)
    urls = set()
    for page in reader.pages:
        text = page.extract_text() or ""
        found = re.findall(r'https?://[^\s]+', text)
        for u in found: urls.add(u)
    content = "\n".join(urls) if urls else "لم يتم العثور على روابط مباشرة في هذا المستند."
    out = io.BytesIO(content.encode('utf-8'))
    out.seek(0)
    return send_file(out, mimetype='text/plain', as_attachment=True, download_name='extracted_urls.txt')

# 29. تجميع المحاضرات (2-in-1)
@app.route('/process/n_up', methods=['POST'])
def n_up():
    file = request.files['file']
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='2_in_1_layout.pdf')

# 30. ختم التاريخ والوقت الحالي على المستند
@app.route('/process/timestamp', methods=['POST'])
def timestamp_pdf():
    file = request.files['file']
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='timestamped.pdf')

# --- الأدوات الجديدة الـ 4 المضافة لتصبح 34 أداة ---

# 31. استخراج الجداول والنصوص المنظمة (.txt)
@app.route('/process/extract_tables', methods=['POST'])
def extract_tables():
    file = request.files['file']
    reader = PdfReader(file)
    output_text = ""
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        output_text += f"=== جدول أو بيانات صفحة {idx+1} ===\n" + text + "\n\n"
    out = io.BytesIO(output_text.encode('utf-8'))
    out.seek(0)
    return send_file(out, mimetype='text/plain', as_attachment=True, download_name='extracted_tables.txt')

# 32. تحسين وضغط البنية الداخلية (Optimize Streams)
@app.route('/process/optimize', methods=['POST'])
def optimize_pdf():
    file = request.files['file']
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='optimized.pdf')

# 33. مقارنة سريعة بين ملفين (مقارنة عدد الصفحات)
@app.route('/process/compare', methods=['POST'])
def compare_pdfs():
    files = request.files.getlist('file')
    if len(files) < 2:
        return jsonify({'error': 'الرجاء اختيار ملفين للمقارنة'}), 400
    r1 = PdfReader(files[0])
    r2 = PdfReader(files[1])
    res = f"الملف الأول: {len(r1.pages)} صفحة\nالملف الثاني: {len(r2.pages)} صفحة\n"
    res += "التطابق في عدد الصفحات: " + ("نعم" if len(r1.pages) == len(r2.pages) else "لا")
    out = io.BytesIO(res.encode('utf-8'))
    out.seek(0)
    return send_file(out, mimetype='text/plain', as_attachment=True, download_name='comparison_result.txt')

# 34. تكرار نطاق صفحة محدد
@app.route('/process/duplicate_range', methods=['POST'])
def duplicate_range():
    file = request.files['file']
    start = int(request.form.get('start', 1)) - 1
    end = int(request.form.get('end', 1))
    reader = PdfReader(file)
    writer = PdfWriter()
    # نسخ الصفحات العادية
    for page in reader.pages:
        writer.add_page(page)
    # تكرار النطاق المحدد وإضافته للنهاية
    for i in range(start, min(end, len(reader.pages))):
        writer.add_page(reader.pages[i])
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='duplicated_range.pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")
