from flask import Flask, render_template_string, request, send_file
import os
from pdf_tools import process_pdf_tool

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# هنا توضع الواجهة كاملة التي صممناها سابقاً
TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>PDF Pro+™ 📄 - الموقع الكامل</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f0f3f6; padding: 10px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }
        .card { background: #fff; padding: 10px; border-radius: 8px; border: 1px solid #ccc; }
        button { background: #1abc9c; color: white; border: none; padding: 8px; width: 100%; cursor: pointer; }
    </style>
</head>
<body>
    <h1>PDF Pro+™ 📄</h1>
    <div class="grid">
        <!-- عينة للأدوات المربوطة بالدوال -->
        <div class="card"><h3>دمج PDF</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="merge"><input type="file" name="pdfs" multiple required><button>دمج</button></form></div>
        <div class="card"><h3>تدوير 180°</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="rotate180"><input type="file" name="pdf" required><button>تدوير</button></form></div>
        <div class="card"><h3>تشفير</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="encrypt"><input type="file" name="pdf" required><input type="text" name="password" placeholder="كلمة المرور"><button>تشفير</button></form></div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return TEMPLATE

@app.route('/process', methods=['POST'])
def process():
    try:
        tool = request.form.get('tool')
        out_name = process_pdf_tool(tool, request.form, request.files, UPLOAD_FOLDER)
        return send_file(os.path.join(UPLOAD_FOLDER, out_name), as_attachment=True)
    except Exception as e:
        return f"حدث خطأ: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
