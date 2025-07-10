import cv2

# Khởi tạo danh sách để lưu trữ các điểm được chọn
selected_points = []

def mouse_callback(event, x, y, flags, params):
    """
    Hàm callback xử lý sự kiện click chuột.
    Khi người dùng nhấp chuột trái, tọa độ (x, y) sẽ được lưu lại.
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_points.append([x, y])
        print(f"Đã chọn điểm: ({x}, {y})")

def run_video_selection(video_path):
    """
    Hàm chính để chạy video, cho phép chọn điểm và lưu tọa độ.

    Args:
        video_path (str): Đường dẫn đến tệp video.
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Lỗi: Không thể mở tệp video.")
        return

    cv2.namedWindow("Video")
    cv2.setMouseCallback("Video", mouse_callback)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Video đã kết thúc hoặc có lỗi khi đọc khung hình.")
            break

        # Vẽ các điểm đã chọn lên khung hình
        for point in selected_points:
            cv2.circle(frame, tuple(point), 5, (0, 0, 255), -1)

        cv2.imshow("Video", frame)

        key = cv2.waitKey(1) & 0xFF

        # Nhấn 'c' để in và xóa danh sách điểm
        if key == ord('c'):
            if selected_points:
                print("Tọa độ các điểm đã lưu:", selected_points)
                # Xóa danh sách điểm sau khi lưu để có thể chọn lại
                selected_points.clear() 
            else:
                print("Chưa có điểm nào được chọn.")

        # Nhấn 'q' để thoát
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Thay thế "your_video.mp4" bằng đường dẫn thực tế đến tệp video của bạn
    video_file = "your_video.mp4"
    run_video_selection(video_file)