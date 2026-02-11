import cv2
import numpy as np
import mahotas
import os
from src.utils.GridMapPPM import GridMapPPM

def load_map_image(map_path):
    grid_map = GridMapPPM()
    grid_map.loadData(map_path)
    image_data = grid_map.mapData
    if isinstance(image_data, np.ndarray):
        if len(image_data.shape) == 3:
            image = cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR)
            if image.dtype != np.uint8:
                image = image.astype(np.uint8)
        else:
            if image_data.dtype != np.uint8:
                image = cv2.normalize(image_data, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            else:
                image = image_data
    else:
        image = cv2.imread(map_path)
    return image

def calculate_zernike_moments(image, radius=64, degree=8):
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    # 二值化
    _, binary = cv2.threshold(gray, 127, 1, cv2.THRESH_BINARY)
    # 计算 Zernike Moments
    zm = mahotas.features.zernike_moments(binary, radius, degree)
    return np.array(zm)

def compare_zernike_moments(zm1, zm2):
    # 使用欧氏距离
    return np.linalg.norm(zm1 - zm2)

def find_similar_images(threshold=0.1):
    data_root = "../../data"
    subdirs = [d for d in os.listdir(data_root) if os.path.isdir(os.path.join(data_root, d))]
    temp_dir = "../../temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    all_zm = {}
    all_images = {}
    for subdir in subdirs:
        subdir_path = os.path.join(data_root, subdir)
        ppm_files = [f for f in os.listdir(subdir_path) if f.endswith(".ppm")]
        for filename in ppm_files:
            filepath = os.path.join(subdir_path, filename)
            try:
                img = load_map_image(filepath)
                zm = calculate_zernike_moments(img)
                all_zm[(subdir, filename)] = zm
                all_images[(subdir, filename)] = img
                print(f"{subdir}/{filename}: {zm}")
            except Exception as e:
                print(f"处理文件 {subdir}/{filename} 时出错: {e}")
    print("\n开始比较不同文件夹下的相似图像:")
    keys = list(all_zm.keys())
    similar_pairs = []
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            subdir1, filename1 = keys[i]
            subdir2, filename2 = keys[j]
            if subdir1 != subdir2:
                zm1 = all_zm[keys[i]]
                zm2 = all_zm[keys[j]]
                distance = compare_zernike_moments(zm1, zm2)
                if distance < threshold:
                    similar_pairs.append({
                        'file1': (subdir1, filename1),
                        'file2': (subdir2, filename2),
                        'zm1': zm1,
                        'zm2': zm2,
                        'distance': distance,
                        'img1': all_images[keys[i]],
                        'img2': all_images[keys[j]]
                    })
    if similar_pairs:
        print(f"\n发现 {len(similar_pairs)} 对相似图像 (阈值: {threshold}):")
        for idx, pair in enumerate(similar_pairs):
            subdir1, filename1 = pair['file1']
            subdir2, filename2 = pair['file2']
            print(f"\n相似图像对:")
            print(f"  文件1: {subdir1}/{filename1}")
            print(f"  文件2: {subdir2}/{filename2}")
            print(f"  距离: {pair['distance']:.6f}")
            print(f"  文件1的 Zernike Moments: {pair['zm1']}")
            print(f"  文件2的 Zernike Moments: {pair['zm2']}")
            generate_comparison_image(pair, idx, temp_dir)
    else:
        print(f"\n没有发现距离小于 {threshold} 的相似图像对")

def generate_comparison_image(pair, index, temp_dir):
    img1 = pair['img1']
    img2 = pair['img2']
    file1_path = f"{pair['file1'][0]}/{pair['file1'][1]}"
    file2_path = f"{pair['file2'][0]}/{pair['file2'][1]}"
    zm1 = pair['zm1']
    zm2 = pair['zm2']
    distance = pair['distance']
    if len(img1.shape) == 2:
        img1 = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)
    if len(img2.shape) == 2:
        img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)
    height = max(img1.shape[0], img2.shape[0])
    width1 = int(img1.shape[1] * (height / img1.shape[0])) if img1.shape[0] > 0 else img1.shape[1]
    width2 = int(img2.shape[1] * (height / img2.shape[0])) if img2.shape[0] > 0 else img2.shape[1]
    img1_resized = cv2.resize(img1, (width1, height))
    img2_resized = cv2.resize(img2, (width2, height))
    combined_img = np.hstack((img1_resized, img2_resized))
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    font_color = (0, 0, 255)
    thickness = 1
    y_offset = height + 30
    cv2.putText(combined_img, f"File 1: {file1_path}", (10, y_offset), font, font_scale, font_color, thickness)
    cv2.putText(combined_img, f"File 2: {file2_path}", (width1 + 10, y_offset), font, font_scale, font_color, thickness)
    y_offset += 30
    zm1_text = f"ZM1: [{', '.join([f'{x:.2f}' for x in zm1])}]"
    zm2_text = f"ZM2: [{', '.join([f'{x:.2f}' for x in zm2])}]"
    cv2.putText(combined_img, zm1_text, (10, y_offset), font, font_scale, font_color, thickness)
    cv2.putText(combined_img, zm2_text, (width1 + 10, y_offset), font, font_scale, font_color, thickness)
    y_offset += 30
    distance_text = f"Distance: {distance:.6f}"
    cv2.putText(combined_img, distance_text, (10, y_offset), font, font_scale, font_color, thickness)
    current_height, current_width = combined_img.shape[:2]
    needed_height = y_offset + 50
    if needed_height > current_height:
        extra_height = needed_height - current_height
        extra_area = np.zeros((extra_height, current_width, 3), dtype=combined_img.dtype)
        combined_img = np.vstack((combined_img, extra_area))
        y_offset = height + 30
        cv2.putText(combined_img, f"File 1: {file1_path}", (10, y_offset), font, font_scale, font_color, thickness)
        cv2.putText(combined_img, f"File 2: {file2_path}", (width1 + 10, y_offset), font, font_scale, font_color, thickness)
        y_offset += 30
        cv2.putText(combined_img, zm1_text, (10, y_offset), font, font_scale, font_color, thickness)
        cv2.putText(combined_img, zm2_text, (width1 + 10, y_offset), font, font_scale, font_color, thickness)
        y_offset += 30
        cv2.putText(combined_img, distance_text, (10, y_offset), font, font_scale, font_color, thickness)
    output_path = os.path.join(temp_dir, f"similar_pair_{index}.jpg")
    cv2.imwrite(output_path, combined_img)
    print(f"  对比图已保存至: {output_path}")

def main():
    print("计算所有 ppm 文件的 Zernike Moments:")
    find_similar_images(threshold=0.5)

if __name__ == "__main__":
    main()