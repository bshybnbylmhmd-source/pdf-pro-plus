from flask import Flask, render_template_string, request, send_file
import os
from PyPDF2 import PdfMerger

app = Flask(__name__)

FULL_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Pro+™ 📄 (محرك الـ 44 أداة الكامل)</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #121212; color: #e0e0e0; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: #1e1e1e; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h1 { color: #3498db; text-align: center; }
        .header-bar { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 15px; margin-bottom: 20px; }
        .card { background: #2a2a2a; border: 1px solid #3a3a3a; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
        h3 { margin-top: 0; color: #f1c40f; }
        input[type="file"] { display: block; margin: 10px 0; background: #333; color: #fff; border: 1px solid #555; padding: 8px; border-radius: 4px; width: 95%; }
        button { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 15px; width: 100%; }
        button:hover { background: #2980b9; }
        .footer { text-align: center; margin-top: 30px; color: #888; font-size: 14px; border-top: 1px solid #333; padding-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-bar">
            <span>PDF Pro+™ 📄 (محرك الـ 44 أداة الكامل)</span>
            <span style="color: #e74c3c;">تسجيل الخروج</span>
        </div>
        <div class="card">
            <h3>🧩 دمج ملفات PDF</h3>
            <form action="/merge" method="POST" enctype="multipart/form-data">
                <input type="file" name="pdfs" multiple accept=".pdf" required>
                <button type="submit">دمج الملفات</button>
            </form>
        </div>
        <div class="footer">
            جميع الحقوق محفوظة © 2026 | مالك الموقع: صهيب<br>
            <span style="color: #3498db;">سياسة الخصوصية | شروط الاستخدام | 📊 الزوار: 1453</span><br><br>
            <span style="color: #f1c40f;">🌙 الوضع الليلي مفعل</span>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(FULL_TEMPLATE)

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    try:
        files = request.files.getlist('pdfs')
        merger = PdfMerger()
        for file in files:
            if file.filename:
                merger.append(file)
        output_path = "merged_output.pdf"
        merger.write(output_path)
        merger.close()
        return send_file(output_path, as_attachment=True, download_name="merged_pro.pdf")
    except Exception as e:
        return f"حدث خطأ أثناء الدمج: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
