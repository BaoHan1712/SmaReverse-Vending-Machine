import os
import shutil
import random
from collections import defaultdict
import re

def extract_class_name(filename):
    """
    Trích xuất tên class từ tên file
    VD: AluCan1,000.jpg -> AluCan
        Glass1,006.jpg -> Glass  
        HDPEM47.jpg -> HDPE
        mix9.jpg -> mix
        PET1,002.jpg -> PET
    """
    # Loại bỏ extension
    name = os.path.splitext(filename)[0]
    
    # Tìm pattern: chữ cái + số/ký tự đặc biệt
    match = re.match(r'^([A-Za-z]+)', name)
    if match:
        return match.group(1)
    
    return name

def organize_yolo_dataset(raw_data_path, output_path, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
    """
    Tổ chức dataset theo cấu trúc YOLO với train/val/test cân bằng
    """
    
    # Kiểm tra tỷ lệ chia
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 0.001:
        raise ValueError("Tổng tỷ lệ train + val + test phải bằng 1.0")
    
    # Tìm tất cả file ảnh
    image_files = []
    for filename in os.listdir(raw_data_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_files.append(filename)
    
    print(f"Tìm thấy {len(image_files)} ảnh")
    
    # Nhóm theo class
    class_groups = defaultdict(list)
    for img_file in image_files:
        class_name = extract_class_name(img_file)
        
        # Kiểm tra file label tương ứng có tồn tại không
        label_file = os.path.splitext(img_file)[0] + '.txt'
        label_path = os.path.join(raw_data_path, label_file)
        
        if os.path.exists(label_path):
            class_groups[class_name].append(img_file)
        else:
            print(f"Cảnh báo: Không tìm thấy file label cho {img_file}")
    
    # In thống kê
    print("\nThống kê dataset:")
    total_samples = 0
    for class_name, files in class_groups.items():
        print(f"  {class_name}: {len(files)} samples")
        total_samples += len(files)
    print(f"Tổng: {total_samples} samples\n")
    
    # Tạo cấu trúc thư mục YOLO
    splits = ['train', 'val', 'test']
    for split in splits:
        os.makedirs(os.path.join(output_path, split, 'images'), exist_ok=True)
        os.makedirs(os.path.join(output_path, split, 'labels'), exist_ok=True)
    
    # Chia dataset cho mỗi class
    split_stats = {split: defaultdict(int) for split in splits}
    
    for class_name, files in class_groups.items():
        # Shuffle để random
        random.shuffle(files)
        
        n_files = len(files)
        n_train = int(n_files * train_ratio)
        n_val = int(n_files * val_ratio)
        n_test = n_files - n_train - n_val  # Phần còn lại để tránh sai lệch làm tròn
        
        # Chia files
        train_files = files[:n_train]
        val_files = files[n_train:n_train + n_val]
        test_files = files[n_train + n_val:]
        
        print(f"Class {class_name}: Train={len(train_files)}, Val={len(val_files)}, Test={len(test_files)}")
        
        # Copy files vào thư mục tương ứng
        for split, split_files in [('train', train_files), ('val', val_files), ('test', test_files)]:
            for img_file in split_files:
                # Copy ảnh
                src_img = os.path.join(raw_data_path, img_file)
                dst_img = os.path.join(output_path, split, 'images', img_file)
                shutil.copy2(src_img, dst_img)
                
                # Copy label
                label_file = os.path.splitext(img_file)[0] + '.txt'
                src_label = os.path.join(raw_data_path, label_file)
                dst_label = os.path.join(output_path, split, 'labels', label_file)
                
                if os.path.exists(src_label):
                    shutil.copy2(src_label, dst_label)
                
                split_stats[split][class_name] += 1
    
    # In thống kê kết quả
    print("\n" + "="*50)
    print("KẾT QUẢ CHIA DATASET:")
    print("="*50)
    
    for split in splits:
        total_split = sum(split_stats[split].values())
        percentage = (total_split / total_samples) * 100
        print(f"\n{split.upper()} ({total_split} samples - {percentage:.1f}%):")
        
        for class_name, count in split_stats[split].items():
            class_total = len(class_groups[class_name])
            class_percentage = (count / class_total) * 100
            print(f"  {class_name}: {count}/{class_total} ({class_percentage:.1f}%)")
    
    # Tạo file data.yaml cho YOLO
    create_data_yaml(output_path, class_groups.keys())
    
    print(f"\nHoàn thành! Dataset đã được tổ chức tại: {output_path}")
    print("Cấu trúc thư mục:")
    print("dataset/")
    print("├── train/")
    print("│   ├── images/")
    print("│   └── labels/")
    print("├── val/")
    print("│   ├── images/")
    print("│   └── labels/")
    print("├── test/")
    print("│   ├── images/")
    print("│   └── labels/")
    print("└── data.yaml")

def create_data_yaml(output_path, class_names):
    """
    Tạo file data.yaml cho YOLO training
    """
    class_list = sorted(list(class_names))
    
    yaml_content = f"""# YOLO Dataset Configuration
# Dataset path (relative to this file)
path: .
train: train/images
val: val/images
test: test/images

# Classes
nc: {len(class_list)}  # number of classes
names: {class_list}  # class names

# Class mapping:
"""
    
    for i, class_name in enumerate(class_list):
        yaml_content += f"# {i}: {class_name}\n"
    
    yaml_path = os.path.join(output_path, 'data.yaml')
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    print(f"Đã tạo file cấu hình: {yaml_path}")

def main():
    # Đường dẫn
    raw_data_path = "raw_data"
    output_path = "dataset"
    
    # Kiểm tra thư mục raw_data
    if not os.path.exists(raw_data_path):
        print(f"Lỗi: Không tìm thấy thư mục {raw_data_path}")
        return
    
    # Tạo thư mục output nếu chưa có
    if os.path.exists(output_path):
        response = input(f"Thư mục {output_path} đã tồn tại. Bạn có muốn xóa và tạo lại? (y/n): ")
        if response.lower() == 'y':
            shutil.rmtree(output_path)
        else:
            print("Hủy bỏ thao tác.")
            return
    
    # Set random seed để có thể tái tạo kết quả
    random.seed(42)
    
    print("Bắt đầu chia dataset...")
    print("Tỷ lệ chia: Train=70%, Val=20%, Test=10%")
    print("-" * 50)
    
    try:
        organize_yolo_dataset(raw_data_path, output_path)
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    main()
