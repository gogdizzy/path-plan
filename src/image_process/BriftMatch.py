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


def detect_brief_keypoints(image):
    """
    使用FAST检测器和BRIEF描述子检测图像的关键点和描述符
    """
    # 转换为灰度图像（如果还不是）
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # 创建 FAST 特征点检测器，调整参数以检测更多特征点
    # 降低阈值以检测更多特征点
    fast = cv2.FastFeatureDetector_create(
        threshold=10,        # 降低阈值以检测更多特征点（默认通常是10-20）
        nonmaxSuppression=True  # 使用非最大抑制来获得更均匀分布的特征点
    )
    
    # 创建 BRIEF 描述子提取器
    brief = cv2.xfeatures2d.BriefDescriptorExtractor_create()
    
    # 检测关键点
    keypoints = fast.detect(gray, None)
    
    # 计算描述符
    keypoints, descriptors = brief.compute(gray, keypoints)
    
    return keypoints, descriptors


def match_and_display_keypoints(img1, keypoints1, descriptors1, img2, keypoints2, descriptors2):
    """
    匹配两个图像的 BRIEF 关键点并显示匹配结果
    """
    # 创建 BFMatcher 对象 (BRIEF 使用汉明距离)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    # 进行特征匹配
    matches = bf.match(descriptors1, descriptors2)
    
    # 按距离排序
    matches = sorted(matches, key=lambda x: x.distance)
    
    # 取前50个匹配点（或更少）
    good_matches = matches[:50]
    
    # 判断图像相似性
    similarity_thresholds = {
        "low": 10,
        "medium": 20,
        "high": 30
    }
    
    if len(good_matches) < similarity_thresholds["low"]:
        similarity = "低"
    elif len(good_matches) < similarity_thresholds["medium"]:
        similarity = "中等"
    elif len(good_matches) < similarity_thresholds["high"]:
        similarity = "高"
    else:
        similarity = "很高"
    
    print(f"图像相似性: {similarity} (匹配点数: {len(good_matches)})")
    
    # 在图像上绘制匹配结果
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
    
    # 绘制匹配的特征点连线
    for match in good_matches:
        # 获取匹配点的坐标
        pt1 = tuple(map(int, keypoints1[match.queryIdx].pt))
        pt2 = tuple(map(int, keypoints2[match.trainIdx].pt))
        
        # 调整第二张图像中点的 x 坐标（因为图像被拼接了）
        pt2_shifted = (pt2[0] + width1, pt2[1])
        
        # 绘制关键点
        cv2.circle(combined_image, pt1, 5, (0, 255, 0), 2)
        cv2.circle(combined_image, pt2_shifted, 5, (0, 255, 0), 2)
        
        # 绘制连线
        cv2.line(combined_image, pt1, pt2_shifted, (255, 0, 0), 1)
    
    # 显示结果
    cv2.imshow('BRIEF Matches', combined_image)
    print(f"找到 {len(good_matches)} 个匹配点")
    
    # 等待按键并关闭窗口
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return good_matches


def process_two_images(image_path1, image_path2):
    """
    处理两个图像文件：提取 BRIEF 关键点并进行匹配
    """
    # 加载图像
    img1 = load_map_image(image_path1)
    img2 = load_map_image(image_path2)
    
    # 对 img1 进行深拷贝
    img1_copy = np.copy(img1)
    
    # 对第二张图像进行90度旋转
    img2_rotated = cv2.rotate(img2, cv2.ROTATE_90_CLOCKWISE)
    
    print(f"图像1尺寸: {img1.shape}")
    print(f"图像1拷贝尺寸: {img1_copy.shape}")
    print(f"图像2尺寸: {img2.shape}")
    print(f"旋转后图像2尺寸: {img2_rotated.shape}")
    
    # 检测 BRIEF 关键点和描述符
    keypoints1, descriptors1 = detect_brief_keypoints(img1_copy)
    keypoints2, descriptors2 = detect_brief_keypoints(img2_rotated)
    
    print(f"图像1检测到 {len(keypoints1)} 个关键点")
    print(f"图像2检测到 {len(keypoints2)} 个关键点")
    
    # 匹配关键点并显示结果
    matches = match_and_display_keypoints(img1_copy, keypoints1, descriptors1, img2_rotated, keypoints2, descriptors2)
    
    return matches


def main():
    """
    主函数 - 处理 data 文件夹中的 ppm 地图文件
    """
    # 设置地图文件路径
    data_folder = "../../data/rr5d2e320bf8d820.RAPTGD44600238"
    
    # 获取所有 ppm 文件
    ppm_files = [f for f in os.listdir(data_folder) if f.endswith(".ppm")]
    
    # 每次处理两个文件
    for i in range(0, len(ppm_files)-1, 2):
        file1 = ppm_files[i]
        file2 = ppm_files[i+1]
        
        map_path1 = os.path.join(data_folder, file1)
        map_path2 = os.path.join(data_folder, file2)
        
        print(f"处理地图文件对: {file1} 和 {file2}")
        
        try:
            matches = process_two_images(map_path1, map_path2)
        except Exception as e:
            print(f"处理文件 {file1} 和 {file2} 时出错: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()