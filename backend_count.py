from get_library import *
from toUart import *

class YOLOProcessor(threading.Thread):
    """
    A dedicated thread to handle YOLO model processing to avoid freezing the GUI.
    """
    def __init__(self, video_path, model_path, output_queue):
        super().__init__(daemon=True)
        self.video_path = video_path
        self.model_path = model_path
        self.output_queue = output_queue
        self.running = True

        #--- Khởi tạo truyền gói tin---
        self.send_uart = ESP32_UART(port='COM4', baudrate=9600)

    def run(self):
        """Main loop for video processing."""
        try:
            model = YOLO(self.model_path)
        except Exception as e:
            print(f"⚠️ Lỗi tải model: {e}")
            return

        try:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                raise IOError(f"Không thể mở video tại: {self.video_path}")
        except Exception as e:
            print(f"⚠️ Lỗi mở video: {e}")
            return
        
        track_history = {}
        line = [10, 190, 630, 190]  # Adjust line position if needed
        count_set = set()
        total_label_0 = 0
        total_label_1 = 0

        while self.running and cap.isOpened():
            success, frame = cap.read()
            if not success:
                if isinstance(self.video_path, str):
                    print("⚠️ Hết video.")
                    break 
                continue

            frame = cv2.resize(frame, (640, 480))
            results = model.track(source=frame, imgsz=640, conf=0.45, verbose=False, device="0", persist=True, tracker=r'tracking/bytetrack.yaml')[0]
            
            cv2.line(frame, (line[0], line[1]), (line[2], line[3]), (0, 255, 255), 3)
            
            if results.boxes and results.boxes.is_track:
                boxes = results.boxes.xywh.cpu().numpy()
                track_ids = results.boxes.id.int().cpu().tolist()
                cls_ids = results.boxes.cls.int().cpu().tolist()  

                frame = results.plot(boxes=True, color_mode='instance')

                for box, track_id, cls_id in zip(boxes, track_ids, cls_ids):
                    x, y, w, h = box
                    center_x = int(x)
                    center_y = int(y)
                    cv2.circle(frame, (center_x, center_y), 3, (0, 255, 0), -1)  

                    if line[1] - 10 < center_y < line[1] + 10:
                        if track_id not in count_set:
                            count_set.add(track_id)

                            if cls_id == 0:
                                total_label_0 += 1
                                self.send_uart.send_packet(1)  
                            elif cls_id == 1:
                                total_label_1 += 1
                                self.send_uart.send_packet(2)
                            
                            cv2.line(frame, (line[0], line[1]), (line[2], line[3]), (0, 0, 255), 3)
                            
            cv2.putText(frame, f"bottle: {total_label_0}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            cv2.putText(frame, f"can: {total_label_1}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            try:
                self.output_queue.put_nowait((frame, total_label_0, total_label_1))
            except queue.Full:
                pass
        
        cap.release()
        print("Luồng YOLO đã dừng.")

    def stop(self):
        """Signals the thread to stop."""
        self.running = False


# ===============================================================
# CLASS IN PHIẾU
# ===============================================================

try:
    import win32print
    IS_WINDOWS = True
except ImportError:
    IS_WINDOWS = False
    print("Cảnh báo: Thư viện 'pywin32' không được tìm thấy. Chức năng in sẽ không hoạt động.")
    print("Để cài đặt, chạy lệnh: pip install pywin32")


class ReceiptPrinter:
    """
    Một class chuyên dụng để xử lý việc tạo và in phiếu tích điểm.
    """
    def __init__(self):
        self.is_ready = IS_WINDOWS
        if not self.is_ready:
            print("Cảnh báo: Chức năng in không có sẵn (chỉ hỗ trợ Windows và yêu cầu pywin32).")

    def print_receipt(self, user_name, bottles, cans, points):
        if not self.is_ready:
            return False, "Chức năng in không có sẵn trên hệ điều hành này hoặc do thiếu thư viện."

        try:
            now = datetime.datetime.now()
            date_str = now.strftime("%d/%m/%Y")
            time_str = now.strftime("%H:%M:%S")

            receipt_content = (
                "   PHIEU TICH DIEM TAI CHE\n"
                "--------------------------------\n"
                f"Khach hang: {user_name}\n"
                f"Ngay: {date_str}\n"
                f"Gio: {time_str}\n"
                "--------------------------------\n"
                "So luong vat pham:\n"
                f"- Chai nhua:      {bottles}\n"
                f"- Lon kim loai:   {cans}\n"
                "--------------------------------\n"
                # f"TONG DIEM TICH LUY: {points}\n\n"
                "Cam on ban da chung tay bao ve\n"
                "         moi truong!\n\n\n."
            )

            printer_name = win32print.GetDefaultPrinter()
            h_printer = win32print.OpenPrinter(printer_name)
            try:
                h_job = win32print.StartDocPrinter(h_printer, 1, ("Phieu Tich Diem", None, "RAW"))
                try:
                    win32print.StartPagePrinter(h_printer)
                    win32print.WritePrinter(h_printer, receipt_content.encode('utf-8'))
                    win32print.EndPagePrinter(h_printer)
                finally:
                    win32print.EndDocPrinter(h_printer)
            finally:
                win32print.ClosePrinter(h_printer)

            success_message = f"Đã gửi phiếu của '{user_name}' đến máy in thành công."
            print(success_message)
            return True, success_message

        except Exception as e:
            error_message = f"Không thể in phiếu. Đã xảy ra lỗi:\n{e}\n\nVui lòng kiểm tra lại kết nối máy in."
            print(error_message)
            return False, error_message