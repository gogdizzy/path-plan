import cv2
import numpy as np

K = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], dtype=np.float32)
dist = np.array([0.01, -0.01, 0, 0, 0], dtype=np.float32)

img = cv2.imread('../../data/111.jpg')
undistorted = cv2.undistort(img, K, dist)
cv2.imwrite('../../data/output.jpg', undistorted)