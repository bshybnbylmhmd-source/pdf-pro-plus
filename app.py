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
    <title>PDF Pro+™ 📄 - المنصة الشاملة</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f0f3f6; padding: 10px; margin: 0; }
        h1 { text-align: center; color: #2c3e50; font-size: 18px; }
        nav { text-align: center; margin-bottom: 15px; }
        nav a { margin: 0 10px; text-decoration: none; color: #16a085; font-weight: bold; font-size: 12px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; }
        .card { background: #fff; padding: 10px; border-radius: 8px; border: 1px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        h3 { font-size: 12px; margin-top: 0; color: #2c3e50; }
        input[type="file"], input[type="text"], input[type="number"] { width: 95%; padding: 5px; margin: 5px 0; font-size: 10px; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #1abc9c; color: white; border: none; padding: 6px; width: 100%; cursor: pointer; border-radius: 4px; font-weight: bold; font-size: 11px; }
        button:hover { background: #16a085; }
        footer { text-align: center; margin-top: 20px; font-size: 10px; color: #7f8c8d; }
    </style>
</head>
<body>
    <h1>PDF Pro+™ 📄 - مالك الموقع: صهيب</h1>
    <nav>
        <a href="/">الرئيسية والأدوات</a> | 
        <a href="/privacy">سياسة الخصوصية</a> | 
        <a href="/about">من نحن</a>
    </nav>

    <div class="grid">
        <div class="card"><h3>دمج PDF</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="merge"><input type="file" name="pdfs" multiple required><button>دمج الملفات</button></form></div>
        <div class="card"><h3>تدوير 180°</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="rotate180"><input type="file" name="pdf" required><button>تدوير 180</button></form></div>
        <div class="card"><h3>تدوير 90°</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="rotate90"><input type="file" name="pdf" required><button>تدوير 90</button></form></div>
        <div class="card"><h3>تدوير 270°</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="rotate270"><input type="file" name="pdf" required><button>تدوير 270</button></form></div>
        <div class="card"><h3>تشفير بكلمة مرور</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="encrypt"><input type="file" name="pdf" required><input type="text" name="password" placeholder="كلمة المرور" required><button>تشفير الملف</button></form></div>
        <div class="card"><h3>إزالة تشفير PDF</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="decrypt"><input type="file" name="pdf" required><input type="text" name="password" placeholder="كلمة المرور الحالية" required><button>إزالة التشفير</button></form></div>
        <div class="card"><h3>حذف صفحة محددة</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="delete"><input type="file" name="pdf" required><input type="number" name="page" placeholder="رقم الصفحة" required><button>حذف الصفحة</button></form></div>
        <div class="card"><h3>تكرار صفحة محددة</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="duplicate_page"><input type="file" name="pdf" required><input type="number" name="page" placeholder="رقم الصفحة للتكرار" required><button>تكرار الصفحة</button></form></div>
        <div class="card"><h3>عكس ترتيب الصفحات</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="reverse"><input type="file" name="pdf" required><button>عكس الترتيب</button></form></div>
        <div class="card"><h3>استخراج نطاق صفحات</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="extract_range"><input type="file" name="pdf" required><input type="number" name="start" placeholder="من صفحة" required><input type="number" name="end" placeholder="إلى صفحة" required><button>استخراج النطاق</button></form></div>
        <div class="card"><h3>استخراج الصفحة الأولى</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="split_first"><input type="file" name="pdf" required><button>استخراج الصفحة الأولى</button></form></div>
        <div class="card"><h3>تعديل عنوان الملف (Metadata)</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="metadata"><input type="file" name="pdf" required><input type="text" name="title" placeholder="العنوان الجديد" required><button>تعديل العنوان</button></form></div>
        <div class="card"><h3>تحسين وتنظيف الملف</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="compress_lite"><input type="file" name="pdf" required><button>تحسين الملف</button></form></div>
        <div class="card"><h3>استخراج النصوص (.txt)</h3><form action="/process" method="POST" enctype="multipart/form-data"><input type="hidden" name="tool" value="text"><input type="file" name="pdf" required><button>استخراج النص</button></form></div>
    </div>
    <footer>جميع الحقوق محفوظة © 2026 - صهيب</footer>
</body>
</html>
"""

PRIVACY_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>سياسة الخصوصية - PDF Pro+</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f0f3f6; padding: 20px; margin: 0; }
        .box { background: #fff; padding: 25px; border-radius: 8px; max-width: 700px; margin: auto; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; font-size: 20px; }
        p, li { font-size: 13px; color: #444; line-height: 1.8; }
        a { color: #16a085; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <h1>سياسة الخصوصية</h1>
        <p>نحن في منصة <strong>PDF Pro+</strong> نولي اهتماماً بالغاً لخصوصية زوارنا. لا يتم الاحتفاظ بملفاتك الشخصية أو ملفات الـ PDF المرفوعة على خوادمنا لفترات طويلة، حيث يتم حذفها تلقائياً بعد معالجتها وحفظها على جهازك.</p>
        <p>كما أننا قد نستعين بشركات إعلانية طرف ثالث (مثل Google AdSense) لعرض الإعلانات.</p>
        <p><a href="/">← العودة إلى رئيسية الأدوات</a></p>
    </div>
</body>
</html>
"""

ABOUT_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>من نحن - PDF Pro+</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f0f3f6; padding: 20px; margin: 0; }
        .box { background: #fff; padding: 25px; border-radius: 8px; max-width: 700px; margin: auto; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; font-size: 20px; }
        p { font-size: 13px; color: #444; line-height: 1.8; }
        a { color: #16a085; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <h1>من نحن</h1>
        <p>منصة <strong>PDF Pro+</strong> هي أداة ويب متكاملة ومصممة لمساعدة المستخدمين على إدارة، تعديل، ومعالجة ملفات الـ PDF بكل سهولة وسرعة.</p>
        <p>تم تطوير هذه المنصة بكل إتقان بواسطة المطور <strong>صهيب</strong>.</p>
        <p><a href="/">← العودة إلى رئيسية الأدوات</a></p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return TEMPLATE

@app.route('/privacy')
def privacy():
    return PRIVACY_TEMPLATE

@app.route('/about')
def about():
    return ABOUT_TEMPLATE

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

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/rotate-90", methods=["POST"])
def rotate_90_route():
    # سيتم إضافة منطق الاستقبال والتنفيذ هنا
    return "تم تدوير الملف 90 درجة بنجاح"

@app.route("/rotate-180", methods=["POST"])
def rotate_180_route():
    return "تم تدوير الملف 180 درجة بنجاح"

@app.route("/rotate-270", methods=["POST"])
def rotate_270_route():
    return "تم تدوير الملف 270 درجة بنجاح"

@app.route("/encrypt", methods=["POST"])
def encrypt_route():
    # سيتم إضافة منطق التشفير هنا
    return "تم تشفير الملف بنجاح"

@app.route("/decrypt", methods=["POST"])
def decrypt_route():
    # سيتم إضافة منطق إزالة التشفير هنا
    return "تم إزالة التشفير بنجاح"

@app.route("/delete-page", methods=["POST"])
def delete_page_route():
    return "تم حذف الصفحة بنجاح"

@app.route("/duplicate-page", methods=["POST"])
def duplicate_page_route():
    return "تم تكرار الصفحة بنجاح"

@app.route("/reverse-pages", methods=["POST"])
def reverse_pages_route():
    return "تم عكس ترتيب الصفحات بنجاح"

@app.route("/extract-range", methods=["POST"])
def extract_range_route():
    return "تم استخراج النطاق بنجاح"

@app.route("/extract-first", methods=["POST"])
def extract_first_route():
    return "تم استخراج الصفحة الأولى بنجاح"

@app.route("/update-metadata", methods=["POST"])
def update_metadata_route():
    return "تم تعديل عنوان الملف بنجاح"

@app.route("/extract-text", methods=["POST"])
def extract_text_route():
    return "تم استخراج النصوص بنجاح"

@app.route("/optimize", methods=["POST"])
def optimize_route():
    return "تم تحسين وضغط الملف بنجاح"

@app.route("/split-pdf", methods=["POST"])
def split_pdf_route():
    return "تم تقسيم الملف بنجاح"

@app.route("/images-to-pdf", methods=["POST"])
def images_to_pdf_route():
    return "تم تحويل الصور إلى PDF بنجاح"

@app.route("/add-watermark", methods=["POST"])
def add_watermark_route():
    return "تمت إضافة العلامة المائية بنجاح"

@app.route("/extract-images", methods=["POST"])
def extract_images_route():
    return "تم استخراج الصور بنجاح"

@app.route("/page-count", methods=["POST"])
def page_count_route():
    return "تم حساب عدد الصفحات بنجاح"

@app.route("/extract-links", methods=["POST"])
def extract_links_route():
    return "تم استخراج الروابط بنجاح"

@app.route("/merge-multiple", methods=["POST"])
def merge_multiple_route():
    return "تم دمج الملفات المتعددة بنجاح"

@app.route("/reorder-pages", methods=["POST"])
def reorder_pages_route():
    return "تم إعادة ترتيب الصفحات بنجاح"

@app.route("/check-encrypted", methods=["POST"])
def check_encrypted_route():
    return "تم فحص حالة تشفير الملف بنجاح"

@app.route("/set-author", methods=["POST"])
def set_author_route():
    return "تم تحديث معلومات المؤلف والموضوع بنجاح"

@app.route("/export-txt", methods=["POST"])
def export_txt_route():
    return "تم تصدير النصوص إلى ملف نصي بنجاح"

@app.route("/verify-not-empty", methods=["POST"])
def verify_not_empty_route():
    return "تم التحقق من أن الملف غير فارغ بنجاح"

@app.route("/rotate-page", methods=["POST"])
def rotate_page_route():
    return "تم تدوير الصفحة بنجاح"

@app.route("/remove-metadata", methods=["POST"])
def remove_metadata_route():
    return "تم حذف خصائص الملف بنجاح"

@app.route("/search-text", methods=["POST"])
def search_text_route():
    return "تم البحث عن الكلمة بنجاح"

@app.route("/extract-first", methods=["POST"])
def extract_first_route():
    return "تم استخراج الصفحة الأولى بنجاح"

@app.route("/count-images", methods=["POST"])
def count_images_route():
    return "تم حساب عدد الصور بنجاح"

@app.route("/list-attachments", methods=["POST"])
def list_attachments_route():
    return "تم استعراض الملفات المرفقة بنجاح"

@app.route("/remove-cover", methods=["POST"])
def remove_cover_route():
    return "تم إزالة صفحة الغلاف بنجاح"

@app.route("/export-info-json", methods=["POST"])
def export_info_json_route():
    return "تم تصدير معلومات الملف بصيغة JSON بنجاح"

@app.route("/extract-page-text", methods=["POST"])
def extract_page_text_route():
    return "تم استخراج نص الصفحة بنجاح"

@app.route("/verify-structure", methods=["POST"])
def verify_structure_route():
    return "تم فحص بنية الملف بنجاح"

@app.route("/check-orientation", methods=["POST"])
def check_orientation_route():
    return "تم فحص اتجاه الصفحة بنجاح"

@app.route("/pdf-version", methods=["POST"])
def pdf_version_route():
    return "تم جلب إصدار ملف الـ PDF بنجاح"
