import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import random
import re
import threading
import queue
from ultralytics import YOLO
import os

# --- Color Palette and Theme ---
PRIMARY_GREEN = "#388e3c"      # Xanh lá cây non
SECONDARY_GREEN = "#b7e4c7"    # Xanh lá nhạt
YELLOW = "#f9f871"             # Vàng nhạt
WHITE = "#f6fff8"              # Trắng xanh nhẹ
DARK_GREEN = "#1B5E20"         # A darker green for text
BORDER_RADIUS = 16              # Bo góc lớn hơn

class SplashScreen(ctk.CTkToplevel):
    """
    Cửa sổ chờ (Splash Screen) hiển thị trước khi ứng dụng chính khởi động.
    Kế thừa từ CTkToplevel để hoạt động như một cửa sổ con.
    """
    def __init__(self, master):
        super().__init__(master)

        # --- Cấu hình cửa sổ ---
        width, height = 450, 350
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        
        self.geometry(f'{width}x{height}+{int(x)}+{int(y)}')
        self.overrideredirect(True) # Bỏ thanh tiêu đề
        self.configure(fg_color=WHITE)
        self.transient(master)
        self.lift()

        # --- Logo ---
        try:
            logo_path = os.path.join("image", "logo.png")
            logo_img = Image.open(logo_path)
            logo_ctk = ctk.CTkImage(light_image=logo_img, size=(200, 200))
            logo_label = ctk.CTkLabel(self, image=logo_ctk, text="")
            logo_label.pack(pady=(30, 15))
        except FileNotFoundError:
            print("Warning: 'image/logo.png' not found for splash screen.")
            logo_label = ctk.CTkLabel(self, text="🌿", font=ctk.CTkFont(size=100))
            logo_label.pack(pady=(30, 15))

        # --- Dòng chữ đang tải ---
        loading_label = ctk.CTkLabel(self, text="Đang khởi tạo hệ thống...", font=ctk.CTkFont(size=16), text_color=DARK_GREEN)
        loading_label.pack()

        # --- Thanh tiến trình ---
        progress_bar = ctk.CTkProgressBar(self, orientation='horizontal', mode='indeterminate', progress_color=PRIMARY_GREEN)
        progress_bar.pack(pady=15, padx=50, fill="x")
        progress_bar.start()

class CustomDialog(ctk.CTkToplevel):
    """
    Một cửa sổ hộp thoại tuỳ chỉnh dùng để xác nhận hoặc hiển thị thông tin.
    """
    def __init__(self, master, title, message, is_confirm=False, command=None):
        super().__init__(master)
        self.title(title)
        master_x, master_y = master.winfo_x(), master.winfo_y()
        master_width, master_height = master.winfo_width(), master.winfo_height()
        dialog_width, dialog_height = 400, 170
        x = master_x + (master_width - dialog_width) // 2
        y = master_y + (master_height - dialog_height) // 2
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.transient(master)
        self.grab_set()
        self.configure(fg_color=SECONDARY_GREEN)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=BORDER_RADIUS)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        label = ctk.CTkLabel(main_frame, text=message, font=ctk.CTkFont(size=15), wraplength=360, text_color=DARK_GREEN)
        label.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=15, pady=15)
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, columnspan=2, sticky="s", pady=(10,10))

        if is_confirm:
            confirm_button = ctk.CTkButton(button_frame, text="Xác nhận", command=lambda: self._confirm(command), fg_color=PRIMARY_GREEN, hover_color=DARK_GREEN, corner_radius=BORDER_RADIUS)
            confirm_button.pack(side="right", padx=(10,0))
            cancel_button = ctk.CTkButton(button_frame, text="Hủy", command=self.destroy, fg_color=YELLOW, hover_color="#e6e600", text_color="black", corner_radius=BORDER_RADIUS)
            cancel_button.pack(side="right")
        else:
            ok_button = ctk.CTkButton(button_frame, text="OK", command=self.destroy, width=100, fg_color=PRIMARY_GREEN, hover_color=DARK_GREEN, corner_radius=BORDER_RADIUS)
            ok_button.pack()

    def _confirm(self, command):
        if command:
            command()
        self.destroy()

