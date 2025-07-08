import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import random
import re

class CustomDialog(ctk.CTkToplevel):
    """
    A custom dialog window that can be used for confirmation or information.
    """
    def __init__(self, master, title, message, is_confirm=False, command=None):
        super().__init__(master)

        self.title(title)
        # Center the dialog on the parent window
        master_x = master.winfo_x()
        master_y = master.winfo_y()
        master_width = master.winfo_width()
        master_height = master.winfo_height()
        dialog_width = 400
        dialog_height = 150
        x = master_x + (master_width - dialog_width) // 2
        y = master_y + (master_height - dialog_height) // 2
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        self.transient(master)  # Keep on top of the main window
        self.grab_set()         # Make the dialog modal

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)

        label = ctk.CTkLabel(main_frame, text=message, font=ctk.CTkFont(size=14), wraplength=360)
        label.grid(row=0, column=0, columnspan=2, sticky="nsew")

        if is_confirm:
            confirm_button = ctk.CTkButton(main_frame, text="Xác nhận", command=lambda: self._confirm(command), fg_color="#F9A825", hover_color="#E89B21")
            confirm_button.grid(row=1, column=0, padx=(0, 5), pady=10, sticky="e")
            cancel_button = ctk.CTkButton(main_frame, text="Hủy", command=self.destroy, fg_color="gray50", hover_color="gray40")
            cancel_button.grid(row=1, column=1, padx=(5, 0), pady=10, sticky="w")
        else:  # Info dialog
            ok_button = ctk.CTkButton(main_frame, text="OK", command=self.destroy, width=100)
            ok_button.grid(row=1, column=0, columnspan=2, pady=10)

    def _confirm(self, command):
        if command:
            command()
        self.destroy()


