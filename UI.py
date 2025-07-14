from get_library import *
from backend_count import *


# Màu sắc và bo góc chủ đạo
PRIMARY_GREEN = "#388e3c"      # Xanh lá cây non
SECONDARY_GREEN = "#b7e4c7"    # Xanh lá nhạt
YELLOW = "#f9f871"             # Vàng nhạt
WHITE = "#f6fff8"              # Trắng xanh nhẹ
DARK_GREEN = "#388e3c"         # Xanh lá đậm
BORDER_RADIUS = 16              # Bo góc lớn hơn

class CustomDialog(ctk.CTkToplevel):
    """
    Một cửa sổ hộp thoại tuỳ chỉnh dùng để xác nhận hoặc hiển thị thông tin.
    """
    def __init__(self, master, title, message, is_confirm=False, command=None):
        # Hàm khởi tạo hộp thoại tuỳ chỉnh với tiêu đề, nội dung và tuỳ chọn xác nhận
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
        self.configure(bg=SECONDARY_GREEN)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        main_frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=BORDER_RADIUS)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)
        label = ctk.CTkLabel(main_frame, text=message, font=ctk.CTkFont(size=15), wraplength=360, text_color=DARK_GREEN)
        label.grid(row=0, column=0, columnspan=2, sticky="nsew")
        if is_confirm:
            confirm_button = ctk.CTkButton(main_frame, text="Xác nhận", command=lambda: self._confirm(command), fg_color=PRIMARY_GREEN, hover_color=DARK_GREEN, corner_radius=BORDER_RADIUS)
            confirm_button.grid(row=1, column=0, padx=(0, 5), pady=(10,5), sticky="e")
            cancel_button = ctk.CTkButton(main_frame, text="Hủy", command=self.destroy, fg_color=YELLOW, hover_color="#e6e600", text_color="black", corner_radius=BORDER_RADIUS)
            cancel_button.grid(row=1, column=1, padx=(5, 0), pady=10, sticky="w")
        else:
            ok_button = ctk.CTkButton(main_frame, text="OK", command=self.destroy, width=100, fg_color=PRIMARY_GREEN, hover_color=DARK_GREEN, corner_radius=BORDER_RADIUS)
            ok_button.grid(row=1, column=0, columnspan=2, pady=10)

    def _confirm(self, command):
        # Hàm xử lý khi nhấn nút xác nhận, thực thi lệnh truyền vào rồi đóng hộp thoại
        if command:
            command()
        self.destroy()

