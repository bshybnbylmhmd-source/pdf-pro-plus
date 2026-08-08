from flask import Flask, render_template_string, request, send_file
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

app = Flask(__name__)

# مجلد مؤقت لحفظ الملفات المعالجة
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

FULL_FUNC_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Pro+™ 📄 - محرك الـ 44 أداة</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f0f3f6; color: #2c3e50; margin: 0; padding: 8px; }
        .container { width: 100%; box-sizing: border-box; background: #ffffff; padding: 12px; border-radius: 8px; }
        .header-bar { display: flex; justify-content: space-between; align-items: center; background: #1abc9c; color: white; padding: 10px 15px; border-radius: 6px; margin-bottom: 10px; font-size: 13px; font-weight: bold; }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
        @media (min-width: 768px) { .grid { grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); } }
        .card { background: #ffffff; border: 1px solid #cbd5e1; padding: 8px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        h3 { margin-top: 0; margin-bottom: 6px; color: #2c3e50; font-size: 11px; font-weight: bold; }
        input[type="file"], input[type="text"], input[type="number"] { display: block; margin: 4px 0; background: #f8fafc; color: #333; border: 1px solid #cbd5e1; padding: 4px 6px; border-radius: 4px; width: 95%; font-size: 10px; }
        button { background: #1abc9c; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 11px; width: 100%; font-weight: bold; }
        button:hover { background: #16a085; }
        .footer { text-align: center; margin-top: 15px; color: #7f8c8d; font-size: 11px; border-top: 1px solid #eee; padding-top: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-bar">
            <span>PDF Pro+™ 📄 (قيد البرمجة الفعالة)</span>
            <span>مالك الموقع: صهيب</span>
        </div>

        <div class="grid">
            <!-- 1. دمج الملفات (شغال فعلياً) -->
            <div class="card">
                <h3>🧩 دمج ملفات PDF</h3>
                <form action="/merge" method="POST" enctype="multipart/form-data">
                    <input type="file" name="pdfs" multiple accept=".pdf" required>
                    <button type="submit">دمج الملفات</button>
                </form>
            </div>

            <!-- 2. تدوير الملف 180 درجة (شغال فعلياً) -->
            <div class="card">
                <h3>🔃 تدوير الملف (180°)</h3>
                <form action="/rotate" method="POST" enctype="multipart/form-data">
                    <input type="file" name="pdf" required>
                    <input type="hidden" name="angle" value="180">
                    <button type="submit">تنفيذ التدوير</button>
                </form>
            </div>

            <!-- 3. تشفير الملف (شغال فعلياً) -->
            <div class="card">
                <h3>🔒 تشفير بكلمة مرور</h3>
                <form action="/encrypt" method="POST" enctype="multipart/form-data">
                    <input type="file" name="pdf" required>
                    <input type="text" name="password" placeholder="كلمة المرور" required>
                    <button type="submit">تشفير الملف</button>
                </form>
            </div>

            <!-- 4. حذف صفحة محددة (شغال فعلياً) -->
            <div class="card">
                <h3>🗑️ حذف صفحة محددة</h3>
                <form action="/delete_page" method="POST" enctype="multipart/form-data">
                    <input type="file" name="pdf" required>
                    <input type="number" name="page" placeholder="رقم الصفحة للحذف" required>
                    <button type="submit">حذف الصفحة</button>
                </form>
            </div>
        </div>

        <div class="footer">جاري تطوير وربط باقي الـ 44 أداة برمجياً خطوة بخطوة...</div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(FULL_FUNC_TEMPLATE)

# 1. مسار الدمج
@app.route('/merge', methods=['POST'])
def merge_pdfs():
    try:
        files = request.files.getlist('pdfs')
        merger = PdfMerger()
        for file in files:
            if file.filename:
                merger.append(file)
        out = os.path.join(UPLOAD_FOLDER, "merged.pdf")
        merger.write(out)
        merger.close()
        return send_file(out, as_attachment=True, download_name="merged.pdf")
    except Exception as e:
        return f"خطأ: {str(e)}"

# 2. مسار التدوير
@app.route('/rotate', methods=['POST'])
def rotate_pdf():
    try:
        file = request.files['pdf']
        angle = int(request.form.get('angle', 180))
        reader = PdfReader(file)
        writer = PdfWriter()
        for page in reader.pages:
            page.rotate(angle)
            writer.add_page(page)
        out = os.path.join(UPLOAD_FOLDER, "rotated.pdf")
        with open(out, "wb") as f:
            writer.write(f)
        return send_file(out, as_attachment=True, download_name="rotated.pdf")
    except Exception as e:
        return f"خطأ: {str(e)}"

# 3. مسار التشفير
@app.route('/encrypt', methods=['POST'])
def encrypt_pdf():
    try:
        file = request.files['pdf']
        password = request.form['password']
        reader = PdfReader(file)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(password)
        out = os.path.join(UPLOAD_FOLDER, "encrypted.pdf")
        with open(out, "wb") as f:
            writer.write(f)
        return send_file(out, as_attachment=True, download_name="encrypted.pdf")
    except Exception as e:
        return f"خطأ: {str(e)}"

# 4. مسار حذف صفحة
@app.route('/delete_page', methods=['POST'])
def delete_page():
    try:
        file = request.files['pdf']
        target_page = int(request.form['page']) - 1
        reader = PdfReader(file)
        writer = PdfWriter()
        for index, page in enumerate(reader.pages):
            if index != target_page:
                writer.add_page(page)
        out = os.path.join(UPLOAD_FOLDER, "page_deleted.pdf")
        with open(out, "wb") as f:
            writer.write(f)
        return send_file(out, as_attachment=True, download_name="page_deleted.pdf")
    except Exception as e:
        return f"خطأ: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
