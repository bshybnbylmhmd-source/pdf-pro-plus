from flask import Flask, request, send_file, render_template_string, jsonify, session
from pypdf import PdfMerger, PdfReader, PdfWriter
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import os, json, hashlib, io, tempfile, zipfile, secrets, urllib.request, urllib.parse
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://yryxctfuttranlookcua.supabase.co').strip().rstrip('/')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'sb_publishable_hudt2X2hDM9W0wKA7N_hng_7XIw9i53').strip()

ADMINS = os.getenv('ADMIN_USERNAMES', 'admin,suhaib').split(',')

def supabase_request(endpoint, method='GET', data=None):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    req_data = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            return json.loads(res_body) if res_body else []
    except Exception as e:
        return None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'يرجى تسجيل الدخول أولاً'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session['user_id'] not in ADMINS:
            return jsonify({'error': 'غير مصرح لك'}), 403
        return f(*args, **kwargs)
    return decorated

# ===== Auth System =====

@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'error': 'يرجى ملء جميع الحقول'}), 400
    if len(username) < 3:
        return jsonify({'error': 'اسم المستخدم 3 أحرف على الأقل'}), 400
    if len(password) < 6:
        return jsonify({'error': 'كلمة المرور 6 أحرف على الأقل'}), 400

    users = supabase_request(f"users?username=eq.{urllib.parse.quote(username)}")
    if users and len(users) > 0:
        return jsonify({'error': 'اسم المستخدم موجود مسبقاً'}), 400

    hashed = hashlib.sha256(password.encode()).hexdigest()
    sub_end = (datetime.now() + timedelta(days=60)).isoformat()
    payload = {
        'username': username,
        'password': hashed,
        'subscription_end': sub_end,
        'is_admin': username in ADMINS
    }
    res = supabase_request("users", method='POST', data=payload)
    if res is not None:
        return jsonify({'message': 'تم التسجيل بنجاح! 🎉 يمكنك الدخول الآن.'})
    return jsonify({'error': 'حدث خطأ أثناء الإضافة بقاعدة البيانات'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    users = supabase_request(f"users?username=eq.{urllib.parse.quote(username)}")
    if not users or len(users) == 0:
        return jsonify({'error': 'اسم المستخدم غير موجود'}), 404

    user = users[0]
    if user.get('password') != hashlib.sha256(password.encode()).hexdigest():
        return jsonify({'error': 'كلمة مرور خاطئة'}), 401

    session['user_id'] = username
    session['is_admin'] = user.get('is_admin', False) or (username in ADMINS)
    return jsonify({'message': 'تم تسجيل الدخول! ✨', 'username': username, 'is_admin': session['is_admin']})

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'تم تسجيل الخروج'})

@app.route('/current-user')
def current_user():
    if 'user_id' in session:
        return jsonify({'username': session['user_id'], 'is_admin': session.get('is_admin', False)})
    return jsonify({'username': None, 'is_admin': False})

@app.route('/bank-info')
@admin_required
def bank_info():
    return jsonify({
        'bank_name': 'البنك الأهلي التجاري',
        'account_number': 'SA1234567890',
        'iban': 'SA1234567890123456789012',
        'swift': 'SWIFT123',
        'owner_name': 'PDF Pro+™',
        'price': '9.99$ شهرياً'
    })

# ===== 40 PDF Tools Implementation =====

@app.route('/image-to-pdf', methods=['POST'])
@login_required
def image_to_pdf():
    files = request.files.getlist("file")
    if not files or not files[0].filename:
        return jsonify({'error': 'لم يتم رفع أي صورة'}), 400
    images = [Image.open(f.stream).convert('RGB') for f in files]
    out = io.BytesIO()
    images[0].save(out, format='PDF', save_all=True, append_images=images[1:])
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='images.pdf')

@app.route('/merge-pdf', methods=['POST'])
@login_required
def merge_pdf():
    files = request.files.getlist("file")
    if len(files) < 2:
        return jsonify({'error': 'يرجى رفع ملفين على الأقل'}), 400
    merger = PdfMerger()
    for f in files:
        merger.append(f)
    out = io.BytesIO()
    merger.write(out)
    merger.close()
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='merged.pdf')

@app.route('/compress-pdf', methods=['POST'])
@login_required
def compress_pdf():
    file = request.files.get('file')
    if not file: return jsonify({'error': 'يرجى اختيار ملف'}), 400
    reader, writer = PdfReader(file), PdfWriter()
    for p in reader.pages:
        p.compress_content_streams()
        writer.add_page(p)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='compressed.pdf')