class YOLOProcessor(threading.Thread):
    """Luồng riêng để xử lý YOLO không làm treo giao diện."""
    def __init__(self, video_path, model_path, output_queue):
        super().__init__(daemon=True)
        self.video_path, self.model_path, self.output_queue = video_path, model_path, output_queue
        self.running = True

    def run(self):
        try:
            model = YOLO(self.model_path)
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened(): raise IOError(f"Không thể mở video tại: {self.video_path}")
        except Exception as e:
            print(f"⚠️ Lỗi khởi tạo tài nguyên: {e}")
            return
        
        line = [10, 240, 630, 240]
        count_set = set()
        total_count = 0
        
        while self.running and cap.isOpened():
            success, frame = cap.read()
            if not success:
                if isinstance(self.video_path, str):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    count_set.clear()
                    continue
                else: break

            frame = cv2.resize(frame, (640, 480))
            results = model.track(source=frame, imgsz=640, conf=0.4, verbose=False, persist=True, tracker='tracking/bytetrack.yaml')[0]

            if results.boxes and results.boxes.is_track:
                frame = results.plot(boxes=True, line_width=2)
                cv2.line(frame, (line[0], line[1]), (line[2], line[3]), (0, 255, 255, 0.5), 2)
                for box, track_id in zip(results.boxes.xywh.cpu().numpy(), results.boxes.id.int().cpu().tolist()):
                    if line[1] - 15 < int(box[1]) < line[1] + 15 and track_id not in count_set:
                        count_set.add(track_id)
                        total_count += 1
            
            try: self.output_queue.put_nowait((frame, total_count))
            except queue.Full: pass
        cap.release()
        print("Luồng YOLO đã dừng.")

    def stop(self):
        self.running = False

