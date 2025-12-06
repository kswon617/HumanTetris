# -----------------------------------------------------------------------------
# main.py
#
# 게임의 메인 루프.
# OpenCV로 카메라 입력을 받고, Pygame으로 게임 화면을 렌더링하며,
# 사용자의 포즈를 인식하여 게임 상태를 업데이트합니다.
# -----------------------------------------------------------------------------

import cv2
import pygame
import random
import time
from collections import deque

# 직접 만든 모듈 임포트
from settings import *
from pose_detector import PoseDetector
from game_logic import GameLogic
from block_templates import POSE_TEMPLATES

# --- 그리기 헬퍼 함수 ---

def draw_text(screen, text, size, x, y, color=WHITE, bg_color=(0, 0, 0), alpha=180):
    """화면에 반투명 배경과 함께 텍스트를 그리는 함수"""
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))

    # 반투명 배경 생성
    if bg_color:
        bg_rect = text_rect.inflate(20, 10)  # 텍스트 주변에 여백 추가
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((*bg_color, alpha))
        screen.blit(bg_surface, bg_rect.topleft)

    screen.blit(text_surface, text_rect)


def draw_grid_border(screen):
    """테트리스 그리드의 테두리를 그리는 함수"""
    pygame.draw.rect(screen, GRAY, (GRID_X - 2, GRID_Y - 2, GRID_WIDTH + 4, GRID_HEIGHT + 4), 2)


