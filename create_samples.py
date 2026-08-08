from pypdf import PdfWriter
from PIL import Image

writer = PdfWriter()
writer.add_blank_page(width=300, height=300)
writer.add_blank_page(width=300, height=300)
with open("sample1.pdf", "wb") as f:
    writer.write(f)

writer2 = PdfWriter()
writer2.add_blank_page(width=300, height=300)
with open("sample2.pdf", "wb") as f:
    writer2.write(f)

img = Image.new('RGB', (200, 200), color = 'red')
img.save('sample_image.png')
print("تم إنشاء الملفات بنجاح!")
