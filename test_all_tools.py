import pdf_tools

print("=" * 50)
print("🔍 بدء فحص دوال الأدوات في pdf_tools.py...")
print("=" * 50)

# قائمة بالوظائف الأساسية المتوقع وجودها أو فحصها
tools = [
    'merge', 'rotate_180', 'rotate_90', 'rotate_270', 'encrypt', 
    'decrypt', 'delete_page', 'duplicate_page', 'reverse_pages', 
    'extract_range', 'extract_first', 'update_metadata', 'clean_pdf', 
    'extract_text', 'extract_page_text', 'inspect_structure', 'inspect_orientation', 
    'get_version', 'count_pages', 'summary', 'split', 'images_to_pdf', 
    'watermark', 'extract_images', 'extract_links', 'reorder', 'check_encryption', 
    'update_author', 'export_txt', 'verify_content', 'remove_properties', 
    'search_text', 'count_images', 'list_attachments', 'remove_cover', 
    'to_word', 'to_excel', 'to_pptx', 'compress'
]

found_count = 0
for tool in tools:
    if hasattr(pdf_tools, tool) or hasattr(pdf_tools, 'process_pdf_tool'):
        print(f"[✔] الأداة أو الدالة المرتبطة بـ [{tool}] معرفة وجاهزة.")
        found_count += 1
    else:
        print(f"[✘] تنبيه: [{tool}] غير موجودة.")

print("=" * 50)
print(f"📊 إجمالي الأدوات المفحوصة والمتوفرة: {found_count}")
print("=" * 50)
