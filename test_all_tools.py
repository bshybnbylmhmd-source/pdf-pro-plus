import io
import app as flask_app

client = flask_app.app.test_client()

# قائمة المسارات والأدوات الأساسية في المشروع
tools_to_test = [
    ('compress', 'sample1.pdf', {}),
    ('rotate_all', 'sample1.pdf', {}),
    ('rotate_90', 'sample1.pdf', {}),
    ('rotate_270', 'sample1.pdf', {}),
    ('reverse', 'sample1.pdf', {}),
    ('extract_text', 'sample1.pdf', {}),
    ('add_blank', 'sample1.pdf', {}),
    ('duplicate', 'sample1.pdf', {}),
    ('unlock', 'sample1.pdf', {}),
    ('split_all', 'sample1.pdf', {}),
    ('to_images', 'sample1.pdf', {}),
    ('crop', 'sample1.pdf', {}),
    ('watermark', 'sample1.pdf', {}),
    ('extract_images', 'sample1.pdf', {}),
    ('split_half', 'sample1.pdf', {}),
    ('clean', 'sample1.pdf', {}),
    ('duplicate_pages', 'sample1.pdf', {}),
    ('compress_images', 'sample1.pdf', {}),
    ('extract_urls', 'sample1.pdf', {}),
    ('n_up', 'sample1.pdf', {}),
    ('timestamp', 'sample1.pdf', {}),
    ('extract_tables', 'sample1.pdf', {}),
    ('optimize', 'sample1.pdf', {}),
    ('extract_fields', 'sample1.pdf', {}),
    ('redact', 'sample1.pdf', {}),
    ('repair', 'sample1.pdf', {}),
    ('strip_metadata', 'sample1.pdf', {}),
    ('signatures', 'sample1.pdf', {}),
    ('margins', 'sample1.pdf', {}),
    ('word_count', 'sample1.pdf', {}),
    ('info', 'sample1.pdf', {}),
    ('delete_page', 'sample1.pdf', {'page_num': '1'}),
    ('extract_single', 'sample1.pdf', {'page_num': '1'}),
    ('extract_range', 'sample1.pdf', {'start': '1', 'end': '2'}),
    ('scale', 'sample1.pdf', {'factor': '0.5'}),
    ('encrypt', 'sample1.pdf', {'password': '123'}),
    ('reorder', 'sample1.pdf', {'order': '2,1'}),
    ('rotate_single', 'sample1.pdf', {'page_num': '1', 'angle': '90'}),
    ('split_batch', 'sample1.pdf', {'batch_size': '1'}),
    ('duplicate_range', 'sample1.pdf', {'start': '1', 'end': '1'})
]

passed = 0
failed = 0

print("🚀 جاري فحص جميع الأدوات...")
for tool, filename, extra_data in tools_to_test:
    with open(filename, "rb") as f:
        data = {'file': (io.BytesIO(f.read()), filename)}
        data.update(extra_data)
        
        response = client.post(f'/process/{tool}', data=data, content_type='multipart/form-data')
        
        if response.status_code == 200:
            print(f"✅ الأداة [{tool}] تعمل بنجاح (Status: 200)")
            passed += 1
        else:
            print(f"❌ الأداة [{tool}] واجهت مشكلة (Status: {response.status_code})")
            failed += 1

# فحص الأدوات التي تتطلب ملفات متعددة (دمج ومقارنة)
multi_tools = ['merge', 'compare', 'compare_text']
for tool in multi_tools:
    with open("sample1.pdf", "rb") as f1, open("sample2.pdf", "rb") as f2:
        data = {
            'file': [
                (io.BytesIO(f1.read()), 'sample1.pdf'),
                (io.BytesIO(f2.read()), 'sample2.pdf')
            ]
        }
        response = client.post(f'/process/{tool}', data=data, content_type='multipart/form-data')
        if response.status_code == 200:
            print(f"✅ الأداة المتعددة [{tool}] تعمل بنجاح (Status: 200)")
            passed += 1
        else:
            print(f"❌ الأداة المتعددة [{tool}] واجهت مشكلة (Status: {response.status_code})")
            failed += 1

print("\n" + "="*30)
print(f"📊 النتيجة النهائية:")
print(f"إجمالي الأدوات الناجحة: {passed}")
print(f"إجمالي الأدوات التي تحتاج مراجعة: {failed}")
print("="*30)
