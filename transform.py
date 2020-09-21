import cv2
import numpy as np


def orderPoints(pts):

    rect_pts = np.zeros((4,2))

    print(rect_pts)

    #top-left point will have minimum sum and bottom right point will have maximum sum

    pts_sum = np.sum(pts, axis=1)

    rect_pts[0] = pts[np.argmin(pts_sum)]
    rect_pts[2] = pts[np.argmax(pts_sum)]

    #top-right point will have maximum diff and bottom left point will have minimum diff
    pts_diff = np.diff(pts, axis=1)

    rect_pts[1] = pts[np.argmax(pts_diff)]
    rect_pts[3] = pts[np.argmin(pts_diff)]

    return rect_pts

def distance(pt1, pt2):
    # Calculates distance between two points
    print(pt1, pt2)
    return np.sqrt(np.square(pt2[0]-pt1[0]) + np.square(pt2[1]-pt1[1]))


def transform(image, src):

    """
    image: Pre-loaded image in BGR format
    src: Source 4-points that needs to be transformed
    """

    ordered_pts = orderPoints(src)
    H1 = distance(ordered_pts[0], ordered_pts[1])
    H2 = distance(ordered_pts[2], ordered_pts[3])
    W1 = distance(ordered_pts[0], ordered_pts[3])
    W2 = distance(ordered_pts[1], ordered_pts[2])

    dst_H = max(H1, H2)
    dst_W = max(W1, W2)

    dst_pts = np.array([[0, 0], [0, round(dst_H)], [round(dst_W), round(dst_H)], [round(dst_W), 0]], dtype="float32")

    trans_mat = cv2.getPerspectiveTransform(ordered_pts.astype(np.float32), dst_pts)

    new_img = cv2.warpPerspective(image, trans_mat, (round(dst_W), round(dst_H)))

    return new_img
