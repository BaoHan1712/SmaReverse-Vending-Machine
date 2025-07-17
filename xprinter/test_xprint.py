import win32print
import win32ui

printer_name = "XP-80C"

printer = win32print.OpenPrinter(printer_name)
printer_info = win32print.GetPrinter(printer, 2)

# Tạo DC để gửi dữ liệu in
pdc = win32ui.CreateDC()
pdc.CreatePrinterDC(printer_name)
pdc.StartDoc("Print Test - Han Quoc Bao")
pdc.StartPage()

# Nội dung (mỗi dòng cách nhau bằng \n)
text = "Hàn Quốc Bảo hẹ hẹ hẹ hẹ \n\n chịu rồi \n\n ."

# Tách ra từng dòng
lines = text.split("\n")
x = 100
y = 100
line_height = 30  # Khoảng cách giữa các dòng 

# In từng dòng
for line in lines:
    pdc.TextOut(x, y, line)
    y += line_height
# Chừa giấy trắng ở cuối
for i in range(10):
    pdc.TextOut(x, y + i * line_height, "")

pdc.EndPage()
pdc.EndDoc()
pdc.DeleteDC()
win32print.ClosePrinter(printer)

print("✅ Đã in xong tên: Hàn Quốc Bảo ")
