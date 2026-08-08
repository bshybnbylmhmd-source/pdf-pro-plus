import io
import app as flask_app

client = flask_app.app.test_client()

with open("sample1.pdf", "rb") as f1, open("sample2.pdf", "rb") as f2:
    data = {
        'file': [
            (io.BytesIO(f1.read()), 'sample1.pdf'),
            (io.BytesIO(f2.read()), 'sample2.pdf')
        ]
    }
    response = client.post('/process/merge', data=data, content_type='multipart/form-data')

print("كود الاستجابة للدمج:", response.status_code)
if response.status_code == 200:
    print("✅ أداة الدمج تعمل بنجاح واستجابت بملف حجمه:", len(response.data), "بايت")
else:
    print("❌ حدث خطأ:", response.data.decode('utf-8', errors='ignore'))
