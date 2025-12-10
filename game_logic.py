# -----------------------------------------------------------------------------
# game_logic.py
#
# 테트리스 게임의 핵심 로직을 담당하는 클래스.
# (그리드 관리, 블록 생성/이동/회전, 충돌 감지, 줄 제거 등)
# -----------------------------------------------------------------------------

import pygame
from settings import *
import random

class Tetromino:
    """
    테트리스 블록(테트로미노) 하나를 나타내는 클래스.
    """
    def __init__(self, x, y, shape_info):
        self.x = x
        self.y = y
        self.shape = shape_info['shape']
        self.name = shape_info['name']
        # 블록마다 랜덤 색상을 지정
        self.color = random.choice(TETROMINO_COLORS)

    def rotate(self):
        """블록을 시계 방향으로 90도 회전시킵니다."""
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

class GameLogic:
    """
    테트리스 게임의 전반적인 로직을 관리하는 클래스.
    """
    def __init__(self):
        # 게임 그리드를 0으로 초기화 (0은 빈 공간)
        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.current_tetromino = None
        self.score = 0
        self.game_over = False

    def create_tetromino(self, shape_info):
        """
        새로운 테트로미노를 생성하여 게임에 추가합니다.
        """
        # 블록을 그리드 중앙 상단에 위치시킴
        start_x = GRID_COLS // 2 - len(shape_info['shape'][0]) // 2
        start_y = 0
        self.current_tetromino = Tetromino(start_x, start_y, shape_info)
        
        # 블록을 생성하자마자 다른 블록과 겹치면 게임 오버
        if self._check_collision(self.current_tetromino):
            self.game_over = True

    def move(self, dx, dy):
        """현재 블록을 dx, dy만큼 이동시킵니다."""
        if self.current_tetromino and not self.game_over:
            # 이동 전 위치 저장
            original_x, original_y = self.current_tetromino.x, self.current_tetromino.y
            
            self.current_tetromino.x += dx
            self.current_tetromino.y += dy
            
            # 이동 후 충돌이 발생하면 원위치
            if self._check_collision(self.current_tetromino):
                self.current_tetromino.x, self.current_tetromino.y = original_x, original_y
                # 아래로 이동하다 충돌한 경우, 블록을 그리드에 고정
                if dy > 0:
                    self._lock_tetromino()
                return False
            return True
        return False

#rotate 복잡해져서 빼고 모든 블록 탬플릿 추가함여
    def rotate(self):
        """현재 블록을 회전시킵니다."""
        if self.current_tetromino and not self.game_over:
            # 회전 전 모양 저장
            original_shape = self.current_tetromino.shape
            self.current_tetromino.rotate()
            
            # 회전 후 충돌이 발생하면 원상복구
            if self._check_collision(self.current_tetromino):
                self.current_tetromino.shape = original_shape

    def hard_drop(self):
        """블록을 한 번에 가장 아래로 내립니다 (Hard Drop)."""
        if self.current_tetromino and not self.game_over:
            # 충돌이 발생할 때까지 계속 아래로 이동
            while not self._check_collision(self.current_tetromino):
                self.current_tetromino.y += 1
            # 충돌 직전 위치로 되돌린 후 고정
            self.current_tetromino.y -= 1
            self._lock_tetromino()

    def _check_collision(self, tetromino):
        """
        주어진 테트로미노가 그리드 경계나 다른 블록과 충돌하는지 확인합니다.
        """
        for y, row in enumerate(tetromino.shape):
            for x, cell in enumerate(row):
                if cell: # 블록의 실제 부분이 있는 칸만 검사
                    grid_x = tetromino.x + x
                    grid_y = tetromino.y + y
                    
                    # 1. 그리드 경계를 벗어나는지 확인
                    if not (0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS):
                        return True
                    # 2. 다른 블록과 겹치는지 확인
                    if self.grid[grid_y][grid_x] != 0:
                        return True
        return False

    def _lock_tetromino(self):
        """
        현재 테트로미노를 그리드에 고정시키고, 다음 블록을 준비합니다.
        """
        if self.current_tetromino:
            for y, row in enumerate(self.current_tetromino.shape):
                for x, cell in enumerate(row):
                    if cell:
                        grid_x = self.current_tetromino.x + x
                        grid_y = self.current_tetromino.y + y
                        # 그리드에 블록의 색상 정보를 기록
                        if 0 <= grid_y < GRID_ROWS:
                            self.grid[grid_y][grid_x] = self.current_tetromino.color
            
            self._clear_lines()
            self.current_tetromino = None # 현재 블록 없음 상태로 변경

    def _clear_lines(self):
        """꽉 찬 줄이 있는지 확인하고 제거합니다."""
        lines_cleared = 0
        # 꽉 차지 않은 줄만 새로운 그리드에 추가
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        lines_cleared = GRID_ROWS - len(new_grid)
        
        if lines_cleared > 0:
            # 점수 계산 (지운 줄 수에 따라 보너스)
            self.score += (lines_cleared ** 2) * 100
            # 지운 줄 수만큼 맨 위에 새로운 빈 줄을 추가
            for _ in range(lines_cleared):
                new_grid.insert(0, [0 for _ in range(GRID_COLS)])
            self.grid = new_grid

    def draw_grid(self, screen):
        """고정된 블록들만 화면에 그립니다."""
        for y, row in enumerate(self.grid):
            for x, cell_color in enumerate(row):
                if cell_color != 0:
                    pygame.draw.rect(
                        screen, cell_color,
                        (GRID_X + x * BLOCK_SIZE, GRID_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0
                    )
                    # 블록 테두리
                    pygame.draw.rect(
                        screen, GRAY,
                        (GRID_X + x * BLOCK_SIZE, GRID_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1
                    )
        

    def draw_current_tetromino(self, screen):
        """현재 움직이는 블록만 화면에 그립니다."""
        if self.current_tetromino:
            for y, row in enumerate(self.current_tetromino.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(
                            screen, self.current_tetromino.color,
                            (GRID_X + (self.current_tetromino.x + x) * BLOCK_SIZE,
                             GRID_Y + (self.current_tetromino.y + y) * BLOCK_SIZE,
                             BLOCK_SIZE, BLOCK_SIZE), 0
                        )
                        pygame.draw.rect(
                            screen, GRAY,
                            (GRID_X + (self.current_tetromino.x + x) * BLOCK_SIZE,
                             GRID_Y + (self.current_tetromino.y + y) * BLOCK_SIZE,
                             BLOCK_SIZE, BLOCK_SIZE), 1
                        )
