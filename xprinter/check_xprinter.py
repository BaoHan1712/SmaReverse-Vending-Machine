import usb.core
import usb.util
from escpos import printer

def find_xprinter_and_print():
    # Quét USB
    devices = usb.core.find(find_all=True)

    for dev in devices:
        vid = dev.idVendor
        pid = dev.idProduct
        print(f"Found USB device: VID={hex(vid)}, PID={hex(pid)}")

        # Nếu đúng VID, PID của Xprinter thì in luôn
        # Ví dụ VID=0x1fc9, PID=0x2016
        if vid == 0x1fc9 and pid == 0x2016:
            p = printer.Usb(vid, pid)
            p.text("hello\n")
            p.cut()
            print("Đã in xong!")
            return

    print("Không tìm thấy máy in Xprinter!")

# Gọi hàm
find_xprinter_and_print()
