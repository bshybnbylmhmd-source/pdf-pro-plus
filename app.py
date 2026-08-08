from flask import Flask, render_template_string, request, send_file
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

app = Flask(__name__)

FULL_GRID_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Pro+™ 📄 (محرك الـ 44 أداة الكامل)</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f4f6f9; color: #333; margin: 0; padding: 10px; }
        .container { max-width: 1200px; margin: 0 auto; background: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
        .header-bar { display: flex; justify-content: space-between; align-items: center; background: #2c3e50; color: white; padding: 10px 15px; border-radius: 6px; margin-bottom: 15px; font-size: 14px; }
        .header-bar a { color: #e74c3c; text-decoration: none; font-weight: bold; }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
        .card { background: #ffffff; border: 1px solid #e1e8ed; padding: 12px; border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); transition: 0.2s; }
        .card:hover { border-color: #3498db; box-shadow: 0 3px 8px rgba(52, 152, 219, 0.15); }
        
        h3 { margin-top: 0; margin-bottom: 8px; color: #2c3e50; font-size: 13px; font-weight: bold; }
        input[type="file"], input[type="text"], input[type="number"] { display: block; margin: 6px 0; background: #f9f9f9; color: #333; border: 1px solid #dcdde1; padding: 5px 8px; border-radius: 4px; width: 93%; font-size: 12px; }
        button { background: #3498db; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; width: 100%; font-weight: bold; }
        button:hover { background: #2980b9; }
        
        .footer { text-align: center; margin-top: 20px; color: #7f8c8d; font-size: 12px; border-top: 1px solid #eee; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-bar">
            <span>PDF Pro+™ 📄 (محرك الـ 44 أداة الكامل)</span>
            <a href="#">تسجيل الخروج</a>
        </div>

        <div class="grid">
            <div class="card"><h3>📉 ضغط ملف PDF</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">تنفيذ الضغط</button></form></div>
            <div class="card"><h3>🧩 دمج ملفات PDF</h3><form action="/merge" method="POST" enctype="multipart/form-data"><input type="file" name="pdfs" multiple accept=".pdf" required><button type="submit">دمج الملفات</button></form></div>
            <div class="card"><h3>🗑️ حذف صفحة محددة</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><input type="number" name="page" placeholder="رقم الصفحة للحذف" required><button type="submit">حذف الصفحة</button></form></div>
            <div class="card"><h3>🔃 تدوير الملف (180°)</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">تدوير 180</button></form></div>
            <div class="card"><h3>🔄 تدوير الملف (90°)</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">تدوير 90</button></form></div>
            <div class="card"><h3>🔄 تدوير الملف (270°)</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">تدوير 270</button></form></div>
            <div class="card"><h3>✂️ استخراج نطاق صفحات</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><input type="text" name="start" placeholder="من"><input type="text" name="end" placeholder="إلى"><button type="submit">استخراج النطاق</button></form></div>
            <div class="card"><h3>🔒 تشفير بكلمة مرور</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><input type="text" name="password" placeholder="كلمة المرور الجديدة" required><button type="submit">تشفير الملف</button></form></div>
            <div class="card"><h3>🔄 عكس ترتيب الصفحات</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">عكس الصفحات</button></form></div>
            <div class="card"><h3>📝 استخراج النصوص (.txt)</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">استخراج النص</button></form></div>
            <div class="card"><h3>➕ إضافة صفحة فارغة</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">إضافة صفحة بالنهاية</button></form></div>
            <div class="card"><h3>ℹ️ فحص معلومات الملف</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">عرض التفاصيل</button></form></div>
            <div class="card"><h3>📋 تكرار الملف بالكامل</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">مضاعفة الصفحات</button></form></div>
            <div class="card"><h3>📄 استخراج صفحة منفردة</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><input type="number" name="page" placeholder="رقم الصفحة للاستخراج" required><button type="submit">استخراج الصفحة</button></form></div>
            <div class="card"><h3>🔓 فك الحماية وإزالة القيود</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">إزالة القفل والقيود</button></form></div>
            <div class="card"><h3>📦 فصل كل صفحة بملف ZIP</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">فصل الكل (ZIP)</button></form></div>
            <div class="card"><h3>🖼️ تحويل الصفحات إلى صور</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">تحويل إلى صور (ZIP)</button></form></div>
            <div class="card"><h3>📏 تغيير مقاس الصفحات</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><input type="text" name="scale" placeholder="معامل الحجم (مثلاً 0.5)" required><button type="submit">تغيير الحجم</button></form></div>
            <div class="card"><h3>✂️ قص حواف الصفحات (Crop)</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">قص الحواف</button></form></div>
            <div class="card"><h3>🛡️ إضافة علامة مائية</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">تطبيق العلامة</button></form></div>
            <div class="card"><h3>🖼️➡️📄 تحويل الصور إلى PDF</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="images" multiple accept="image/*" required><button type="submit">تحويل الصور لملف PDF</button></form></div>
            <div class="card"><h3>📥 استخراج الصور من الـ PDF</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">استخراج الصور (ZIP)</button></form></div>
            <div class="card"><h3>🔄 إعادة ترتيب الصفحات</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><input type="text" name="order" placeholder="الترتيب (مثال: 3,1,2,4)" required><button type="submit">تطبيق الترتيب الجديد</button></form></div>
            <div class="card"><h3>✂️ فصل الملف إلى نصفين</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">فصل إلى نصفين (ZIP)</button></form></div>
            <div class="card"><h3>🧹 تنظيف الملف وإزالة الفارغ</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">تنظيف الصفحات</button></form></div>
            <div class="card"><h3>📑 مضاعفة كل صفحة مرتين</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">مضاعفة الصفحات</button></form></div>
            <div class="card"><h3>📉 ضغط الصور الداخلية</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">ضغط الصور</button></form></div>
            <div class="card"><h3>🔗 استخراج الروابط (.txt)</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">استخراج الروابط</button></form></div>
            <div class="card"><h3>🗂️ دمج صفحتين بصفحة (2-in-1)</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">تنسيق المحاضرات</button></form></div>
            <div class="card"><h3>🕒 ختم الوقت والتاريخ</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">ختم المستند</button></form></div>
            <div class="card"><h3>📊 استخراج الجداول (.txt)</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">استخراج الجداول</button></form></div>
            <div class="card"><h3>⚡ تحسين وضغط البنية (Optimize)</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">تحسين البنية</button></form></div>
            <div class="card"><h3>⚖️ مقارنة ملفين PDF</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdfs" multiple accept=".pdf" required><button type="submit">مقارنة الملفين</button></form></div>
            <div class="card"><h3>🔁 تكرار نطاق صفحات محدد</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><input type="text" name="start" placeholder="من"><input type="text" name="end" placeholder="إلى"><button type="submit">تكرار النطاق</button></form></div>
            <div class="card"><h3>📋 استخراج حقول النماذج</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">استخراج النماذج</button></form></div>
            <div class="card"><h3>📦 تقسيم الملف لكتل (Batch ZIP)</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><input type="number" name="chunk" value="5" required><button type="submit">تقسيم بكتل</button></form></div>
            <div class="card"><h3>🛡️ تنقيح وإخفاء البيانات</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">تنقيح المستند</button></form></div>
            <div class="card"><h3>🔧 إصلاح وتصحيح الملف</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">إصلاح الملف</button></form></div>
            <div class="card"><h3>🧹 إزالة بيانات الميتا والناشر</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">إزالة الميتا</button></form></div>
            <div class="card"><h3>🔎 مقارنة محتوى النصوص</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdfs" multiple accept=".pdf" required><button type="submit">مقارنة النصوص</button></form></div>
            <div class="card"><h3>🔄 تدوير صفحة محددة فقط</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><input type="number" name="page" placeholder="الصفحة" required><input type="text" name="angle" value="90" required><button type="submit">تدوير الصفحة</button></form></div>
            <div class="card"><h3>✍️ فحص التوقيعات الرقمية</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">فحص التوقيعات</button></form></div>
            <div class="card"><h3>📐 إضافة هوامش بيضاء للملف</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">إضافة الهوامش</button></form></div>
            <div class="card"><h3>📊 حساب عدد الكلمات الكلي</h3><form action="#" method="POST" enctype="multipart/form-data"><input type="file" name="pdf" required><button type="submit">حساب الكلمات</button></form></div>
        </div>

        <div class="footer">
            جميع الحقوق محفوظة © 2026 | مالك الموقع: صهيب<br>
            <span style="color: #3498db;">سياسة الخصوصية | شروط الاستخدام | 📊 الزوار: 1453</span><br><br>
            <span style="color: #e67e22;">🌙 الوضع الليلي مفعل</span>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(FULL_GRID_TEMPLATE)

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
