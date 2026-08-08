import app as flask_app
import io

# إنشاء عميل اختبار لـ Flask
client = flask_app.app.test_client()

# قراءة ملف الاختبار sample1.pdf وتجربة إرساله لمسار الضغط
with open("sample1.pdf", "rb") as f:
    data = {'file': (f, 'sample1.pdf')}
    response = client.post('/process/compress', data=data, content_type='multipart/form-data')

print("كود الاستجابة (Status Code):", response.status_code)
if response.status_code == 200:
    print("✅ أداة الضغط تعمل بنجاح واستجابت بملف حجمه:", len(response.data), "بايت")
else:
    print("❌ حدث خطأ في الاستجابة:", response.data.decode('utf-8', errors='ignore'))