class RecyclingApp(ctk.CTk):
    """
    Ứng dụng giao diện chính cho hệ thống tái chế.
    """
    def __init__(self):
        # Hàm khởi tạo giao diện chính, thiết lập các thành phần và khởi động luồng xử lý YOLO
        super().__init__()
        self.title("Vì môi trường xanh sạch đẹp - Ươm mầm cây xanh non")
        self.geometry("1350x660")
        self._set_appearance_mode("light")
        self.configure(bg=SECONDARY_GREEN)

        # --- Data Attributes ---
        self.bottles_counted, self.cans_counted, self.total_points = 0, 0, 0
        self.current_yolo_bottle_count, self.current_yolo_can_count = 0, 0
        self.last_confirmed_bottle_count, self.last_confirmed_can_count = 0, 0

        # --- Threading and Queue Setup ---
        self.yolo_queue = queue.Queue(maxsize=2)
        # Change to 0 for webcam, or keep the path for a video file
        video_source = 1
        self.yolo_thread = YOLOProcessor(
            video_path=video_source,
            model_path=r"model/best.pt",
            output_queue=self.yolo_queue
        )
        self.yolo_thread.start()

        self.grid_columnconfigure(0, weight=45)
        self.grid_columnconfigure(1, weight=55)
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self, fg_color=SECONDARY_GREEN, corner_radius=BORDER_RADIUS)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.setup_left_frame()

        self.right_frame = ctk.CTkFrame(self, fg_color=SECONDARY_GREEN, corner_radius=BORDER_RADIUS)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.setup_right_frame()

        self.update_camera_feed()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_left_frame(self):
        """
        Thiết lập các widget cho khung bên trái (hiển thị camera, logo, nút xác nhận).
        """
        self.left_frame.grid_rowconfigure(0, weight=0)
        self.left_frame.grid_rowconfigure(1, weight=0)
        self.left_frame.grid_rowconfigure(2, weight=0)
        self.left_frame.grid_rowconfigure(3, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        header_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        header_container.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")
        header_container.grid_columnconfigure(1, weight=1)

        try:
            logo_img = Image.open(r"image/logo.png")
            logo_ctk = ctk.CTkImage(light_image=logo_img, size=(70, 70))
            self.logo_label = ctk.CTkLabel(header_container, image=logo_ctk, text="")
            self.logo_label.grid(row=0, column=0, sticky="w")
        except FileNotFoundError:
            print("Warning: 'image/logo.png' not found.")
            self.logo_label = ctk.CTkLabel(header_container, text="LOGO", width=80, font=ctk.CTkFont(size=20))
            self.logo_label.grid(row=0, column=0, sticky="w")

        title_img = Image.open(r"image\title.png")
        title_ctk = ctk.CTkImage(light_image=title_img, size=(300, 80))
        self.title_label = ctk.CTkLabel(header_container, image=title_ctk, text="")
        self.title_label.grid(row=0, column=1, padx=1 ,sticky="ew")
        # self.animate_title()

        self.camera_label = ctk.CTkLabel(self.left_frame, text="Đang khởi tạo camera...", font=ctk.CTkFont(size=20))
        self.camera_label.grid(row=1, column=0, padx=20, pady=5, sticky="ew") 

        confirm_button = ctk.CTkButton(
            self.left_frame, text="Xác nhận số lượng", font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#F9A825", hover_color="#E89B21", text_color="white", height=50,
            corner_radius=10, command=self.confirm_and_update_stats
        )
        confirm_button.grid(row=2, column=0, padx=120, pady=(5, 20), sticky="ew")

    def animate_title(self, colors=None, idx=0):
        """
        Hiệu ứng đổi màu tiêu đề liên tục.
        """
        if colors is None: colors = ["#6eaa16", "#7cc117", "#5c9410"]
        self.title_label.configure(text_color=colors[idx % len(colors)])
        self.after(500, self.animate_title, colors, idx+1)

    def confirm_and_update_stats(self):
        newly_detected_bottles = self.current_yolo_bottle_count - self.last_confirmed_bottle_count
        newly_detected_cans = self.current_yolo_can_count - self.last_confirmed_can_count

        if newly_detected_bottles > 0 or newly_detected_cans > 0:
            print(f"Xác nhận {newly_detected_bottles} chai và {newly_detected_cans} lon mới.")
            self.bottles_counted += newly_detected_bottles
            self.cans_counted += newly_detected_cans
            self.total_points += (newly_detected_bottles + newly_detected_cans) * 5
            
            self.last_confirmed_bottle_count = self.current_yolo_bottle_count
            self.last_confirmed_can_count = self.current_yolo_can_count
            
            self.update_dashboard_display()
        else:
            CustomDialog(self, title="Thông báo", message="Không có vật phẩm mới nào được phát hiện.")

    def update_camera_feed(self):
        """
        Lấy frame mới nhất từ queue và hiển thị lên giao diện.
        """
        try:
            frame, bottle_count, can_count = self.yolo_queue.get_nowait()
            self.current_yolo_bottle_count = bottle_count
            self.current_yolo_can_count = can_count

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            ctk_image = ctk.CTkImage(light_image=pil_image, size=(640, 480))
            self.camera_label.configure(image=ctk_image, text="")
            self.camera_label.image = ctk_image
        except queue.Empty:
            pass # No new frame available yet
        finally:
            self.after(20, self.update_camera_feed)

    def on_closing(self):
        """
        Đóng ứng dụng một cách an toàn, dừng luồng YOLO trước khi thoát.
        """
        print("Đang đóng ứng dụng...")
        self.yolo_thread.stop()
        self.yolo_thread.join(timeout=1.0) # Wait for the thread to finish
        print("Luồng xử lý đã dừng. Đóng cửa sổ.")
        self.destroy()

    def setup_right_frame(self):
        """
        Thiết lập các widget cho khung bên phải (dashboard, thống kê, phần thưởng, nút reset).
        """
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(3, weight=1)
        self.right_frame.grid_rowconfigure(4, weight=0)
        
        header_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        dashboard_label = ctk.CTkLabel(header_frame, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"), text_color=DARK_GREEN)
        dashboard_label.grid(row=0, column=0, sticky="w", pady=20)

        # --- NÚT EXPORT MỚI ---
        try:

            export_icon_path = Image.open(r"image\export.png")
            export_icon = ctk.CTkImage(light_image=export_icon_path, size=(80, 45))
            export_button = ctk.CTkButton(
                header_frame, image=export_icon, text="", width=20,
                fg_color="transparent", hover_color=SECONDARY_GREEN,
                command=self.prompt_export
            )
        except FileNotFoundError:
            print("Warning: 'image/export_icon.png' not found. Using text button.")
            export_button = ctk.CTkButton(
                header_frame, text="Xuất Phiếu", font=ctk.CTkFont(weight="bold"),
                fg_color="transparent", border_color=PRIMARY_GREEN, text_color=PRIMARY_GREEN,
                border_width=2, hover_color=SECONDARY_GREEN, command=self.prompt_export
            )
        export_button.grid(row=0, column=1, sticky="e")
        
        stats_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="ew", pady=10)
        stats_frame.grid_columnconfigure((0, 1), weight=1)
        self.bottles_and_cans_value_label = self.create_stat_box(
            stats_frame, 0, "Số chai/lon", f"{self.bottles_counted} , {self.cans_counted}", "Nhựa & Lon", ""
        )
        self.points_value_label = self.create_stat_box(stats_frame, 1, "Tổng điểm", str(self.total_points), "Tích lũy", "")
        rewards_header_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        rewards_header_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(20, 10))
        rewards_header_frame.grid_columnconfigure(0, weight=1)
        rewards_label = ctk.CTkLabel(rewards_header_frame, text="Phần thưởng có sẵn", font=ctk.CTkFont(size=18, weight="bold"), text_color=DARK_GREEN)
        rewards_label.grid(row=0, column=0, sticky="w")
        rewards_grid = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        rewards_grid.grid(row=3, column=0, sticky="nsew")
        rewards_grid.grid_columnconfigure((0, 1, 2), weight=1)
        reward_items = [
            ("🥤", "30 Điểm", ""), ("🍿", "75 Điểm", ""),
            ("🎶", "10 Điểm", ""), ("🧃", "40 Điểm", ""),
            ("🥫", "20 Điểm", ""), ("🍾", "15 Điểm", "")
        ]
        for i, item in enumerate(reward_items):
            row, col = i // 3, i % 3
            self.create_reward_card(rewards_grid, row, col, item[0], item[1], item[2])
        
        reset_button = ctk.CTkButton(
            self.right_frame, text="Đặt lại số liệu", font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#F9A825", hover_color="#E89B21", text_color="white", corner_radius=10, command=self.prompt_reset_stats
        )
        reset_button.grid(row=4, column=0, padx=10, pady=(20, 10), sticky="ew")

    def prompt_export(self):
        """Mở hộp thoại để người dùng nhập tên và xuất phiếu."""
        dialog = ctk.CTkInputDialog(
            text="Vui lòng nhập họ và tên để xuất phiếu:",
            title="Xuất Phiếu Tích Điểm"
        )
        user_name = dialog.get_input()

        if user_name:
            print(f"Đã xuất phiếu thành công cho: {user_name}")
            # Hiển thị thông báo thành công
            success_message = (f"Đã xuất phiếu thành công cho {user_name}")
            CustomDialog(self, title="Thành công", message=success_message)
        else:
            print("Hủy xuất phiếu.")

    def prompt_reset_stats(self):
        """
        Hiển thị hộp thoại xác nhận trước khi đặt lại số liệu thống kê.
        """
        message = "Bạn có chắc chắn muốn đặt lại toàn bộ số liệu không?"
        CustomDialog(self, title="Xác nhận", message=message, is_confirm=True, command=self.reset_stats)

    def reset_stats(self):
        """Đặt lại toàn bộ số liệu thống kê về 0."""
        print("Resetting statistics...")
        self.bottles_counted, self.cans_counted, self.total_points = 0, 0, 0
        self.last_confirmed_bottle_count = self.current_yolo_bottle_count
        self.last_confirmed_can_count = self.current_yolo_can_count
        self.update_dashboard_display()
    
    def create_stat_box(self, parent, col, title, value, subtitle, icon):
        """
        Tạo một ô thống kê nhỏ hiển thị số liệu (số chai/lon, tổng điểm).
        """
        stat_box = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=BORDER_RADIUS, border_width=2, border_color="#388e3c")
        stat_box.grid(row=0, column=col, sticky="ew", padx=10)
        icon_label = ctk.CTkLabel(stat_box, text=icon, font=ctk.CTkFont(size=30))
        icon_label.grid(row=0, column=0, rowspan=3, padx=(10, 0), pady=10, sticky="nsw")
        title_label = ctk.CTkLabel(stat_box, text=title, font=ctk.CTkFont(size=14), text_color=DARK_GREEN)
        title_label.grid(row=0, column=1, sticky="sw", pady=(10, 0))
        value_label = ctk.CTkLabel(stat_box, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=PRIMARY_GREEN)
        value_label.grid(row=1, column=1, sticky="w")
        subtitle_label = ctk.CTkLabel(stat_box, text=subtitle, font=ctk.CTkFont(size=12), text_color=PRIMARY_GREEN)
        subtitle_label.grid(row=2, column=1, sticky="nw", pady=(0, 10))
        return value_label

    def create_reward_card(self, parent, row, col, image_text, points_text, size):
        """
        Tạo một thẻ phần thưởng, cho phép người dùng nhấn để đổi quà nếu đủ điểm.
        """
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, cursor="hand2")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        try:
            points_needed = int(re.search(r'\d+', points_text).group())
        except (AttributeError, ValueError):
            points_needed = 0
        card.bind("<Button-1>", lambda event, p=points_needed: self.prompt_redeem_reward(p))
        img_placeholder = ctk.CTkFrame(card, fg_color=SECONDARY_GREEN, height=80, corner_radius=BORDER_RADIUS)
        img_placeholder.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(img_placeholder, text=image_text, font=ctk.CTkFont(size=50)).pack(expand=True)
        points_label = ctk.CTkLabel(card, text=points_text, font=ctk.CTkFont(size=14, weight="bold"), text_color=DARK_GREEN)
        points_label.pack(padx=10, pady=(0, 5))
        if size:
            size_label = ctk.CTkLabel(card, text=size, font=ctk.CTkFont(size=12), text_color=PRIMARY_GREEN)
            size_label.pack(padx=10, pady=(0, 10))
        for widget in card.winfo_children():
            widget.bind("<Button-1>", lambda event, p=points_needed: self.prompt_redeem_reward(p))
            for child_widget in widget.winfo_children():
                 child_widget.bind("<Button-1>", lambda event, p=points_needed: self.prompt_redeem_reward(p))

    def prompt_redeem_reward(self, points_needed):
        """
        Hiển thị hộp thoại xác nhận khi người dùng muốn đổi phần thưởng.
        """
        if self.total_points < points_needed:
            CustomDialog(self, title="Lỗi", message="Bạn không đủ điểm để đổi vật phẩm này!")
        else:
            message = f"Bạn có chắc muốn dùng {points_needed} điểm để đổi vật phẩm này?"
            CustomDialog(self, title="Xác nhận đổi quà", message=message, is_confirm=True, 
                         command=lambda: self.redeem_reward(points_needed))

    def redeem_reward(self, points_to_deduct):
        """
        Trừ điểm khi người dùng đổi phần thưởng và cập nhật lại số điểm.
        """
        self.total_points -= points_to_deduct
        self.points_value_label.configure(text=str(self.total_points))
        print(f"Đã đổi vật phẩm! Trừ {points_to_deduct} điểm. Điểm còn lại: {self.total_points}")

    def update_dashboard_display(self):
        """
        Cập nhật hiển thị dashboard với số liệu mới nhất.
        """
        self.bottles_and_cans_value_label.configure(text=f"{self.bottles_counted} , {self.cans_counted}")
        self.points_value_label.configure(text=str(self.total_points))

