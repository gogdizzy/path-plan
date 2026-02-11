import cv2
import numpy as np
from src.utils.GridMapPPM import GridMapPPM
import os


def load_map_image(map_path):
    """
    使用 GridMapPPM 加载 ppm 地图文件并转换为 OpenCV 图像格式
    """
    # 使用 GridMapPPM 读取 ppm 文件
    grid_map = GridMapPPM()
    grid_map.loadData(map_path)

    # 获取图像数据并转换为 OpenCV 格式
    image_data = grid_map.mapData

    # 如果返回的是 numpy 数组，确保格式正确
    if isinstance(image_data, np.ndarray):
        if len(image_data.shape) == 3:
            # 如果是彩色图像，转换为 BGR 格式（OpenCV 默认格式）
            image = cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR)
            # 确保数据类型为 uint8
            if image.dtype != np.uint8:
                image = image.astype(np.uint8)
        else:
            # 处理二维数组情况（地图数据通常是灰度图）
            # 确保数据类型为 uint8，这是 OpenCV 所要求的
            if image_data.dtype != np.uint8:
                # 归一化到 0-255 范围并转换为 uint8 类型
                image = cv2.normalize(image_data, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            else:
                image = image_data
    else:
        # 如果需要从文件重新读取
        image = cv2.imread(map_path)

    return image


def calculate_hu_moments(image):
    """
    计算图像的 Hu 不变矩
    """
    # 转换为灰度图像（如果还不是）
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # 计算图像的矩
    moments = cv2.moments(gray)
    
    # 计算 Hu 不变矩
    hu_moments = cv2.HuMoments(moments)
    
    # 对 Hu 不变矩取对数以获得更好的数值稳定性
    # 注意：对于值为0的情况需要特殊处理
    for i in range(0, 7):
        if hu_moments[i] != 0:
            hu_moments[i] = -1 * np.sign(hu_moments[i]) * np.log10(abs(hu_moments[i]))
    
    return hu_moments.flatten()


def compare_hu_moments_with_mirror_handling(hu1, hu2):
    """
    比较两个 Hu 不变矩，考虑镜像符号问题
    """
    # 计算两个图像 Hu 不变矩之间的距离
    # 使用 L2 距离（欧几里得距离），但对第6和第7个值使用绝对值差
    diff = np.abs(hu1 - hu2)
    
    # 对于第6个（索引5）和第7个（索引6）Hu不变矩，使用绝对值差
    # 因为这些值在镜像反射时会改变符号
    diff[5] = np.abs(np.abs(hu1[5]) - np.abs(hu2[5]))
    diff[6] = np.abs(np.abs(hu1[6]) - np.abs(hu2[6]))
    
    # 计算欧几里得距离
    distance = np.linalg.norm(diff)
    
    return distance


def find_similar_images(threshold=0.1):
    """
    遍历 data 目录下的所有文件夹，计算每个 ppm 文件的 Hu 不变矩，
    如果不同文件夹下的两个文件的 Hu 不变矩比较类似，则输出相关信息
    """
    # 获取 data 目录下的所有子目录
    data_root = "../../data"
    subdirs = [d for d in os.listdir(data_root) if os.path.isdir(os.path.join(data_root, d))]
    
    # 创建 temp 文件夹用于存储结果图片
    temp_dir = "../../temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # 存储所有文件的 Hu 不变矩和原始图像
    all_hu_moments = {}
    all_images = {}
    
    # 遍历每个子目录
    for subdir in subdirs:
        subdir_path = os.path.join(data_root, subdir)
        ppm_files = [f for f in os.listdir(subdir_path) if f.endswith(".ppm")]
        
        # 计算每个 ppm 文件的 Hu 不变矩
        for filename in ppm_files:
            filepath = os.path.join(subdir_path, filename)
            try:
                img = load_map_image(filepath)
                hu_moments = calculate_hu_moments(img)
                # 存储文件路径和对应的 Hu 不变矩以及原始图像
                all_hu_moments[(subdir, filename)] = hu_moments
                all_images[(subdir, filename)] = img
                print(f"{subdir}/{filename}: {hu_moments}")
            except Exception as e:
                print(f"处理文件 {subdir}/{filename} 时出错: {e}")
    
    print("\n开始比较不同文件夹下的相似图像:")
    
    # 比较不同文件夹下的文件
    keys = list(all_hu_moments.keys())
    similar_pairs = []
    
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            subdir1, filename1 = keys[i]
            subdir2, filename2 = keys[j]
            
            # 只比较不同文件夹下的文件
            if subdir1 != subdir2:
                hu1 = all_hu_moments[keys[i]]
                hu2 = all_hu_moments[keys[j]]
                
                # 计算相似性距离
                distance = compare_hu_moments_with_mirror_handling(hu1, hu2)
                
                # 如果距离小于阈值，则认为是相似的
                if distance < threshold:
                    similar_pairs.append({
                        'file1': (subdir1, filename1),
                        'file2': (subdir2, filename2),
                        'hu1': hu1,
                        'hu2': hu2,
                        'distance': distance,
                        'img1': all_images[keys[i]],
                        'img2': all_images[keys[j]]
                    })
    
    # 输出相似的文件对并生成对比图
    if similar_pairs:
        print(f"\n发现 {len(similar_pairs)} 对相似图像 (阈值: {threshold}):")
        for idx, pair in enumerate(similar_pairs):
            subdir1, filename1 = pair['file1']
            subdir2, filename2 = pair['file2']
            print(f"\n相似图像对:")
            print(f"  文件1: {subdir1}/{filename1}")
            print(f"  文件2: {subdir2}/{filename2}")
            print(f"  距离: {pair['distance']:.6f}")
            print(f"  文件1的 Hu 不变矩: {pair['hu1']}")
            print(f"  文件2的 Hu 不变矩: {pair['hu2']}")
            
            # 生成对比图
            generate_comparison_image(pair, idx, temp_dir)
    else:
        print(f"\n没有发现距离小于 {threshold} 的相似图像对")


def generate_comparison_image(pair, index, temp_dir):
    """
    生成相似图像对比图
    """
    # 获取图像和信息
    img1 = pair['img1']
    img2 = pair['img2']
    file1_path = f"{pair['file1'][0]}/{pair['file1'][1]}"
    file2_path = f"{pair['file2'][0]}/{pair['file2'][1]}"
    hu1 = pair['hu1']
    hu2 = pair['hu2']
    distance = pair['distance']
    
    # 确保图像是三通道BGR格式
    if len(img1.shape) == 2:
        img1 = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)
    if len(img2.shape) == 2:
        img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)
    
    # 调整图像大小使其高度一致
    height = max(img1.shape[0], img2.shape[0])
    width1 = int(img1.shape[1] * (height / img1.shape[0])) if img1.shape[0] > 0 else img1.shape[1]
    width2 = int(img2.shape[1] * (height / img2.shape[0])) if img2.shape[0] > 0 else img2.shape[1]
    
    img1_resized = cv2.resize(img1, (width1, height))
    img2_resized = cv2.resize(img2, (width2, height))
    
    # 水平拼接图像
    combined_img = np.hstack((img1_resized, img2_resized))
    
    # 添加文本信息
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    font_color = (0, 0, 255)  # 红色
    thickness = 1
    
    # 添加文件名
    y_offset = height + 30
    cv2.putText(combined_img, f"File 1: {file1_path}", (10, y_offset), font, font_scale, font_color, thickness)
    cv2.putText(combined_img, f"File 2: {file2_path}", (width1 + 10, y_offset), font, font_scale, font_color, thickness)
    
    # 添加 Hu 不变矩数值
    y_offset += 30
    hu1_text = f"Hu1: [{', '.join([f'{x:.2f}' for x in hu1])}]"
    hu2_text = f"Hu2: [{', '.join([f'{x:.2f}' for x in hu2])}]"
    cv2.putText(combined_img, hu1_text, (10, y_offset), font, font_scale, font_color, thickness)
    cv2.putText(combined_img, hu2_text, (width1 + 10, y_offset), font, font_scale, font_color, thickness)
    
    # 添加距离
    y_offset += 30
    distance_text = f"Distance: {distance:.6f}"
    cv2.putText(combined_img, distance_text, (10, y_offset), font, font_scale, font_color, thickness)
    
    # 如果图像高度不够，扩展图像
    current_height, current_width = combined_img.shape[:2]
    needed_height = y_offset + 50
    if needed_height > current_height:
        extra_height = needed_height - current_height
        extra_area = np.zeros((extra_height, current_width, 3), dtype=combined_img.dtype)
        combined_img = np.vstack((combined_img, extra_area))
        # 重新添加文本
        y_offset = height + 30
        cv2.putText(combined_img, f"File 1: {file1_path}", (10, y_offset), font, font_scale, font_color, thickness)
        cv2.putText(combined_img, f"File 2: {file2_path}", (width1 + 10, y_offset), font, font_scale, font_color, thickness)
        y_offset += 30
        cv2.putText(combined_img, hu1_text, (10, y_offset), font, font_scale, font_color, thickness)
        cv2.putText(combined_img, hu2_text, (width1 + 10, y_offset), font, font_scale, font_color, thickness)
        y_offset += 30
        cv2.putText(combined_img, distance_text, (10, y_offset), font, font_scale, font_color, thickness)
    
    # 保存图像
    output_path = os.path.join(temp_dir, f"similar_pair_{index}.jpg")
    cv2.imwrite(output_path, combined_img)
    print(f"  对比图已保存至: {output_path}")


def main():
    """
    主函数
    """
    print("计算所有 ppm 文件的 Hu 不变矩:")
    find_similar_images(threshold=0.5)


if __name__ == "__main__":
    main()