def draw_candidate_blocks(screen, candidates, selected_zone=None):
    """화면 상단에 후보 블록과 선택 존(Zone)을 그리는 함수

    candidates는 템플릿 객체들의 리스트로 가정한다.
    """
    if not candidates:
        return
    
    zone_width = SCREEN_WIDTH // len(candidates)
    for i, template in enumerate(candidates):
        zone_x = i * zone_width
        
        # 현재 사용자가 위치한 존(Zone)을 반투명 배경으로 하이라이트
        if selected_zone == i:
            highlight_surface = pygame.Surface((zone_width, 200), pygame.SRCALPHA)
            highlight_surface.fill((80, 80, 80, 150)) # 밝은 회색, 반투명
            screen.blit(highlight_surface, (zone_x, 0))
        
        # 블록 이름 표시 (배경 없음)
        draw_text(screen, template['name'], 24, zone_x + zone_width // 2, 100, bg_color=None)
        
        # 블록 모양 그리기
        shape = template['shape']
        for r, row in enumerate(shape):
            for c, cell in enumerate(row):
                if cell:
                    block_x = zone_x + zone_width // 2 + c * 20 - (len(row) * 20 // 2)
                    block_y = 130 + r * 20
                    pygame.draw.rect(screen, WHITE, (block_x, block_y, 20, 20))
                    pygame.draw.rect(screen, GRAY, (block_x, block_y, 20, 20), 1)


def draw_live_top3(screen, similarities):
    """오른쪽 상단에 실시간 Top-3 후보(이름 + score)를 표시"""
    x = SCREEN_WIDTH - 220
    y = 80
    draw_text(screen, "Live Top-3", 22, x + 100, y - 30, bg_color=None)
    for i, (key, score) in enumerate(similarities[:3]):
        name = POSE_TEMPLATES[key]['name'] if key in POSE_TEMPLATES else str(key)
        text = f"{i+1}. {name} ({score:.2f})"
        draw_text(screen, text, 20, x + 100, y + i * 36, bg_color=None)


# --- 메인 게임 함수 ---

def main():
    # 1. 초기화
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Human Tetris")
    clock = pygame.time.Clock()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("에러: 카메라를 열 수 없습니다.")
        return

    pose_detector = PoseDetector()
    game_logic = GameLogic()
    
    # 2. 게임 상태 및 변수 선언
    game_state = STATE_RECOGNITION
    candidate_blocks = []             # 상위 3개 후보 블록 (템플릿 객체 리스트)
    selected_block_info = None        # 사용자가 선택한 블록 정보
    pose_timer_start = 0              # POSE_SELECTION에서 사용하는 타이머
    fall_timer_start = time.time()    # 블록 자동 하강 타이머

    # 포즈 5초 유지 관련
    POSE_MATCH_HOLD_TIME = 5.0        # 사용자가 포즈를 5초 동안 유지해야 함
    pose_match_start = None           # 포즈 유지 시작 시각
    last_top1_key = None              # 5초 동안 마지막으로 관찰된 Top-1 키

    # 좌우 이동 감지를 위한 변수 (선택 존 감지에도 사용)
    shoulder_x_history = deque(maxlen=10) # 어깨 중심의 x좌표 기록

    # 3. 메인 게임 루프
    running = True
    while running:
        # --- 이벤트 처리 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False

        # --- 카메라 프레임 처리 ---
        success, img = cap.read()
        if not success:
            continue
        
        img = cv2.flip(img, 1) # 좌우 반전 (거울 모드)
        img_posed = pose_detector.find_pose(img.copy(), draw=True)
        lm_list = pose_detector.get_landmarks_list(img)
        user_vectors = pose_detector.get_body_vectors(lm_list) if lm_list else None

        cam_width = img.shape[1]

        # --- 유사도 계산: 매 프레임마다 전체 템플릿과 비교하여 Top-3 계산 ---
        similarities = []  # list of (key, score) sorted desc
        if user_vectors:
            for key, template in POSE_TEMPLATES.items():
                sim = PoseDetector.compare_poses(template['vectors'], user_vectors)
                similarities.append((key, sim))
            similarities.sort(key=lambda x: x[1], reverse=True)

        # 어깨 중심 좌표 계산 및 현재 위치 존(Zone) 확인
        current_zone = None
        if lm_list and similarities:
            left_shoulder, right_shoulder = lm_list[11], lm_list[12]
            shoulder_center_x_cam = (left_shoulder[1] + right_shoulder[1]) / 2

            candidate_count = min(3, len(similarities))
            zone_width = SCREEN_WIDTH / candidate_count

            shoulder_center_x_screen = shoulder_center_x_cam * (SCREEN_WIDTH / cam_width)

            # --- 수정: 정확한 존 계산 (부동소수점 → int 변환 오류 제거) ---
            current_zone = int(shoulder_center_x_screen / zone_width)
            if current_zone < 0:
                current_zone = 0
            elif current_zone >= candidate_count:
                current_zone = candidate_count - 1

        # --- 화면 그리기 ---

        # 1. 카메라 영상을 전체 배경으로 설정
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pygame = pygame.image.frombuffer(img_rgb.tobytes(), img_rgb.shape[1::-1], "RGB")
        img_pygame = pygame.transform.scale(img_pygame, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(img_pygame, (0, 0))
        
        # 2. 그리드 영역에 반투명 배경 추가
        grid_surface = pygame.Surface((GRID_WIDTH, GRID_HEIGHT), pygame.SRCALPHA)
        grid_surface.fill((0, 0, 0, 150)) # 검은색, 반투명
        screen.blit(grid_surface, (GRID_X, GRID_Y))

        # 3. 공통 UI 그리기
        draw_grid_border(screen)
        game_logic.draw_grid(screen) # 고정된 블록들 그리기
        draw_text(screen, f"Score: {game_logic.score}", 40, 150, 50)
        
        # --- 게임 상태별 로직 & 그리기 ---

        if game_state == STATE_RECOGNITION:
            draw_text(screen, "POSE as you NEED!", 50, SCREEN_WIDTH // 2, 50)

            if user_vectors and similarities:
                # 매 프레임 Top-3 템플릿을 갱신
                top3_keys = [k for k, s in similarities[:3]]
                candidate_blocks = [POSE_TEMPLATES[k] for k in top3_keys]

                # 후보 블록을 화면에 그림
                draw_candidate_blocks(screen, candidate_blocks)

                # 오른쪽 상단에 실시간 Top-3와 점수 표시
                draw_live_top3(screen, similarities)

                # 사용자가 특정 존에 들어가고 해당 존의 템플릿이 일정 유사도 이상이면 타이머 시작
                if current_zone is not None:
                    target_key = top3_keys[current_zone]
                    target_score = dict(similarities)[target_key]

                    if target_score > POSE_SIMILARITY_THRESHOLD:
                        # 포즈 유지 타이머 시작
                        if pose_match_start is None:
                            pose_match_start = time.time()
                            # 초기 last_top1을 현재 Top-1으로 설정
                            last_top1_key = similarities[0][0]

                        # 동안에는 Top-1을 계속 갱신 (마지막 순간 값이 사용됨)
                        last_top1_key = similarities[0][0]

                        elapsed = time.time() - pose_match_start
                        draw_text(screen, f"POSE RECOGNIZING: {elapsed:.1f}s / {POSE_MATCH_HOLD_TIME}s", 26, SCREEN_WIDTH//2, 220)
                        # 진행 바 표시
                        progress = min(1.0, elapsed / POSE_MATCH_HOLD_TIME)
                        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH//2 - 150, 250, 300 * progress, 30))

                        # 5초 유지 성공하면 최종 Top-1을 선택하고 Selection 상태로 전환
                        if elapsed >= POSE_MATCH_HOLD_TIME:
                            # 마지막에 관찰된 Top-1을 선택
                            final_key = last_top1_key
                            selected_block_info = POSE_TEMPLATES[final_key]

                            # Selection 단계 진입 (기존 로직에 맞게 포즈 타이머 초기화)
                            pose_timer_start = time.time()
                            game_state = STATE_SELECTION

                            # 타이머 리셋
                            pose_match_start = None
                            last_top1_key = None
                    else:
                        # 유사도 기준 미달 -> 타이머 리셋
                        pose_match_start = None
                        last_top1_key = None
                else:
                    # 존에 있지 않다면 타이머 리셋
                    pose_match_start = None
                    last_top1_key = None

            else:
                # 포즈가 인식되지 않으면 안내 문구 표시
                draw_candidate_blocks(screen, candidate_blocks, current_zone) # 후보는 계속 표시
                draw_text(screen, "Show your WHOLE Body", 40, SCREEN_WIDTH // 2, 150)
                # 리셋
                pose_match_start = None
                last_top1_key = None

        elif game_state == STATE_SELECTION:
            # Selection 단계: 한번 진입하면 역행하지 않도록 유지
            draw_text(screen, f"Stay still for {POSE_SELECTION_TIME}secs!", 40, SCREEN_WIDTH // 2, 50)
            draw_candidate_blocks(screen, candidate_blocks, current_zone)

            if user_vectors and candidate_blocks:
                target_template = selected_block_info
                similarity = PoseDetector.compare_poses(target_template['vectors'], user_vectors)

                # 사용자가 자세에서 잠깐 흔들려도 상태를 역행하지 않도록 유지
                if similarity > POSE_SIMILARITY_THRESHOLD:
                    # 포즈가 안정되면 기존 타이머 계속(처음 진입시 설정된 pose_timer_start 사용)
                    hold_time = time.time() - pose_timer_start
                    draw_text(screen, f"Selecting: {target_template['name']}", 30, SCREEN_WIDTH // 2, 220)
                    progress = min(1.0, hold_time / POSE_SELECTION_TIME)
                    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH//2 - 150, 250, 300 * progress, 30))

                    if hold_time >= POSE_SELECTION_TIME:
                        game_logic.create_tetromino(selected_block_info)
                        fall_timer_start = time.time()
                        game_state = STATE_PLAYING
                else:
                    # 자세가 흐트러져도 RECOGNITION으로 역행하지 않음.
                    # 대신 경고 문구를 보여주고 pose_timer_start를 리셋하여 다시 유지해야 함.
                    draw_text(screen, "Stay still!", 26, SCREEN_WIDTH//2, 220)
                    # 리셋하되 상태는 그대로 유지
                    pose_timer_start = time.time()
            else:
                # landmark 사라져도 Selection에서 바로 RECOGNITION으로 가지 않음
                draw_text(screen, "Out of screen. Come back!", 26, SCREEN_WIDTH//2, 220)
                pose_timer_start = time.time()

        elif game_state == STATE_PLAYING:
            if game_logic.game_over:
                game_state = STATE_GAME_OVER
                continue

            # 블록 자동 하강
            if time.time() - fall_timer_start > INITIAL_FALL_INTERVAL:
                game_logic.move(0, 1)
                fall_timer_start = time.time()

            # "서 있는 위치" 기반으로 블록 조작
            if lm_list:
                left_shoulder, right_shoulder = lm_list[11], lm_list[12]
                shoulder_center_x_cam = (left_shoulder[1] + right_shoulder[1]) / 2

                # 카메라 좌표를 화면 좌표로 매핑
                shoulder_center_x_screen = shoulder_center_x_cam * (SCREEN_WIDTH / cam_width)

                # 화면을 3등분하여 현재 위치 파악
                zone_third = SCREEN_WIDTH / 3
                if shoulder_center_x_screen < zone_third: # 왼쪽 존
                    game_logic.move(-1, 0)
                elif shoulder_center_x_screen > zone_third * 2: # 오른쪽 존
                    game_logic.move(1, 0)
                # 중앙 존에서는 움직이지 않음

            # 움직이는 블록 그리기
            game_logic.draw_current_tetromino(screen)

            # 현재 블록이 없다면 (블록이 바닥에 닿았다면) 다음 블록을 위해 인식 단계로 전환
            if game_logic.current_tetromino is None:
                game_state = STATE_RECOGNITION
                candidate_blocks = [] # 후보 블록 리스트 초기화
            
        elif game_state == STATE_GAME_OVER:
            draw_text(screen, "GAME OVER", 100, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            draw_text(screen, f"Final Score: {game_logic.score}", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            draw_text(screen, "Press 'Q' to Quit", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)

        # --- 최종 화면 업데이트 ---
        # 랜드마크가 그려진 포즈 이미지를 좌측 하단에 작게 표시
        img_posed_rgb = cv2.cvtColor(img_posed, cv2.COLOR_BGR2RGB)
        img_posed_pygame = pygame.image.frombuffer(img_posed_rgb.tobytes(), img_posed_rgb.shape[1::-1], "RGB")
        pose_view = pygame.transform.scale(img_posed_pygame, (320, 240))
        screen.blit(pose_view, (20, SCREEN_HEIGHT - 260))

        pygame.display.flip()
        clock.tick(FPS)

    # 4. 종료
    cap.release()
    pygame.quit()

if __name__ == '__main__':
    main()
