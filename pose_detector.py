# -----------------------------------------------------------------------------
# pose_detector.py
#
# MediaPipe를 사용하여 사용자의 포즈를 감지하고,
# 신체 주요 관절의 각도를 계산하여 벡터로 반환하는 클래스.
# -----------------------------------------------------------------------------

import cv2
import mediapipe as mp
import numpy as np
import math

class PoseDetector:
    """
    MediaPipe Pose 모델을 사용하여 신체 포즈를 감지하는 클래스.
    """
    def __init__(self, detection_confidence=0.5, tracking_confidence=0.5):
        # MediaPipe Pose 모델 초기화
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.landmarks = None

    def find_pose(self, img, draw=True):
        """
        입력 이미지에서 포즈를 찾고, 결과 랜드마크 위에 선을 그립니다.
        
        :param img: 처리할 이미지 (OpenCV BGR 형식)
        :param draw: 랜드마크 위에 그림을 그릴지 여부
        :return: 랜드마크가 그려진 이미지
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.pose.process(img_rgb)
        self.landmarks = results.pose_landmarks

        if self.landmarks and draw:
            self.mp_draw.draw_landmarks(img, self.landmarks, self.mp_pose.POSE_CONNECTIONS)
        
        return img

    def get_landmarks_list(self, img):
        """
        감지된 랜드마크의 화면 좌표(x, y) 리스트를 반환합니다.
        
        :param img: 좌표를 계산할 기준 이미지
        :return: 각 랜드마크의 [id, x, y]를 담은 리스트
        """
        lm_list = []
        if self.landmarks:
            h, w, _ = img.shape
            for id, lm in enumerate(self.landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
        return lm_list

    def _calculate_angle(self, lm_list, p1, p2, p3):
        """세 점(p1, p2, p3) 사이의 각도를 계산합니다. p2가 중심점입니다."""
        try:
            x1, y1 = lm_list[p1][1:]
            x2, y2 = lm_list[p2][1:]
            x3, y3 = lm_list[p3][1:]

            # atan2를 사용하여 벡터 간의 각도를 계산
            angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - 
                                 math.atan2(y1 - y2, x1 - x2))
            if angle < 0:
                angle += 360
            return angle
        except IndexError:
            return 0 # 랜드마크가 감지되지 않은 경우

    def get_body_vectors(self, lm_list):
        """
        주요 신체 부위의 각도를 계산하여 벡터(딕셔너리) 형태로 반환합니다.
        
        :param lm_list: get_landmarks_list()로부터 얻은 랜드마크 리스트
        :return: 부위별 각도 정보가 담긴 딕셔너리
        """
        if len(lm_list) < 32: # MediaPipe가 모든 랜드마크를 감지했는지 확인
            return None

        vectors = {
            'right_arm': self._calculate_angle(lm_list, 11, 13, 15), # R Shoulder, Elbow, Wrist
            'left_arm': self._calculate_angle(lm_list, 12, 14, 16),  # L Shoulder, Elbow, Wrist
            'right_leg': self._calculate_angle(lm_list, 23, 25, 27), # R Hip, Knee, Ankle
            'left_leg': self._calculate_angle(lm_list, 24, 26, 28),   # L Hip, Knee, Ankle
            'right_body': self._calculate_angle(lm_list, 11, 23, 25),# R Shoulder, Hip, Knee
            'left_body': self._calculate_angle(lm_list, 12, 24, 26), # L Shoulder, Hip, Knee
        }
        return vectors

    @staticmethod
    def compare_poses(template_vectors, user_vectors, tolerance=30):


        if user_vectors is None or template_vectors is None:
            return 0

        common_keys = template_vectors.keys()
        total = 0
        match = 0

        for key in common_keys:
            t = template_vectors[key]
            u = user_vectors[key]

            diff = abs(t - u)
            diff = min(diff, 360 - diff)   # 0~180 사이로 정규화

            if diff <= tolerance:
                match += 1

            total += 1

        return match / total