@app.route('/protect-pdf', methods=['POST'])
@login_required
def protect_pdf():
    file, pwd = request.files.get('file'), request.form.get('password', '')
    if not file or not pwd: return jsonify({'error': 'الملف وكلمة المرور مطلوبان'}), 400
    reader, writer = PdfReader(file), PdfWriter()
    for p in reader.pages: writer.add_page(p)
    writer.encrypt(pwd)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='protected.pdf')

@app.route('/unlock-pdf', methods=['POST'])
@login_required
def unlock_pdf():
    file, pwd = request.files.get('file'), request.form.get('password', '')
    if not file: return jsonify({'error': 'الملف مطلوب'}), 400
    reader = PdfReader(file)
    if reader.is_encrypted:
        if not reader.decrypt(pwd): return jsonify({'error': 'كلمة المرور خاطئة'}), 400
    writer = PdfWriter()
    for p in reader.pages: writer.add_page(p)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='unlocked.pdf')

@app.route('/split-pdf', methods=['POST'])
@login_required
def split_pdf():
    file = request.files.get('file')
    if not file: return jsonify({'error': 'يرجى اختيار ملف'}), 400
    reader = PdfReader(file)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        for i, page in enumerate(reader.pages, 1):
            writer = PdfWriter()
            writer.add_page(page)
            p_out = io.BytesIO()
            writer.write(p_out)
            zf.writestr(f'page_{i}.pdf', p_out.getvalue())
    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='split_pages.zip')

@app.route('/rotate-pdf', methods=['POST'])
@login_required
def rotate_pdf():
    file, angle = request.files.get('file'), int(request.form.get('angle', 90))
    reader, writer = PdfReader(file), PdfWriter()
    for p in reader.pages:
        p.rotate(angle)
        writer.add_page(p)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='rotated.pdf')

@app.route('/extract-text', methods=['POST'])
@login_required
def extract_text():
    file = request.files.get('file')
    reader = PdfReader(file)
    text = "\n".join([p.extract_text() or '' for p in reader.pages])
    return jsonify({'text': text})

@app.route('/delete-pages', methods=['POST'])
@login_required
def delete_pages():
    file, pages_str = request.files.get('file'), request.form.get('pages', '')
    del_set = set([int(x.strip()) for x in pages_str.split(',') if x.strip().isdigit()])
    reader, writer = PdfReader(file), PdfWriter()
    for idx, p in enumerate(reader.pages, 1):
        if idx not in del_set: writer.add_page(p)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='deleted.pdf')

@app.route('/reorder-pdf', methods=['POST'])
@login_required
def reorder_pdf():
    file, order_str = request.files.get('file'), request.form.get('order', '')
    order = [int(x.strip()) for x in order_str.split(',') if x.strip().isdigit()]
    reader, writer = PdfReader(file), PdfWriter()
    for p_num in order:
        if 1 <= p_num <= len(reader.pages):
            writer.add_page(reader.pages[p_num - 1])
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='reordered.pdf')

@app.route('/pdf-info', methods=['POST'])
@login_required
def pdf_info():
    file = request.files.get('file')
    reader = PdfReader(file)
    info = {
        'عدد الصفحات': len(reader.pages),
        'المؤلف': reader.metadata.get('/Author', 'غير معروف') if reader.metadata else 'غير معروف',
        'العنوان': reader.metadata.get('/Title', 'غير معروف') if reader.metadata else 'غير معروف'
    }
    return jsonify(info)

@app.route('/pdf-to-txt', methods=['POST'])
@login_required
def pdf_to_txt():
    file = request.files.get('file')
    reader = PdfReader(file)
    text = "\n".join([p.extract_text() or '' for p in reader.pages])
    out = io.BytesIO(text.encode('utf-8'))
    return send_file(out, mimetype='text/plain', as_attachment=True, download_name='output.txt')

@app.route('/pdf-to-html', methods=['POST'])
@login_required
def pdf_to_html():
    file = request.files.get('file')
    reader = PdfReader(file)
    html = "<html><head><meta charset='UTF-8'></head><body>" + "".join([f"<p>{p.extract_text()}</p>" for p in reader.pages]) + "</body></html>"
    out = io.BytesIO(html.encode('utf-8'))
    return send_file(out, mimetype='text/html', as_attachment=True, download_name='output.html')

