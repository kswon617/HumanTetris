# -----------------------------------------------------------------------------
# main.py (FINAL - RECOGNITION_DURATION 추가된 버전)
# -----------------------------------------------------------------------------

import cv2
import pygame
import random
import time
from collections import deque, Counter

from settings import *
from pose_detector import PoseDetector
from game_logic import GameLogic
from block_templates import POSE_TEMPLATES


# ---------------------------------------------------------------------
# UI 헬퍼: 텍스트 / 후보 블록 / 카운트다운 바
# ---------------------------------------------------------------------
def draw_text(screen, text, size, x, y, color=WHITE, bg_color=(0, 0, 0), alpha=160):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))

    if bg_color:
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((*bg_color, alpha))
        screen.blit(bg_surface, bg_rect.topleft)

    screen.blit(text_surface, text_rect)


def draw_candidate_blocks(screen, candidates, selected_zone=None):
    if not candidates:
        return

    zone_width = SCREEN_WIDTH // len(candidates)
    for i, template in enumerate(candidates):
        zone_x = i * zone_width

        if selected_zone == i:
            highlight_surface = pygame.Surface((zone_width, 200), pygame.SRCALPHA)
            highlight_surface.fill((80, 80, 80, 130))
            screen.blit(highlight_surface, (zone_x, 0))

        draw_text(screen, template['name'], 26, zone_x + zone_width // 2, 90, bg_color=None)

        shape = template['shape']
        for r, row in enumerate(shape):
            for c, cell in enumerate(row):
                if cell:
                    bx = zone_x + zone_width // 2 + c * 20 - (len(row) * 20 // 2)
                    by = 130 + r * 20
                    pygame.draw.rect(screen, WHITE, (bx, by, 20, 20))
                    pygame.draw.rect(screen, GRAY, (bx, by, 20, 20), 1)


def draw_countdown_bar(screen, elapsed, total, center_y):
    progress = min(1.0, max(0.0, elapsed / total))
    BAR_W, BAR_H = 300, 30

    x = SCREEN_WIDTH // 2 - BAR_W // 2
    y = center_y

    # 채워진 부분과 테두리
    pygame.draw.rect(screen, GREEN, (x, y, BAR_W * progress, BAR_H))
    pygame.draw.rect(screen, WHITE, (x, y, BAR_W, BAR_H), 2)


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Human Tetris")
    clock = pygame.time.Clock()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Cannot access camera.")
        return

    pose_detector = PoseDetector()
    game_logic = GameLogic()

    # ---------------------------------------------------------
    # 설정 (RECOGNITION_DURATION 추가)
    # POSE_SELECTION_TIME 은 settings.py에 정의되어 있다고 가정
    # ---------------------------------------------------------
    RECOGNITION_DURATION = 5.0  # Recognition 단계 관찰 시간 (초)
    # POSE_SELECTION_TIME는 settings.py에서 가져옴

    # 게임 상태 변수
    game_state = STATE_RECOGNITION
    candidate_blocks = []
    recognition_start = None
    recognition_counter = Counter()

    auto_select_start = None
    fall_timer_start = time.time()

    shoulder_x_history = deque(maxlen=10)

    running = True
    while running:
        # 이벤트
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False

        # 카메라 프레임
        success, img = cap.read()
        if not success:
            continue

        img = cv2.flip(img, 1)  # 거울 모드
        img_posed = pose_detector.find_pose(img.copy(), draw=True)
        lm_list = pose_detector.get_landmarks_list(img)
        user_vectors = pose_detector.get_body_vectors(lm_list) if lm_list else None

        cam_width = img.shape[1]

        # 각 템플릿과 유사도 계산 (Recognition에서 top 후보 표시용)
        similarities = []
        if user_vectors:
            for key, template in POSE_TEMPLATES.items():
                sim = PoseDetector.compare_poses(template['vectors'], user_vectors)
                similarities.append((key, sim))
            similarities.sort(key=lambda x: x[1], reverse=True)

        # 어깨 중심으로 zone 계산
        current_zone = None
        if lm_list:
            left_sh, right_sh = lm_list[11], lm_list[12]
            shoulder_center_x_cam = (left_sh[1] + right_sh[1]) / 2
            zone_count = 3 if game_state == STATE_RECOGNITION else max(1, len(candidate_blocks))
            zone_width = SCREEN_WIDTH / zone_count
            shoulder_center_x_screen = shoulder_center_x_cam * (SCREEN_WIDTH / cam_width)
            current_zone = int(shoulder_center_x_screen / zone_width)
            current_zone = max(0, min(zone_count - 1, current_zone))

        # 화면 그리기 (카메라 배경)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cam_surf = pygame.image.frombuffer(img_rgb.tobytes(), img_rgb.shape[1::-1], "RGB")
        cam_surf = pygame.transform.scale(cam_surf, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(cam_surf, (0, 0))

        grid_surface = pygame.Surface((GRID_WIDTH, GRID_HEIGHT), pygame.SRCALPHA)
        grid_surface.fill((0, 0, 0, 150))
        screen.blit(grid_surface, (GRID_X, GRID_Y))

        draw_grid_border = lambda s: pygame.draw.rect(s, GRAY, (GRID_X - 2, GRID_Y - 2, GRID_WIDTH + 4, GRID_HEIGHT + 4), 2)
        draw_grid_border(screen)
        game_logic.draw_grid(screen)
        draw_text(screen, f"Score: {game_logic.score}", 40, 150, 50)

        # -----------------------------
        # RECOGNITION STATE
        # -----------------------------
        if game_state == STATE_RECOGNITION:
            if recognition_start is None:
                recognition_start = time.time()
                recognition_counter = Counter()

            draw_text(screen, "POSE as you NEED!", 44, SCREEN_WIDTH // 2, 50)

            if user_vectors and similarities:
                realtime_top3 = [k for k, _ in similarities[:3]]
                realtime_cands = [POSE_TEMPLATES[k] for k in realtime_top3]
                draw_candidate_blocks(screen, realtime_cands)

                top1_key, top1_score = similarities[0]
                if top1_score > POSE_SIMILARITY_THRESHOLD:
                    recognition_counter[top1_key] += 1

            elapsed = time.time() - recognition_start
            draw_text(screen, f"Recognizing... {elapsed:.1f}s / {RECOGNITION_DURATION:.1f}s", 26, SCREEN_WIDTH // 2, 220)
            draw_countdown_bar(screen, elapsed, RECOGNITION_DURATION, 250)

            if elapsed >= RECOGNITION_DURATION:
                final_keys = [k for k, _ in recognition_counter.most_common(3)]
                if len(final_keys) < 3:
                    for k, _ in similarities[:3]:
                        if k not in final_keys:
                            final_keys.append(k)
                        if len(final_keys) >= 3:
                            break

                candidate_blocks = [POSE_TEMPLATES[k] for k in final_keys]
                auto_select_start = None
                game_state = STATE_SELECTION
                recognition_start = None
                recognition_counter = Counter()

        # -----------------------------
        # SELECTION STATE
        # (3초 카운트다운, 3초 끝난 순간 zone 기반 선택, zone 없으면 랜덤)
        # -----------------------------
        elif game_state == STATE_SELECTION:
            if not candidate_blocks:
                game_state = STATE_RECOGNITION
                recognition_start = None
                recognition_counter = Counter()
                continue

            draw_text(screen, "Move into a Zone to Select a Block", 32, SCREEN_WIDTH // 2, 50)
            draw_candidate_blocks(screen, candidate_blocks, current_zone)

            if auto_select_start is None:
                auto_select_start = time.time()

            elapsed = time.time() - auto_select_start
            draw_text(screen, f"Selecting...  {elapsed:.1f}s / {POSE_SELECTION_TIME:.1f}s", 26, SCREEN_WIDTH // 2, 220)
            draw_countdown_bar(screen, elapsed, POSE_SELECTION_TIME, 250)

            if elapsed >= POSE_SELECTION_TIME:
                if current_zone is not None and 0 <= current_zone < len(candidate_blocks):
                    chosen_block = candidate_blocks[current_zone]
                else:
                    chosen_block = random.choice(candidate_blocks)

                game_logic.create_tetromino(chosen_block)
                fall_timer_start = time.time()
                game_state = STATE_PLAYING
                candidate_blocks = []
                auto_select_start = None

        # -----------------------------
        # PLAYING STATE
        # -----------------------------
        elif game_state == STATE_PLAYING:
            if game_logic.game_over:
                game_state = STATE_GAME_OVER
                continue

            if time.time() - fall_timer_start > INITIAL_FALL_INTERVAL:
                game_logic.move(0, 1)
                fall_timer_start = time.time()

            if lm_list:
                left_sh, right_sh = lm_list[11], lm_list[12]
                shoulder_center_x_cam = (left_sh[1] + right_sh[1]) / 2
                shoulder_center_x_screen = shoulder_center_x_cam * (SCREEN_WIDTH / cam_width)

                zone_third = SCREEN_WIDTH / 3
                if shoulder_center_x_screen < zone_third:
                    game_logic.move(-1, 0)
                elif shoulder_center_x_screen > zone_third * 2:
                    game_logic.move(1, 0)

            game_logic.draw_current_tetromino(screen)

            if game_logic.current_tetromino is None:
                game_state = STATE_RECOGNITION

        # -----------------------------
        # GAME OVER
        # -----------------------------
        elif game_state == STATE_GAME_OVER:
            draw_text(screen, "GAME OVER", 100, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            draw_text(screen, f"Final Score: {game_logic.score}", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            draw_text(screen, "Press 'Q' to Quit", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)

        # 포즈 미리보기
        img_posed_rgb = cv2.cvtColor(img_posed, cv2.COLOR_BGR2RGB)
        img_posed_pygame = pygame.image.frombuffer(img_posed_rgb.tobytes(), img_posed_rgb.shape[1::-1], "RGB")
        pose_view = pygame.transform.scale(img_posed_pygame, (320, 240))
        screen.blit(pose_view, (20, SCREEN_HEIGHT - 260))

        pygame.display.flip()
        clock.tick(FPS)

    cap.release()
    pygame.quit()


if __name__ == '__main__':
    main()
