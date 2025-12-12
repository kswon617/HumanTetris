# -----------------------------------------------------------------------------
# settings.py
#
# 게임의 모든 상수를 저장하는 파일입니다.
# (화면 크기, 색상, 게임 속도 등)
# -----------------------------------------------------------------------------

# 화면 설정
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 30

# 게임 그리드(테트리스 판) 설정
GRID_ROWS = 20
GRID_COLS = 10
BLOCK_SIZE = 30
GRID_WIDTH = GRID_COLS * BLOCK_SIZE
GRID_HEIGHT = GRID_ROWS * BLOCK_SIZE
# 그리드를 화면 중앙에 위치시키기 위한 좌표
GRID_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
GRID_Y = (SCREEN_HEIGHT - GRID_HEIGHT) // 2

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

TETROMINO_COLORS = [CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]

# 게임 상태 정의
# 각 단계(모양 인식, 블록 선택 등)를 숫자로 구분하여 관리합니다.
STATE_RECOGNITION = 0  # 1. 모양 인식 단계
STATE_SELECTION = 1    # 2. 블록 선택 단계
STATE_COUNTDOWN = 2    # 3. 카운트다운
STATE_PLAYING = 3      # 4. 블록 조작 (게임 플레이)
STATE_GAME_OVER = 4    # 5. 게임 오버

# 포즈 인식 관련 설정
POSE_CONFIDENCE_THRESHOLD = 0.5  # MediaPipe가 포즈를 감지했다고 판단하는 최소 신뢰도
POSE_SIMILARITY_THRESHOLD = 0.7  # 사용자의 포즈가 템플릿과 얼마나 유사해야 하는지에 대한 임계값
POSE_SELECTION_TIME = 3          # 블록 선택을 위해 포즈를 유지해야 하는 시간 (초)

# 블록 떨어지는 속도 (숫자가 작을수록 빠름)
INITIAL_FALL_INTERVAL = 0.3  # 0.3초에 한 칸씩 떨어짐