class RecyclingApp(ctk.CTk):
    """Ứng dụng giao diện chính cho hệ thống tái chế."""
    def __init__(self):
        super().__init__()
        self.withdraw() # Ẩn cửa sổ chính ban đầu
        self.title("Vì môi trường xanh sạch đẹp - Ươm mầm cây xanh non")
        self.geometry("1350x700")
        self._set_appearance_mode("light")
        self.configure(fg_color=SECONDARY_GREEN)

        # --- Khởi tạo Splash Screen ---
        self.splash = SplashScreen(self)

        # --- Data Attributes ---
        self.bottles_counted, self.cans_counted, self.total_points = 0, 0, 0
        self.current_yolo_total, self.last_confirmed_count = 0, 0

        # --- Threading and Queue Setup ---
        self.yolo_queue = queue.Queue(maxsize=2)
        video_source = r"data/video2.avi" # Hoặc 0 cho webcam
        self.yolo_thread = YOLOProcessor(
            video_path=video_source,
            model_path="model/yolo11n.pt",
            output_queue=self.yolo_queue
        )
        self.yolo_thread.start()

        # --- UI Setup ---
        self.grid_columnconfigure(0, weight=45)
        self.grid_columnconfigure(1, weight=55)
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.setup_left_frame()

        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.setup_right_frame()

        # --- Lên lịch hiển thị cửa sổ chính ---
        self.after(3000, self.show_main_window)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_main_window(self):
        """Hủy splash screen và hiển thị cửa sổ chính."""
        if self.splash:
            self.splash.destroy()
            self.splash = None
        self.deiconify() # Hiển thị lại cửa sổ chính
        self.update_camera_feed() # Bắt đầu vòng lặp cập nhật camera

    def setup_left_frame(self):
        """Thiết lập các widget cho khung bên trái."""
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        header_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        header_container.grid(row=0, column=0, pady=(0, 15), sticky="ew")
        header_container.grid_columnconfigure(1, weight=1)

        try:
            logo_path = os.path.join("image", "logo.png")
            logo_img = Image.open(logo_path)
            logo_ctk = ctk.CTkImage(light_image=logo_img, size=(70, 70))
            self.logo_label = ctk.CTkLabel(header_container, image=logo_ctk, text="")
            self.logo_label.grid(row=0, column=0, sticky="w")
        except FileNotFoundError:
            print("Warning: 'image/logo.png' not found.")
            self.logo_label = ctk.CTkLabel(header_container, text="🌿", font=ctk.CTkFont(size=40))
            self.logo_label.grid(row=0, column=0, sticky="w")

        try:
            title_path = os.path.join("image", "title.png")
            title_img = Image.open(title_path)
            title_ctk = ctk.CTkImage(light_image=title_img, size=(300, 80))
            self.title_label = ctk.CTkLabel(header_container, image=title_ctk, text="")
            self.title_label.grid(row=0, column=1, padx=10, sticky="ew")
        except FileNotFoundError:
            print("Warning: 'image/title.png' not found.")
            self.title_label = ctk.CTkLabel(header_container, text="Smart Vending Machine", font=ctk.CTkFont(size=24, weight="bold"))
            self.title_label.grid(row=0, column=1, padx=10, sticky="ew")

        self.camera_label = ctk.CTkLabel(self.left_frame, text="Đang khởi tạo camera...", font=ctk.CTkFont(size=20), fg_color=WHITE, corner_radius=BORDER_RADIUS)
        self.camera_label.grid(row=1, column=0, sticky="nsew")

        confirm_button = ctk.CTkButton(
            self.left_frame, text="Xác nhận số lượng", font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#F9A825", hover_color="#E89B21", text_color="white", height=50,
            corner_radius=BORDER_RADIUS, command=self.confirm_and_update_stats
        )
        confirm_button.grid(row=2, column=0, padx=50, pady=(15, 0), sticky="ew")

    def setup_right_frame(self):
        """Thiết lập các widget cho khung bên phải."""
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)
        
        dashboard_label = ctk.CTkLabel(self.right_frame, text="Dashboard", font=ctk.CTkFont(size=32, weight="bold"), text_color=DARK_GREEN, anchor="w")
        dashboard_label.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        main_card = ctk.CTkFrame(self.right_frame, fg_color=WHITE, corner_radius=BORDER_RADIUS)
        main_card.grid(row=1, column=0, sticky="nsew")
        main_card.grid_columnconfigure(0, weight=1)
        main_card.grid_rowconfigure(2, weight=1)

        stats_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        stats_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        stats_frame.grid_columnconfigure((0, 1), weight=1)

        self.bottles_and_cans_value_label = self.create_stat_box(stats_frame, 0, "Số chai/lon", f"{self.bottles_counted} , {self.cans_counted}", "Nhựa & Lon")
        self.points_value_label = self.create_stat_box(stats_frame, 1, "Tổng điểm", str(self.total_points), "Tích lũy")
        
        rewards_label = ctk.CTkLabel(main_card, text="Phần thưởng có sẵn", font=ctk.CTkFont(size=20, weight="bold"), text_color=DARK_GREEN, anchor="w")
        rewards_label.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="ew")

        rewards_grid = ctk.CTkScrollableFrame(main_card, fg_color="transparent")
        rewards_grid.grid(row=2, column=0, sticky="nsew", padx=10, pady=0)
        rewards_grid.grid_columnconfigure((0, 1, 2), weight=1)

        reward_items = [("🥤", "30 Điểm"), ("🍿", "75 Điểm"), ("🎶", "10 Điểm"), ("🧃", "40 Điểm"), ("🥫", "20 Điểm"), ("🍾", "15 Điểm")]
        for i, item in enumerate(reward_items):
            self.create_reward_card(rewards_grid, i // 3, i % 3, item[0], item[1])
        
        reset_button = ctk.CTkButton(
            self.right_frame, text="Đặt lại số liệu", font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#EF5350", hover_color="#E57373", corner_radius=BORDER_RADIUS, command=self.prompt_reset_stats
        )
        reset_button.grid(row=2, column=0, pady=(15, 0), sticky="e")

    def create_stat_box(self, parent, col, title, value, subtitle):
        stat_box = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=BORDER_RADIUS, border_width=2, border_color=SECONDARY_GREEN)
        stat_box.grid(row=0, column=col, sticky="nsew", padx=10, pady=10)
        stat_box.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(stat_box, text=title, font=ctk.CTkFont(size=14), text_color=DARK_GREEN, anchor="w")
        title_label.pack(fill="x", padx=15, pady=(10,0))
        
        value_label = ctk.CTkLabel(stat_box, text=value, font=ctk.CTkFont(size=32, weight="bold"), text_color=PRIMARY_GREEN, anchor="w")
        value_label.pack(fill="x", padx=15)
        
        subtitle_label = ctk.CTkLabel(stat_box, text=subtitle, font=ctk.CTkFont(size=12), text_color=PRIMARY_GREEN, anchor="w")
        subtitle_label.pack(fill="x", padx=15, pady=(0,10))
        
        return value_label

    def create_reward_card(self, parent, row, col, image_text, points_text):
        """Tạo một thẻ phần thưởng. Chỉ sử dụng .grid() để sắp xếp."""
        try: points_needed = int(re.search(r'\d+', points_text).group())
        except (AttributeError, ValueError): points_needed = 0
        
        card = ctk.CTkButton(
            parent, text="", fg_color=WHITE, border_color=SECONDARY_GREEN, border_width=2,
            hover_color=SECONDARY_GREEN, corner_radius=BORDER_RADIUS, cursor="hand2",
            command=lambda p=points_needed: self.prompt_redeem_reward(p)
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # --- SỬA LỖI: Chỉ sử dụng .grid() để sắp xếp các widget bên trong ---
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=image_text, font=ctk.CTkFont(size=50)).grid(row=0, column=0, pady=(10,0))
        ctk.CTkLabel(card, text=points_text, font=ctk.CTkFont(size=14, weight="bold"), text_color=DARK_GREEN).grid(row=1, column=0, pady=(0,10))

    def confirm_and_update_stats(self):
        newly_detected = self.current_yolo_total - self.last_confirmed_count
        if newly_detected > 0:
            print(f"Xác nhận {newly_detected} vật phẩm mới.")
            self.bottles_counted += newly_detected
            self.total_points += newly_detected * 5
            self.last_confirmed_count = self.current_yolo_total
            self.update_dashboard_display()
        else:
            CustomDialog(self, title="Thông báo", message="Không có vật phẩm mới nào được phát hiện.")

    def update_dashboard_display(self):
        self.bottles_and_cans_value_label.configure(text=f"{self.bottles_counted} , {self.cans_counted}")
        self.points_value_label.configure(text=str(self.total_points))

    def update_camera_feed(self):
        try:
            frame, yolo_total_count = self.yolo_queue.get_nowait()
            self.current_yolo_total = yolo_total_count
            cv2.putText(frame, f'Tong so luong: {yolo_total_count}', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            ctk_image = ctk.CTkImage(light_image=pil_image, size=(640, 480))
            self.camera_label.configure(image=ctk_image, text="")
        except queue.Empty:
            pass
        finally:
            self.after(20, self.update_camera_feed)

    def on_closing(self):
        print("Đang đóng ứng dụng...")
        self.yolo_thread.stop()
        self.yolo_thread.join(timeout=1.0)
        print("Luồng xử lý đã dừng. Đóng cửa sổ.")
        self.destroy()

    def prompt_reset_stats(self):
        CustomDialog(self, title="Xác nhận", message="Bạn có chắc chắn muốn đặt lại toàn bộ số liệu không?", is_confirm=True, command=self.reset_stats)

    def reset_stats(self):
        print("Resetting statistics...")
        self.bottles_counted, self.cans_counted, self.total_points = 0, 0, 0
        self.last_confirmed_count = self.current_yolo_total
        self.update_dashboard_display()

    def prompt_redeem_reward(self, points_needed):
        if self.total_points < points_needed:
            CustomDialog(self, title="Lỗi", message="Bạn không đủ điểm để đổi vật phẩm này!")
        else:
            CustomDialog(self, title="Xác nhận đổi quà", message=f"Bạn có chắc muốn dùng {points_needed} điểm để đổi vật phẩm này?", is_confirm=True, command=lambda: self.redeem_reward(points_needed))

    def redeem_reward(self, points_to_deduct):
        self.total_points -= points_to_deduct
        self.update_dashboard_display()
        print(f"Đã đổi vật phẩm! Trừ {points_to_deduct} điểm. Điểm còn lại: {self.total_points}")

if __name__ == "__main__":
    app = RecyclingApp()
    app.mainloop()