class RecyclingApp(ctk.CTk):
    """
    A UI application for a recycling rewards system, featuring a camera feed
    and a confirmation button to update the dashboard.
    """
    def __init__(self):
        super().__init__()

        # --- Basic Window Configuration ---
        self.title("Recycling Dashboard with Camera")
        self.geometry("1300x650")
        self._set_appearance_mode("light")

        # --- Data Attributes ---
        self.bottles_counted = 0
        self.cans_counted = 0
        self.total_points = 0

        # --- OpenCV Camera Setup ---
        self.cap = cv2.VideoCapture(0)
        self.camera_width = 640
        self.camera_height = 480

        # --- Main Layout Frames ---
        self.grid_columnconfigure(0, weight=45)
        self.grid_columnconfigure(1, weight=55)
        self.grid_rowconfigure(0, weight=1)

        # --- Left Frame ---
        self.left_frame = ctk.CTkFrame(self, fg_color="#90e0ef", corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.setup_left_frame()

        # --- Right Frame ---
        self.right_frame = ctk.CTkFrame(self, fg_color="#b7e4c7", corner_radius=0)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.setup_right_frame()

        # --- Start the camera update loop ---
        self.update_camera_feed()
        
        # --- Set protocol for closing the window ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_left_frame(self):
        """Configures the widgets within the left-hand side frame."""
        self.left_frame.grid_rowconfigure(0, weight=0)
        self.left_frame.grid_rowconfigure(1, weight=0)
        self.left_frame.grid_rowconfigure(2, weight=0)
        self.left_frame.grid_rowconfigure(3, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        header_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        header_container.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")
        header_container.grid_columnconfigure(1, weight=1)

        try:
            logo_img = Image.open("image/logo.png")
            logo_ctk = ctk.CTkImage(light_image=logo_img, size=(70, 70))
            self.logo_label = ctk.CTkLabel(header_container, image=logo_ctk, text="")
            self.logo_label.grid(row=0, column=0, sticky="w")
        except FileNotFoundError:
            print("Warning: 'image/logo.png' not found.")
            self.logo_label = ctk.CTkLabel(header_container, text="LOGO", width=80, font=ctk.CTkFont(size=20))
            self.logo_label.grid(row=0, column=0, sticky="w")

        self.title_label = ctk.CTkLabel(
            header_container,
            text="Smart Reverse Vending Machine",
            font=ctk.CTkFont(size=35, weight="bold")
        )
        self.title_label.grid(row=0, column=1, padx=80, sticky="w")
        self.animate_title()

        self.camera_label = ctk.CTkLabel(self.left_frame, text="")
        self.camera_label.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        confirm_button = ctk.CTkButton(
            self.left_frame,
            text="Xác nhận số lượng",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#F9A825",
            hover_color="#E89B21",
            text_color="white",
            height=50,
            corner_radius=10,
            command=self.confirm_and_update_stats
        )
        confirm_button.grid(row=2, column=0, padx=120, pady=(5, 20), sticky="ew")

    def animate_title(self, colors=None, idx=0):
        if colors is None:
            colors = ["#6eaa16", "#7cc117", "#5c9410"]
        self.title_label.configure(text_color=colors[idx % len(colors)])
        self.after(500, self.animate_title, colors, idx+1)

    def confirm_and_update_stats(self):
        detected_bottles = random.randint(1, 3)
        detected_cans = random.randint(0, 2)
        print(f"Đã phát hiện {detected_bottles} chai, {detected_cans} lon.")

        self.bottles_counted += detected_bottles
        self.cans_counted += detected_cans
        self.total_points += (detected_bottles + detected_cans) * 5

        self.bottles_and_cans_value_label.configure(text=f"{self.bottles_counted} , {self.cans_counted}")
        self.points_value_label.configure(text=str(self.total_points))

    def update_camera_feed(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            ctk_image = ctk.CTkImage(light_image=pil_image, size=(self.camera_width, self.camera_height))
            
            self.camera_label.configure(image=ctk_image)
            self.camera_label.image = ctk_image

        self.after(15, self.update_camera_feed)

    def on_closing(self):
        print("Releasing camera and closing app...")
        self.cap.release()
        self.destroy()

    def setup_right_frame(self):
        """Configures the widgets within the right-hand side dashboard frame."""
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(3, weight=1)
        self.right_frame.grid_rowconfigure(4, weight=0)
        
        header_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        
        dashboard_label = ctk.CTkLabel(header_frame, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"), text_color="black")
        dashboard_label.grid(row=0, column=0, sticky="w", pady=20)
        
        filter_icon_label = ctk.CTkLabel(header_frame, text="📊", font=ctk.CTkFont(size=24))
        filter_icon_label.grid(row=0, column=1, sticky="e")

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

        rewards_label = ctk.CTkLabel(rewards_header_frame, text="Phần thưởng có sẵn", font=ctk.CTkFont(size=18, weight="bold"), text_color="black")
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
            row = i // 3
            col = i % 3
            self.create_reward_card(rewards_grid, row, col, item[0], item[1], item[2])
        
        # --- Reset Button ---
        reset_button = ctk.CTkButton(
            self.right_frame,
            text="Đặt lại số liệu",
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="gray50",
            hover_color="gray40",
            command=self.prompt_reset_stats # Changed command
        )
        reset_button.grid(row=4, column=0, padx=10, pady=(20, 10), sticky="ew")

    def prompt_reset_stats(self):
        """Shows a confirmation dialog before resetting statistics."""
        message = "Bạn có chắc chắn muốn đặt lại toàn bộ số liệu không?"
        CustomDialog(self, title="Xác nhận", message=message, is_confirm=True, command=self.reset_stats)

    def reset_stats(self):
        """Resets all statistics to zero and updates the dashboard."""
        print("Resetting statistics...")
        self.bottles_counted = 0
        self.cans_counted = 0
        self.total_points = 0

        # Update the dashboard labels
        self.bottles_and_cans_value_label.configure(text=f"{self.bottles_counted} , {self.cans_counted}")
        self.points_value_label.configure(text=str(self.total_points))
    
    def create_stat_box(self, parent, col, title, value, subtitle, icon):
        stat_box = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        stat_box.grid(row=0, column=col, sticky="ew", padx=10)
        
        icon_label = ctk.CTkLabel(stat_box, text=icon, font=ctk.CTkFont(size=30))
        icon_label.grid(row=0, column=0, rowspan=3, padx=15, pady=15)

        title_label = ctk.CTkLabel(stat_box, text=title, font=ctk.CTkFont(size=14), text_color="gray50")
        title_label.grid(row=0, column=1, sticky="sw", pady=(10, 0))

        value_label = ctk.CTkLabel(stat_box, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color="black")
        value_label.grid(row=1, column=1, sticky="w")

        subtitle_label = ctk.CTkLabel(stat_box, text=subtitle, font=ctk.CTkFont(size=12), text_color="gray")
        subtitle_label.grid(row=2, column=1, sticky="nw", pady=(0, 10))

        return value_label

    def create_reward_card(self, parent, row, col, image_text, points_text, size):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, cursor="hand2")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        try:
            points_needed = int(re.search(r'\d+', points_text).group())
        except (AttributeError, ValueError):
            points_needed = 0
        
        card.bind("<Button-1>", lambda event, p=points_needed: self.prompt_redeem_reward(p))

        img_placeholder = ctk.CTkFrame(card, fg_color="#F0F0F0", height=80)
        img_placeholder.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(img_placeholder, text=image_text, font=ctk.CTkFont(size=50)).pack(expand=True)
        
        points_label = ctk.CTkLabel(card, text=points_text, font=ctk.CTkFont(size=14, weight="bold"))
        points_label.pack(padx=10, pady=(0, 5))
        
        if size:
            size_label = ctk.CTkLabel(card, text=size, font=ctk.CTkFont(size=12), text_color="gray")
            size_label.pack(padx=10, pady=(0, 10))
        
        for widget in card.winfo_children():
            widget.bind("<Button-1>", lambda event, p=points_needed: self.prompt_redeem_reward(p))
            for child_widget in widget.winfo_children():
                 child_widget.bind("<Button-1>", lambda event, p=points_needed: self.prompt_redeem_reward(p))

    def prompt_redeem_reward(self, points_needed):
        if self.total_points < points_needed:
            CustomDialog(self, title="Lỗi", message="Bạn không đủ điểm để đổi vật phẩm này!")
        else:
            message = f"Bạn có chắc muốn dùng {points_needed} điểm để đổi vật phẩm này?"
            CustomDialog(self, title="Xác nhận đổi quà", message=message, is_confirm=True, 
                         command=lambda: self.redeem_reward(points_needed))

    def redeem_reward(self, points_to_deduct):
        self.total_points -= points_to_deduct
        self.points_value_label.configure(text=str(self.total_points))
        print(f"Đã đổi vật phẩm! Trừ {points_to_deduct} điểm. Điểm còn lại: {self.total_points}")


if __name__ == "__main__":
    app = RecyclingApp()
    app.mainloop()