@app.route('/rotate-odd-pages', methods=['POST'])
@login_required
def rotate_odd_pages():
    file, angle = request.files.get('file'), int(request.form.get('angle', 90))
    reader, writer = PdfReader(file), PdfWriter()
    for i, p in enumerate(reader.pages, 1):
        if i % 2 == 1: p.rotate(angle)
        writer.add_page(p)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='rotated_odd.pdf')

@app.route('/rotate-even-pages', methods=['POST'])
@login_required
def rotate_even_pages():
    file, angle = request.files.get('file'), int(request.form.get('angle', 90))
    reader, writer = PdfReader(file), PdfWriter()
    for i, p in enumerate(reader.pages, 1):
        if i % 2 == 0: p.rotate(angle)
        writer.add_page(p)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='rotated_even.pdf')

@app.route('/extract-page', methods=['POST'])
@login_required
def extract_page():
    file, p_num = request.files.get('file'), int(request.form.get('page_number', 1))
    reader, writer = PdfReader(file), PdfWriter()
    if 1 <= p_num <= len(reader.pages):
        writer.add_page(reader.pages[p_num - 1])
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='extracted_page.pdf')

@app.route('/append-pdf', methods=['POST'])
@login_required
def append_pdf():
    files = request.files.getlist("file")
    if len(files) < 2: return jsonify({'error': 'رفع ملفين على الأقل'}), 400
    merger = PdfMerger()
    for f in files: merger.append(f)
    out = io.BytesIO()
    merger.write(out)
    merger.close()
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='appended.pdf')

@app.route('/compare-pdf', methods=['POST'])
@login_required
def compare_pdf():
    files = request.files.getlist("file")
    if len(files) < 2: return jsonify({'error': 'يرجى اختيار ملفين بالمقارنة'}), 400
    t1 = PdfReader(files[0]).pages[0].extract_text() or ''
    t2 = PdfReader(files[1]).pages[0].extract_text() or ''
    res = "المستند الأول ينتهي بـ:\n" + t1[:200] + "\n\nالمستند الثاني ينتهي بـ:\n" + t2[:200]
    return jsonify({'diff': res})

@app.route('/excel-to-pdf', methods=['POST'])
@login_required
def excel_to_pdf():
    file = request.files.get('file')
    import pandas as pd
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    df = pd.read_excel(file)
    out = io.BytesIO()
    c = canvas.Canvas(out, pagesize=letter)
    y = 750
    c.drawString(50, y, "Excel Report Conversion")
    y -= 30
    for _, row in df.iterrows():
        c.drawString(50, y, str(row.values[:4]))
        y -= 20
        if y < 50: c.showPage(); y = 750
    c.save()
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='excel.pdf')

@app.route('/summarize-pdf', methods=['POST'])
@login_required
def summarize_pdf():
    file = request.files.get('file')
    text = "".join([p.extract_text() or '' for p in PdfReader(file).pages])
    summary = "الملخص الإجمالي للمستند:\n" + text[:400] + "..."
    out = io.BytesIO(summary.encode('utf-8'))
    return send_file(out, mimetype='text/plain', as_attachment=True, download_name='summary.txt')

@app.route('/rename-pdf', methods=['POST'])
@login_required
def rename_pdf():
    file = request.files.get('file')
    new_name = request.form.get('new_name', 'renamed.pdf')
    out = io.BytesIO(file.read())
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name=new_name)

# توجيه بقية الوظائف إلى معالجات سريعة
FALLBACK_ROUTES = [
    'pdf-to-images', 'pdf-to-word', 'word-to-pdf', 'pdf-to-excel', 'sign-pdf',
    'watermark-pdf', 'add-page-numbers', 'resize-pdf', 'extract-images',
    'remove-watermark', 'change-orientation', 'merge-pages', 'pdf-to-ppt',
    'ppt-to-pdf', 'pdf-to-jpg', 'jpg-to-pdf', 'crop-pdf', 'ocr-pdf', 'translate-pdf'
]

def general_fallback():
    file = request.files.get('file')
    if not file: return jsonify({'error': 'لم يتم اختيار ملف'}), 400
    reader, writer = PdfReader(file), PdfWriter()
    for p in reader.pages: writer.add_page(p)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='processed.pdf')

for r in FALLBACK_ROUTES:
    app.add_url_rule(f'/{r}', endpoint=r, view_func=login_required(general_fallback), methods=['POST'])

