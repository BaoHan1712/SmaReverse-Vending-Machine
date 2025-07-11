import os
import shutil
import argparse

def copy_image_files(source_folder, destination_folder):
    """
    Sao chép tất cả các file ảnh từ thư mục nguồn sang thư mục đích.

    :param source_folder: Đường dẫn đến thư mục chứa ảnh gốc.
    :param destination_folder: Đường dẫn đến thư mục muốn lưu ảnh đã sao chép.
    """
    
    # 1. Kiểm tra xem thư mục nguồn có tồn tại không
    if not os.path.isdir(source_folder):
        print(f"Lỗi: Thư mục nguồn '{source_folder}' không tồn tại.")
        return

    # 2. Tạo thư mục đích nếu nó chưa tồn tại
    try:
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
            print(f"Đã tạo thư mục đích: '{destination_folder}'")
    except OSError as e:
        print(f"Lỗi: Không thể tạo thư mục đích '{destination_folder}'. Lý do: {e}")
        return

    # 3. Định nghĩa các đuôi file ảnh hợp lệ
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
    
    copied_count = 0
    skipped_count = 0
    
    print(f"\nBắt đầu sao chép từ '{source_folder}' đến '{destination_folder}'...")

    # 4. Lặp qua tất cả các file trong thư mục nguồn
    for filename in os.listdir(source_folder):
        # Kiểm tra xem file có phải là định dạng ảnh không (không phân biệt chữ hoa/thường)
        if filename.lower().endswith(image_extensions):
            source_path = os.path.join(source_folder, filename)
            destination_path = os.path.join(destination_folder, filename)
            
            try:
                # Thực hiện sao chép file
                shutil.copy2(source_path, destination_path)
                print(f"Đã sao chép: {filename}")
                copied_count += 1
            except Exception as e:
                print(f"Lỗi khi sao chép file '{filename}': {e}")
                skipped_count += 1
        else:
            # Bỏ qua các file không phải ảnh
            skipped_count += 1

    # 5. In ra kết quả tổng kết
    print("\n-------------------------------------------")
    print("Hoàn tất!")
    print(f"Tổng số file đã sao chép: {copied_count}")
    print(f"Tổng số file đã bỏ qua (không phải ảnh): {skipped_count}")
    print(f"Các file ảnh đã được lưu tại: {os.path.abspath(destination_folder)}")
    print("-------------------------------------------")


if __name__ == "__main__":
    # Tạo trình phân tích cú pháp dòng lệnh
    parser = argparse.ArgumentParser(description="Sao chép tất cả các file ảnh từ thư mục này sang thư mục khác.")
    
    # Thêm các đối số bắt buộc
    parser.add_argument("source", type=str, help="Đường dẫn đến thư mục nguồn chứa ảnh.")
    parser.add_argument("destination", type=str, help="Đường dẫn đến thư mục đích để lưu bản sao.")
    
    # Phân tích các đối số
    args = parser.parse_args()
    
    # Gọi hàm chính với các đường dẫn từ dòng lệnh
    copy_image_files(args.source, args.destination)