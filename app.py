from flask import Flask, render_template_string, request, send_file
import os
from pdf_tools import process_pdf_tool

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>PDF Pro+™ 📄 - لوحة الأدوات</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f0f3f6; padding: 10px; margin: 0; }
        h1 { text-align: center; color: #2c3e50; font-size: 18px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; }
        .card { background: #fff; padding: 10px; border-radius: 8px; border: 1px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        h3 { font-size: 12px; margin-top: 0; color: #2c3e50; }
        input[type="file"], input[type="text"], input[type="number"] { width: 95%; padding: 5px; margin: 5px 0; font-size: 10px; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #1abc9c; color: white; border: none; padding: 6px; width: 100%; cursor: pointer; border-radius: 4px; font-weight: bold; font-size: 11px; }
        button:hover { background: #16a085; }
    </style>
</head>
<body>
    <h1>PDF Pro+™ 📄 - مالك الموقع: صهيب</h1>
    <div class="grid">
        <div class="card"><h3>دمج PDF</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="merge"><input type="file" name="pdfs" multiple required><button>دمج الملفات</button></form></div>
        <div class="card"><h3>تدوير 180°</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="rotate180"><input type="file" name="pdf" required><button>تدوير 180</button></form></div>
        <div class="card"><h3>تدوير 90°</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="rotate90"><input type="file" name="pdf" required><button>تدوير 90</button></form></div>
        <div class="card"><h3>تدوير 270°</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="rotate270"><input type="file" name="pdf" required><button>تدوير 270</button></form></div>
        <div class="card"><h3>تشفير بكلمة مرور</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="encrypt"><input type="file" name="pdf" required><input type="text" name="password" placeholder="كلمة المرور" required><button>تشفير الملف</button></form></div>
        <div class="card"><h3>إزالة تشفير PDF</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="decrypt"><input type="file" name="pdf" required><input type="text" name="password" placeholder="كلمة المرور الحالية" required><button>إزالة التشفير</button></form></div>
        <div class="card"><h3>حذف صفحة محددة</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="delete"><input type="file" name="pdf" required><input type="number" name="page" placeholder="رقم الصفحة" required><button>حذف الصفحة</button></form></div>
        <div class="card"><h3>عكس ترتيب الصفحات</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="reverse"><input type="file" name="pdf" required><button>عكس الترتيب</button></form></div>
        <div class="card"><h3>استخراج نطاق صفحات</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="extract_range"><input type="file" name="pdf" required><input type="number" name="start" placeholder="من صفحة" required><input type="number" name="end" placeholder="إلى صفحة" required><button>استخراج النطاق</button></form></div>
        <div class="card"><h3>استخراج الصفحة الأولى</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="split_first"><input type="file" name="pdf" required><button>استخراج الصفحة الأولى</button></form></div>
        <div class="card"><h3>تعديل عنوان الملف (Metadata)</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="metadata"><input type="file" name="pdf" required><input type="text" name="title" placeholder="العنوان الجديد" required><button>تعديل العنوان</button></form></div>
        <div class="card"><h3>تحسين وتنظيف الملف</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="compress_lite"><input type="file" name="pdf" required><button>تحسين الملف</button></form></div>
        <div class="card"><h3>استخراج النصوص (.txt)</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="text"><input type="file" name="pdf" required><button>استخراج النص</button></form></div>
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
        return send_file(os.path.join(UPLOAD_FOLDER, out_name), as_attachment=True, download_name=out_name)
    except Exception as e:
        return f"حدث خطأ: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
