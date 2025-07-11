# Smart Reverse Vending Machine

## Giới thiệu

**Smart Reverse Vending Machine** là ứng dụng giao diện người dùng (UI) mô phỏng hệ thống máy thu gom chai/lon thông minh, tích điểm đổi quà vì môi trường xanh sạch. Ứng dụng sử dụng Python, thư viện [customtkinter](https://github.com/TomSchimansky/CustomTkinter) để xây dựng giao diện hiện đại, tích hợp camera (OpenCV) để nhận diện vật phẩm, và quản lý điểm thưởng.

## Tính năng

- **Giao diện hiện đại, thân thiện, chủ đề xanh sạch.**
- **Tích hợp camera**: Hiển thị trực tiếp hình ảnh từ webcam.
- **Đếm số chai/lon**: Nhấn nút để xác nhận số lượng, hệ thống tự động cộng dồn.
- **Tích điểm đổi quà**: Mỗi chai/lon được cộng điểm, có thể dùng điểm để đổi các phần thưởng hấp dẫn.
- **Reset số liệu**: Có xác nhận trước khi đặt lại toàn bộ số liệu.
- **Hiệu ứng động cho tiêu đề**: Tiêu đề đổi màu liên tục tạo cảm giác sinh động.
- **Hộp thoại xác nhận, thông báo**: Giao diện xác nhận thân thiện, tiếng Việt.

## Demo giao diện

![Demo giao diện](image/UI.png)

## Yêu cầu hệ thống

- Python >= 3.8, Đang dùng python 3.9
- Thư viện: customtkinter, opencv-python, pillow

## Cài đặt

1. **Clone dự án:**
   ```bash
   git clone <https://github.com/BaoHan1712/SmaReverse-Vending-Machine.git>
   ```

2. **Cài đặt thư viện cần thiết:**
   ```bash
   pip install customtkinter opencv-python pillow
   ```

3. **Thêm ảnh logo (nếu có):**
   - Đặt file logo (ví dụ: `logo.png`) vào thư mục `image/` (nếu chưa có, chương trình sẽ hiển thị chữ LOGO thay thế).

   ![Demo logo](image/logo.png)

   ![Demo giao diện splash](image/giphy.gif)

4. **Chạy ứng dụng:**
   ```bash
   python UI.py
   ```

## Hướng dẫn sử dụng

- **Xác nhận số lượng:** Đặt chai/lon trước camera, nhấn "Xác nhận số lượng" để hệ thống cộng dồn số lượng và điểm.
- **Đổi quà:** Nhấn vào phần thưởng muốn đổi, xác nhận để trừ điểm.
- **Đặt lại số liệu:** Nhấn "Đặt lại số liệu", xác nhận để reset toàn bộ số liệu về 0.
- **Thoát:** Đóng cửa sổ để thoát ứng dụng.

## Cấu trúc file

```
.
├── UI.py           # File code chính giao diện
├── image/
│   └── UI.png        # Ảnh demo giao diện
│   └── logo.png      # (Tùy chọn) Logo mầm non/cây trồng
```

## Đóng góp

Mọi ý kiến đóng góp, báo lỗi hoặc đề xuất tính năng mới đều được hoan nghênh!

---

**Tác giả:**  
- [BaoHan1712] 