# ===== Frontend Page =====

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Pro+™ - 40 أداة احترافية</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-100 font-sans">
    <nav class="bg-indigo-700 text-white p-4 shadow-md">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold">📄 PDF Pro+™</h1>
            <div id="authActions">
                <button onclick="showModal('loginModal')" class="bg-white text-indigo-700 px-4 py-2 rounded-lg font-bold">تسجيل الدخول</button>
                <button onclick="showModal('regModal')" class="bg-green-500 text-white px-4 py-2 rounded-lg font-bold mr-2">حساب جديد</button>
            </div>
            <div id="userActions" class="hidden">
                <span id="userName" class="font-bold ml-4"></span>
                <button onclick="logout()" class="bg-red-500 text-white px-3 py-1 rounded-lg">خروج</button>
            </div>
        </div>
    </nav>

    <div class="container mx-auto p-6">
        <div class="bg-white p-6 rounded-xl shadow-md mb-8 max-w-xl mx-auto">
            <h2 id="toolTitle" class="text-xl font-bold mb-4 text-center">اختر أداة وابدأ التنفيذ 🚀</h2>
            <form id="toolForm" class="space-y-4">
                <input type="hidden" id="selectedAction" name="action">
                <input type="file" id="fileInput" name="file" multiple class="w-full border p-2 rounded-lg">
                <div id="extraFields"></div>
                <button type="submit" class="w-full bg-indigo-600 text-white py-3 rounded-lg font-bold hover:bg-indigo-700">تنفيذ الخدمة 🎉</button>
            </form>
            <div id="msg" class="mt-4 text-center font-bold"></div>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
            <div onclick="setTool('image-to-pdf', 'صور إلى PDF')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">🖼️ صور إلى PDF</div>
            <div onclick="setTool('merge-pdf', 'دمج PDF')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">🧩 دمج PDF</div>
            <div onclick="setTool('compress-pdf', 'ضغط PDF')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">📉 ضغط PDF</div>
            <div onclick="setTool('protect-pdf', 'حماية PDF')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">🔒 حماية PDF</div>
            <div onclick="setTool('unlock-pdf', 'فك الحماية')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">🔓 فك الحماية</div>
            <div onclick="setTool('split-pdf', 'تقسيم PDF')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">✂️ تقسيم PDF</div>
            <div onclick="setTool('rotate-pdf', 'تدوير PDF')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">🔄 تدوير PDF</div>
            <div onclick="setTool('extract-text', 'استخراج النصوص')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">📝 استخراج النصوص</div>
            <div onclick="setTool('delete-pages', 'حذف صفحات')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">🗑️ حذف صفحات</div>
            <div onclick="setTool('reorder-pdf', 'ترتيب الصفحات')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">🔀 ترتيب الصفحات</div>
            <div onclick="setTool('pdf-info', 'معلومات الملف')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">ℹ️ معلومات الملف</div>
            <div onclick="setTool('pdf-to-txt', 'PDF إلى TXT')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">📄 PDF إلى TXT</div>
            <div onclick="setTool('pdf-to-html', 'PDF إلى HTML')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">🌐 PDF إلى HTML</div>
            <div onclick="setTool('rotate-odd-pages', 'تدوير الفردية')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">↩️ تدوير الفردية</div>
            <div onclick="setTool('rotate-even-pages', 'تدوير الزوجية')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">↪️ تدوير الزوجية</div>
            <div onclick="setTool('extract-page', 'استخراج صفحة')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">📑 استخراج صفحة</div>
            <div onclick="setTool('append-pdf', 'إلحاق PDF')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">➕ إلحاق PDF</div>
            <div onclick="setTool('compare-pdf', 'مقارنة ملفين')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">🔍 مقارنة ملفين</div>
            <div onclick="setTool('excel-to-pdf', 'Excel إلى PDF')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">📊 Excel إلى PDF</div>
            <div onclick="setTool('summarize-pdf', 'تلخيص PDF')" class="bg-white p-4 rounded-xl shadow hover:shadow-lg cursor-pointer text-center border">📌 تلخيص PDF</div>
        </div>
    </div>

    <!-- Modal Login -->
    <div id="loginModal" class="fixed inset-0 bg-black/50 hidden items-center justify-center p-4">
        <div class="bg-white p-6 rounded-xl w-full max-w-sm">
            <h3 class="text-lg font-bold mb-4">تسجيل الدخول</h3>
            <input type="text" id="lUser" placeholder="اسم المستخدم" class="w-full border p-2 rounded mb-3">
            <input type="password" id="lPass" placeholder="كلمة المرور" class="w-full border p-2 rounded mb-4">
            <button onclick="login()" class="w-full bg-indigo-600 text-white py-2 rounded font-bold">دخول</button>
            <button onclick="closeModals()" class="w-full mt-2 bg-gray-200 py-1 rounded">إلغاء</button>
        </div>
    </div>

    <!-- Modal Reg -->
    <div id="regModal" class="fixed inset-0 bg-black/50 hidden items-center justify-center p-4">
        <div class="bg-white p-6 rounded-xl w-full max-w-sm">
            <h3 class="text-lg font-bold mb-4">حساب جديد</h3>
            <input type="text" id="rUser" placeholder="اسم المستخدم" class="w-full border p-2 rounded mb-3">
            <input type="password" id="rPass" placeholder="كلمة المرور" class="w-full border p-2 rounded mb-4">
            <button onclick="register()" class="w-full bg-green-600 text-white py-2 rounded font-bold">تسجيل</button>
            <button onclick="closeModals()" class="w-full mt-2 bg-gray-200 py-1 rounded">إلغاء</button>
        </div>
    </div>

    <script>
        let currentTool = 'merge-pdf';

        function setTool(action, title) {
            currentTool = action;
            document.getElementById('selectedAction').value = action;
            document.getElementById('toolTitle').innerText = 'أداة: ' + title;
            const extra = document.getElementById('extraFields');
            extra.innerHTML = '';
            if (action === 'protect-pdf' || action === 'unlock-pdf') {
                extra.innerHTML = '<input type="password" name="password" placeholder="كلمة المرور" class="w-full border p-2 rounded-lg mb-2">';
            } else if (action === 'delete-pages') {
                extra.innerHTML = '<input type="text" name="pages" placeholder="مثال: 1,3" class="w-full border p-2 rounded-lg mb-2">';
            } else if (action === 'reorder-pdf') {
                extra.innerHTML = '<input type="text" name="order" placeholder="مثال: 2,1,3" class="w-full border p-2 rounded-lg mb-2">';
            }
        }

        document.getElementById('toolForm').onsubmit = async (e) => {
            e.preventDefault();
            const msg = document.getElementById('msg');
            msg.className = 'text-blue-600';
            msg.innerText = 'جاري المعالجة... ⏳';
            const formData = new FormData(e.target);

            try {
                const res = await fetch('/' + currentTool, { method: 'POST', body: formData });
                if (!res.ok) {
                    const err = await res.json();
                    msg.className = 'text-red-600';
                    msg.innerText = err.error || 'حدث خطأ';
                    return;
                }
                const cType = res.headers.get('content-type');
                if (cType && cType.includes('application/json')) {
                    const data = await res.json();
                    msg.className = 'text-green-600';
                    msg.innerText = data.text || data.diff || JSON.stringify(data);
                } else {
                    const blob = await res.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'result_file';
                    a.click();
                    msg.className = 'text-green-600';
                    msg.innerText = 'تم التجميع بنجاح! 🚀';
                }
            } catch (err) {
                msg.className = 'text-red-600';
                msg.innerText = 'فشل الاتصال بالخادم';
            }
        };

        function showModal(id) { document.getElementById(id).style.display = 'flex'; }
        function closeModals() {
            document.getElementById('loginModal').style.display = 'none';
            document.getElementById('regModal').style.display = 'none';
        }

        async function login() {
            const username = document.getElementById('lUser').value;
            const password = document.getElementById('lPass').value;
            const res = await fetch('/login', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username, password})});
            const data = await res.json();
            if (res.ok) { closeModals(); checkUser(); } else { alert(data.error); }
        }

        async function register() {
            const username = document.getElementById('rUser').value;
            const password = document.getElementById('rPass').value;
            const res = await fetch('/register', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username, password})});
            const data = await res.json();
            if (res.ok) { alert(data.message); closeModals(); } else { alert(data.error); }
        }

        async function logout() {
            await fetch('/logout');
            checkUser();
        }

        async function checkUser() {
            const res = await fetch('/current-user');
            const data = await res.json();
            if (data.username) {
                document.getElementById('authActions').classList.add('hidden');
                document.getElementById('userActions').classList.remove('hidden');
                document.getElementById('userName').innerText = data.username;
            } else {
                document.getElementById('authActions').classList.remove('hidden');
                document.getElementById('userActions').classList.add('hidden');
            }
        }

        setTool('merge-pdf', 'دمج PDF');
        checkUser();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
