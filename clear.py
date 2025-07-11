import os
import sys
import argparse
from PIL import Image
import imagehash
import networkx as nx
from tqdm import tqdm

def find_and_delete_clusters(directory, threshold=10, hash_size=8, dry_run=True, keep_highest_res=True):
    """
    Sử dụng thuật toán phân cụm đồ thị để tìm và xóa các nhóm ảnh tương đồng.
    
    :param directory: Đường dẫn tới thư mục chứa ảnh.
    :param threshold: Ngưỡng khoảng cách hash để nối 2 ảnh vào cùng một cụm.
    :param hash_size: Kích thước của hash.
    :param dry_run: Nếu True, chỉ hiển thị kết quả mà không xóa.
    :param keep_highest_res: Nếu True, giữ lại ảnh có độ phân giải cao nhất trong mỗi cụm.
    """
    
    # 1. Tính hash và thu thập thông tin ảnh
    print("Bước 1: Đang tính hash và thu thập thông tin ảnh...")
    image_data = {} # {filepath: {'hash': hash, 'size': int}}
    
    all_files = []
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                all_files.append(os.path.join(dirpath, filename))

    for filepath in tqdm(sorted(all_files), desc="Tính toán Hash"):
        try:
            with Image.open(filepath) as img:
                h = imagehash.phash(img, hash_size=hash_size)
                size = img.size[0] * img.size[1]
                image_data[filepath] = {'hash': h, 'size': size}
        except Exception as e:
            print(f"\nCảnh báo: Bỏ qua file '{filepath}' do lỗi: {e}")

    if not image_data:
        print("Không tìm thấy ảnh nào để xử lý.")
        return

    filepaths = list(image_data.keys())
    print(f"Hoàn thành. Đã xử lý {len(filepaths)} ảnh.")

    # 2. Xây dựng đồ thị
    print(f"\nBước 2: Xây dựng đồ thị kết nối các ảnh tương đồng (ngưỡng={threshold})...")
    G = nx.Graph()
    G.add_nodes_from(filepaths) # Mỗi ảnh là 1 node

    # Thêm cạnh giữa các node tương đồng
    for i in tqdm(range(len(filepaths)), desc="So sánh và xây dựng đồ thị"):
        for j in range(i + 1, len(filepaths)):
            file1 = filepaths[i]
            file2 = filepaths[j]
            
            distance = image_data[file1]['hash'] - image_data[file2]['hash']
            if distance <= threshold:
                G.add_edge(file1, file2, weight=distance)

    # 3. Tìm các thành phần liên thông (các cụm)
    print("\nBước 3: Tìm các cụm ảnh từ đồ thị...")
    clusters = list(nx.connected_components(G))
    
    # Lọc ra các cụm có nhiều hơn 1 ảnh (cụm có ảnh trùng lặp)
    duplicate_clusters = [c for c in clusters if len(c) > 1]
    
    if not duplicate_clusters:
        print("Không tìm thấy cụm ảnh nào trùng lặp.")
        return

    # 4. Xác định các file cần xóa
    print(f"Tìm thấy {len(duplicate_clusters)} cụm ảnh có chứa bản sao.")
    files_to_delete = set()
    
    for i, cluster in enumerate(duplicate_clusters):
        cluster_list = list(cluster)
        
        # Chọn ảnh để giữ lại
        if keep_highest_res:
            # Sắp xếp theo kích thước ảnh giảm dần, rồi đến tên file
            cluster_list.sort(key=lambda x: (image_data[x]['size'], x), reverse=True)
        
        file_to_keep = cluster_list[0]
        files_to_delete.update(cluster_list[1:])
        
        if dry_run:
            print(f"\n--- Cụm {i+1} ({len(cluster_list)} ảnh) ---")
            print(f"  [GIỮ LẠI]: {os.path.basename(file_to_keep)} (Size: {image_data[file_to_keep]['size']})")
            for f in cluster_list[1:]:
                print(f"  [ĐỀ NGHỊ XÓA]: {os.path.basename(f)} (Size: {image_data[f]['size']})")

    # 5. Thực hiện xóa
    print("\n----------------------------------------------------")
    if not files_to_delete:
        print("Không tìm thấy file nào cần xóa sau khi xử lý các cụm.")
        return

    print(f"Tổng cộng có {len(files_to_delete)} file được đề nghị xóa.")
    
    if dry_run:
        print("Chế độ DRY RUN đang bật. Sẽ không có file nào bị xóa.")
    else:
        print("Các file sau đây sẽ bị XÓA VĨNH VIỄN:")
        for f in sorted(list(files_to_delete)):
            print(f" - {f}")
            
        confirm = input("\nBạn có chắc chắn muốn xóa các file này không? (yes/no): ")
        if confirm.lower() == 'yes':
            deleted_count = 0
            for filepath in files_to_delete:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e:
                    print(f"Lỗi khi xóa file '{filepath}': {e}")
            print(f"\nĐã xóa thành công {deleted_count}/{len(files_to_delete)} file.")
        else:
            print("\nHủy bỏ thao tác. Không có file nào bị xóa.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tìm và xóa các nhóm ảnh tương đồng bằng thuật toán phân cụm.")
    parser.add_argument("directory", type=str, help="Đường dẫn đến thư mục 'train/images'.")
    parser.add_argument("--threshold", type=int, default=10, help="Ngưỡng khoảng cách hash để coi là cùng cụm (khuyến nghị: 8-12). Mặc định: 10.")
    parser.add_argument("--hash-size", type=int, default=8, help="Kích thước hash (mặc định 8).")
    parser.add_argument("--execute", action="store_true", help="Thực sự xóa file thay vì chỉ liệt kê (dry run).")
    
    args = parser.parse_args()

    is_dry_run = not args.execute
    find_and_delete_clusters(args.directory, threshold=args.threshold, hash_size=args.hash_size, dry_run=is_dry_run)