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
from collections import deque, Counter

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
    candidate_blocks = []             # 상위 3개 후보 블록 (템플릿 객체 리스트, Recognition 종료 시 고정)
    selected_block_info = None        # 사용자가 Selection에서 최종 선택한 블록 정보
    pose_timer_start = None           # Selection에서 사용자가 포즈 유지 시작 시각
    fall_timer_start = time.time()    # 블록 자동 하강 타이머

    # 포즈 5초 유지 관련 (Recognition 에서의 총 인식 시간)
    RECOGNITION_DURATION = 5.0        # Recognition 단계에서 총 5초 동안 관찰하여 후보 결정
    recognition_start = None          # Recognition 시작 시각
    recognition_counter = Counter()   # Recognition 동안 관찰된 Top-1 키 빈도 카운터

    
    # 포즈 매칭 임계값은 settings에 정의된 POSE_SIMILARITY_THRESHOLD 사용
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

        # 어깨 중심 좌표 계산 및 현재 위치 존(Zone) 확인 (화면 좌표 기준 zone)
        current_zone = None
        if lm_list and similarities and len(similarities) > 0:
            left_shoulder, right_shoulder = lm_list[11], lm_list[12]
            shoulder_center_x_cam = (left_shoulder[1] + right_shoulder[1]) / 2

            # candidate_count는 화면에 보이는 후보 수 (Recognition이 끝나기 전에는 실시간 top3, 끝나면 고정 후보 수)
            candidate_count = min(3, len(similarities)) if not candidate_blocks else len(candidate_blocks)
            zone_width = SCREEN_WIDTH / candidate_count if candidate_count > 0 else SCREEN_WIDTH

            shoulder_center_x_screen = shoulder_center_x_cam * (SCREEN_WIDTH / cam_width)

            # 안전한 정수 변환 및 범위 고정
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
            # Recognition 진입 시 시작 시간 초기화
            if recognition_start is None:
                recognition_start = time.time()
                recognition_counter = Counter()

            draw_text(screen, "POSE as you NEED! (Recognition)", 44, SCREEN_WIDTH // 2, 50)

            if user_vectors and similarities:
                # 매 프레임 Top-3 템플릿을 갱신하여 화면에 표시 (실시간 갱신)
                realtime_top3_keys = [k for k, s in similarities[:3]]
                realtime_candidate_blocks = [POSE_TEMPLATES[k] for k in realtime_top3_keys]
                # 화면에는 실시간 Top-3 보여주기
                draw_candidate_blocks(screen, realtime_candidate_blocks)
                draw_live_top3(screen, similarities)

                # Recognition 카운트: 매 프레임의 Top-1(가장 높은 유사도 키)을 관찰값으로 카운트
                top1_key, top1_score = similarities[0]
                if top1_score > POSE_SIMILARITY_THRESHOLD:
                    recognition_counter[top1_key] += 1

                # 진행 시간 표시
                elapsed_recog = time.time() - recognition_start
                remaining = max(0.0, RECOGNITION_DURATION - elapsed_recog)
                draw_text(screen, f"Recognizing... {elapsed_recog:.1f}s / {RECOGNITION_DURATION:.1f}s", 26, SCREEN_WIDTH//2, 220)
                pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH//2 - 150, 250, 300 * (elapsed_recog / RECOGNITION_DURATION), 30))

                # Recognition 기간이 끝나면 최종 Top-3 결정하고 Selection으로 전환
                if elapsed_recog >= RECOGNITION_DURATION:
                    # recognition_counter로부터 최빈값 기반 top3 결정
                    most_common = recognition_counter.most_common(3)  # [(key, cnt), ...]
                    final_keys = [k for k, c in most_common]

                    # 만약 recognition_counter에 후보가 적게 모였으면, 실시간 top3로 채움
                    if len(final_keys) < 3:
                        for k, s in similarities[:3]:
                            if k not in final_keys:
                                final_keys.append(k)
                            if len(final_keys) >= 3:
                                break

                    # 이제 candidate_blocks를 최종 고정(Selection에서 이 3개 중 선택)
                    candidate_blocks = [POSE_TEMPLATES[k] for k in final_keys]
                    # reset selection variables
                    selected_block_info = None
                    pose_timer_start = None

                    # move to selection state
                    game_state = STATE_SELECTION

                    # reset recognition anchors
                    recognition_start = None
                    recognition_counter = Counter()

            else:
                # 포즈가 인식되지 않을 때: 실시간 후보 표시(이전 후보 유지), 안내 문구
                draw_candidate_blocks(screen, candidate_blocks)
                draw_text(screen, "Show your WHOLE Body", 40, SCREEN_WIDTH // 2, 150)
                # recognition도 계속 진행 타이머는 리셋하지 않음 - 사용자가 없으면 단순히 관찰 안 된 것으로 처리됨

        elif game_state == STATE_SELECTION:
            # Selection 단계: Recognition에서 고정된 candidate_blocks 중에서 선택
            draw_text(screen, f"Select one of the final 3 by standing in a zone", 30, SCREEN_WIDTH // 2, 50)
            draw_candidate_blocks(screen, candidate_blocks, current_zone)


            # 후보가 없으면 안전하게 RECOGNITION으로 복귀
            if not candidate_blocks:
                game_state = STATE_RECOGNITION
                recognition_start = None
                recognition_counter = Counter()
                continue

            # 현재 화면에서 감지된 벡터가 있을 때만 selection 체크
            if user_vectors and current_zone is not None:
                # 안전하게 zone index 범위 맞추기
                if current_zone < 0:
                    current_zone = 0
                elif current_zone >= len(candidate_blocks):
                    current_zone = len(candidate_blocks) - 1

                # 사용자가 서있는 zone의 템플릿을 타깃으로 설정
                target_template = candidate_blocks[current_zone]

                # 타이머 시작(처음 zone에 들어갈 때)

                if pose_timer_start is None:
                    pose_timer_start = time.time()
                    selected_block_info = target_template  # 후보로 잠정 선택
                else:
                    # 만약 사용자가 zone을 바꿨다면 타이머 리셋하고 새 타겟 설정
                    if selected_block_info is not target_template:
                        
                        selected_block_info = target_template

                # 포즈 일치도 측정
                similarity = PoseDetector.compare_poses(target_template['vectors'], user_vectors)
                elapsed_hold = time.time() - pose_timer_start

                # UI
                draw_text(screen, f"Holding {target_template['name']}: {elapsed_hold:.1f}s / {POSE_SELECTION_TIME}s", 26, SCREEN_WIDTH//2, 220)
                progress = min(1.0, elapsed_hold / POSE_SELECTION_TIME)
                pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH//2 - 150, 250, 300 * progress, 30))

                if similarity >= POSE_SIMILARITY_THRESHOLD:
                    # 유지 시간이 충족되면 최종 확정
                    if elapsed_hold >= POSE_SELECTION_TIME:
                        # 최종 선택 블록 확정
                        game_logic.create_tetromino(selected_block_info)
                        fall_timer_start = time.time()
                        # selection 완료 후 playing으로 이동
                        game_state = STATE_PLAYING
                        # reset selection anchors
                        pose_timer_start = None
                        selected_block_info = None
                else:
                    # 포즈가 기준 미달이면 타이머 리셋(하지만 상태는 Selection에 머무름)
                    pose_timer_start = time.time()
                    selected_block_info = target_template

            else:
                # landmark가 사라지거나 인식이 안될 때: 안내 및 타이머 리셋(상태 유지)
                draw_text(screen, "Get into a zone and hold the pose!", 28, SCREEN_WIDTH//2, 220)
                pose_timer_start = None
                selected_block_info = None

        elif game_state == STATE_PLAYING:
            if game_logic.game_over:
                game_state = STATE_GAME_OVER
                continue


            # 블록 자동 하강
            if time.time() - fall_timer_start > INITIAL_FALL_INTERVAL:
                game_logic.move(0, 1)
                fall_timer_start = time.time()

            # "서 있는 위치" 기반으로 블록 조작 (라이브 조작은 Recognition/Selection과 다름)
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
                recognition_start = None
                recognition_counter = Counter()
            
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
