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

def calculate_hu_moments(image):
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    moments = cv2.moments(binary)
    hu = cv2.HuMoments(moments).flatten()
    return hu

def calculate_zernike_moments(image, radius=64, degree=8):
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    _, binary = cv2.threshold(gray, 127, 1, cv2.THRESH_BINARY)
    zm = mahotas.features.zernike_moments(binary, radius, degree)
    return np.array(zm)

def hu_distance(hu1, hu2):
    # 前五项用欧氏距离，后两项用绝对值差
    diff = np.abs(hu1 - hu2)

    # 对于第6个（索引5）和第7个（索引6）Hu不变矩，使用绝对值差
    # 因为这些值在镜像反射时会改变符号
    diff[5] = np.abs(np.abs(hu1[5]) - np.abs(hu2[5]))
    diff[6] = np.abs(np.abs(hu1[6]) - np.abs(hu2[6]))

    # 计算欧几里得距离
    return np.linalg.norm(diff)

def zernike_distance(zm1, zm2):
    # 一般直接用欧氏距离或对分量取绝对值后再算距离
    return np.linalg.norm(zm1 - zm2)

def euclidean_distance(vec1, vec2):
    return np.linalg.norm(vec1 - vec2)

def stat_moments_distance(data_root="../../data"):
    # 1. 收集所有图片的特征
    folder_features = {}
    subdirs = [d for d in os.listdir(data_root) if os.path.isdir(os.path.join(data_root, d))]
    for subdir in subdirs:
        subdir_path = os.path.join(data_root, subdir)
        ppm_files = [f for f in os.listdir(subdir_path) if f.endswith(".ppm")]
        features = []
        for filename in ppm_files:
            filepath = os.path.join(subdir_path, filename)
            try:
                img = load_map_image(filepath)
                hu = calculate_hu_moments(img)
                zm = calculate_zernike_moments(img)
                features.append({'file': filename, 'hu': hu, 'zm': zm})
            except Exception as e:
                print(f"处理文件 {subdir}/{filename} 时出错: {e}")
        folder_features[subdir] = features

    # 2. 统计每个文件夹内的距离最大最小值
    print("\n每个文件夹内图片的 Hu/Zernike Moments 距离最大最小值：")
    for subdir, feats in folder_features.items():
        hu_distances = []
        zm_distances = []
        n = len(feats)
        for i in range(n):
            for j in range(i+1, n):
                hu_dist = hu_distance(feats[i]['hu'], feats[j]['hu'])
                zm_dist = zernike_distance(feats[i]['zm'], feats[j]['zm'])
                hu_distances.append(hu_dist)
                zm_distances.append(zm_dist)
        if hu_distances:
            print(f"\n{subdir}:")
            print(f"  Hu Moments 距离: min={min(hu_distances):.6f}, max={max(hu_distances):.6f}")
            print(f"  Zernike Moments 距离: min={min(zm_distances):.6f}, max={max(zm_distances):.6f}")
        else:
            print(f"\n{subdir}: 图片数量不足，无法统计距离。")

    # 3. 统计不同文件夹之间的距离最小值
    print("\n不同文件夹之间图片的 Hu/Zernike Moments 距离最小值：")
    for i in range(len(subdirs)):
        for j in range(i+1, len(subdirs)):
            folder1 = subdirs[i]
            folder2 = subdirs[j]
            feats1 = folder_features[folder1]
            feats2 = folder_features[folder2]
            hu_min = None
            zm_min = None
            for f1 in feats1:
                for f2 in feats2:
                    hu_dist = hu_distance(f1['hu'], f2['hu'])
                    zm_dist = zernike_distance(f1['zm'], f2['zm'])
                    if hu_min is None or hu_dist < hu_min:
                        hu_min = hu_dist
                    if zm_min is None or zm_dist < zm_min:
                        zm_min = zm_dist
            print(f"\n{folder1} <-> {folder2}:")
            print(f"  Hu Moments 距离最小值: {hu_min:.6f}" if hu_min is not None else "  无法统计")
            print(f"  Zernike Moments 距离最小值: {zm_min:.6f}" if zm_min is not None else "  无法统计")

if __name__ == "__main__":
    stat_moments_distance()