# Hàm splash 
def create_splash_screen(master):
    """
    Hàm này tạo và hiển thị cửa sổ màn hình chờ với ảnh GIF động.
    """
    splash = ctk.CTkToplevel(master)

    # --- Cấu hình cửa sổ ---
    width, height = 650, 500
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)

    splash.geometry(f'{width}x{height}+{int(x)}+{int(y)}')
    splash.overrideredirect(True)
    splash.configure(fg_color="#F9F9F9")  # Nền sáng

    # --- Load và xử lý GIF ---
    frames = []
    gif_path = r"image\giphy.gif"  

    if os.path.exists(gif_path):
        gif = Image.open(gif_path)
        try:
            while True:
                frame = gif.copy().convert("RGBA").resize((315, 315))
                # Sử dụng CTkImage
                ctk_image = ctk.CTkImage(light_image=frame, dark_image=frame, size=(315, 315))
                frames.append(ctk_image)
                gif.seek(len(frames))
        except EOFError:
            pass
    else:
        print(f"Warning: '{gif_path}' not found. Hiển thị placeholder.")
        frames = None

    # --- Label ảnh ---
    image_label = ctk.CTkLabel(splash, text="")
    image_label.pack(pady=(50, 20))

    # --- Hàm chạy GIF ---
    def animate(frame_index=0):
        if frames:
            frame = frames[frame_index]
            image_label.configure(image=frame)
            next_index = (frame_index + 1) % len(frames)
            splash.after(29, animate, next_index)

    if frames:
        animate()
    else:
        # Nếu không có GIF, hiện placeholder text
        image_label.configure(text="</>", font=ctk.CTkFont(size=100, family="Courier New", weight="bold"), text_color="#00FF7F")

    # --- Dòng chữ đang tải ---
    loading_label = ctk.CTkLabel(
        splash,
        text="Đang khởi tạo...",
        font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
        text_color="#1B5E20"
    )
    loading_label.pack(pady=(10, 5))

    # --- Thanh tiến trình ---
    progress_bar = ctk.CTkProgressBar(
        splash,
        orientation='horizontal',
        mode='determinate',
        progress_color="#4CAF50",
        fg_color="#E8F5E9"
    )
    progress_bar.pack(pady=10, padx=50, fill="x")
    progress_bar.set(0)

    # --- Nhãn hiển thị phần trăm ---
    percentage_label = ctk.CTkLabel(
        splash,
        text="0%",
        font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
        text_color="#388E3C"
    )
    percentage_label.pack()

    # --- Hàm cập nhật tiến trình ---
    def update_progress(value=0):
        if value <= 1.0:
            progress_bar.set(value)
            percentage_label.configure(text=f"{int(value * 100)}%")
            splash.after(28, update_progress, value + 0.01)
        else:
            progress_bar.set(1)
            percentage_label.configure(text="100%")

    update_progress()

    return splash


if __name__ == "__main__":
    app = RecyclingApp()
    app.withdraw()
    splash = create_splash_screen(app)
    def show_main_window():
        splash.destroy()
        app.deiconify()

    app.after(3000, show_main_window)
    app.iconbitmap(r"image\logo.ico") 
    app.mainloop()
