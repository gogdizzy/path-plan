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


def match_and_display_hu_moments(img1, hu_moments1, img2, hu_moments2):
    """
    对比两个图像的 Hu 不变矩并显示匹配结果
    """
    # 计算两个图像 Hu 不变矩之间的距离
    # 使用 L2 距离（欧几里得距离），但对第6和第7个值使用绝对值差
    diff = np.abs(hu_moments1 - hu_moments2)
    
    # 对于第6个（索引5）和第7个（索引6）Hu不变矩，使用绝对值差
    # 因为这些值在镜像反射时会改变符号
    diff[5] = np.abs(np.abs(hu_moments1[5]) - np.abs(hu_moments2[5]))
    diff[6] = np.abs(np.abs(hu_moments1[6]) - np.abs(hu_moments2[6]))
    
    # 计算欧几里得距离
    distance = np.linalg.norm(diff)
    
    # 判断图像相似性
    # Hu 不变矩距离越小，图像越相似
    if distance < 0.1:
        similarity = "很高"
    elif distance < 0.5:
        similarity = "高"
    elif distance < 1.0:
        similarity = "中等"
    else:
        similarity = "低"
    
    print(f"图像相似性: {similarity} (Hu 不变矩距离: {distance:.4f})")
    
    # 在图像上显示结果
    # 将两张图像横向拼接
    height1, width1 = img1.shape[:2]
    height2, width2 = img2.shape[:2]
    
    # 创建一个新的图像来显示匹配结果
    combined_height = max(height1, height2)
    combined_width = width1 + width2
    combined_image = np.zeros((combined_height, combined_width, 3), dtype=img1.dtype)
    
    # 复制第一张图像
    if len(img1.shape) == 2:  # 灰度图
        combined_image[:height1, :width1, :] = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)
    else:
        combined_image[:height1, :width1, :] = img1
    
    # 复制第二张图像
    if len(img2.shape) == 2:  # 灰度图
        combined_image[:height2, width1:width1+width2, :] = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)
    else:
        combined_image[:height2, width1:width1+width2, :] = img2
    
    # 显示结果
    cv2.imshow('Hu Moments Comparison', combined_image)
    print(f"Hu 不变矩距离: {distance:.4f}")
    
    # 等待按键并关闭窗口
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return distance


def process_two_images(image_path1, image_path2):
    """
    处理两个图像文件：计算 Hu 不变矩并进行匹配
    """
    # 加载图像
    img1 = load_map_image(image_path1)
    img2 = load_map_image(image_path2)
    
    # 对 img1 进行深拷贝
    img1_copy = np.copy(img1)
    
    # 对第二张图像进行90度旋转
    #img2_rotated = cv2.rotate(img2, cv2.ROTATE_90_CLOCKWISE)
    img2_rotated = img2
    
    print(f"图像1尺寸: {img1.shape}")
    print(f"图像1拷贝尺寸: {img1_copy.shape}")
    print(f"图像2尺寸: {img2.shape}")
    print(f"旋转后图像2尺寸: {img2_rotated.shape}")
    
    # 计算 Hu 不变矩
    hu_moments1 = calculate_hu_moments(img1_copy)
    hu_moments2 = calculate_hu_moments(img2_rotated)
    
    print(f"图像1的 Hu 不变矩: {hu_moments1}")
    print(f"图像2的 Hu 不变矩: {hu_moments2}")
    
    # 匹配并显示结果
    distance = match_and_display_hu_moments(img1_copy, hu_moments1, img2_rotated, hu_moments2)
    
    return distance


def main():
    """
    主函数 - 处理 data 文件夹中的 ppm 地图文件
    """
    # 设置地图文件路径
    data_folder = "../../data/rr5fe6be36ac9850.RAPEBD50402969"
    
    # 获取所有 ppm 文件
    ppm_files = [f for f in os.listdir(data_folder) if f.endswith(".ppm")]
    
    # 存储所有文件的 Hu 不变矩
    all_hu_moments = {}
    
    # 先计算并输出每个文件的 Hu 不变矩
    print("计算每个文件的 Hu 不变矩:")
    for filename in ppm_files:
        map_path = os.path.join(data_folder, filename)
        try:
            img = load_map_image(map_path)
            hu_moments = calculate_hu_moments(img)
            all_hu_moments[filename] = hu_moments
            print(f"{filename}: {hu_moments}")
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {e}")
    
    print("\n开始进行文件对比:")
    
    # 每次处理两个文件
    for i in range(0, len(ppm_files)-1, 2):
        file1 = ppm_files[i]
        file2 = ppm_files[i+1]
        
        map_path1 = os.path.join(data_folder, file1)
        map_path2 = os.path.join(data_folder, file2)
        
        print(f"\n处理地图文件对: {file1} 和 {file2}")
        
        try:
            distance = process_two_images(map_path1, map_path2)
        except Exception as e:
            print(f"处理文件 {file1} 和 {file2} 时出错: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()