# -----------------------------------------------------------------------------
# block_templates.py (human-friendly pose version)
#
# 사람의 실제 포즈를 기준으로 제작된 템플릿.
# 각 신체 파트는 MediaPipe 벡터 방향(0~360도)을 기준으로 비교된다.
#
# 방향 규칙:
#   0°   = 화면 오른쪽
#   90°  = 화면 위
#   180° = 화면 왼쪽
#   270° = 화면 아래
# -----------------------------------------------------------------------------

POSE_TEMPLATES = {

    # ============================================================
    # I BLOCK (만세 자세)
    # ============================================================

    # I_0 : 서서 만세(세로)
    "I_0": {
        'name': 'I Block 0°',
        'shape': [[1], [1], [1], [1]],
        'vectors': {
            'right_arm': 90, 'left_arm': 90,        # 만세
            'right_leg': 270, 'left_leg': 270,      # 아래
            'right_body': 90, 'left_body': 90       # 몸 위쪽
        }
    },

    # I_90 : 누워서 만세(가로)
    "I_90": {
        'name': 'I Block 90°',
        'shape': [[1, 1, 1, 1]],
        'vectors': {
            'right_arm': 180, 'left_arm': 180,
            'right_leg': 0, 'left_leg': 0,
            'right_body': 180, 'left_body': 180      
        }
    },
    


    # ============================================================
    # O BLOCK (OTZ 자세)
    # ============================================================

    "O_0": {
        'name': 'O Block',
        'shape': [[1, 1], [1, 1]],
        'vectors': {
            'right_arm': 270, 'left_arm': 270,     
            'right_leg': 180, 'left_leg': 180,      
            'right_body': 0, 'left_body': 0       
        }
    },

    # ============================================================
    # T BLOCK (ㅗㅏㅓㅜ)
    # ============================================================

    # ㅗ : 다리 좌우 + 만세
    "T_180": {
        'name': 'T Block 180°',
        'shape': [[0, 1, 0], [1, 1, 1]],
        'vectors': {
            'right_arm': 90, 'left_arm': 90,        # 만세
            'right_leg': 0, 'left_leg': 180,        # 다리 좌우 벌림
            'right_body': 90, 'left_body': 90
        }
    },

    # ㅏ : 오른팔 옆 + 왼팔 만세
    "T_270": {
        'name': 'T Block 270°',
        'shape': [[1, 0], [1, 1], [1, 0]],
        'vectors': {
            'right_arm': 0, 'left_arm': 90,         # 오른팔 옆, 왼팔 위
            'right_leg': 270, 'left_leg': 270,
            'right_body': 90, 'left_body': 90
        }
    },

    # ㅜ : 양팔 좌우
    "T_0": {
        'name': 'T Block 0°',
        'shape': [[1, 1, 1], [0, 1, 0]],
        'vectors': {
            'right_arm': 0, 'left_arm': 180,        # 좌우
            'right_leg': 270, 'left_leg': 270,
            'right_body': 90, 'left_body': 90
        }
    },

    # ㅓ : 왼팔 옆 + 오른팔 만세
    "T_90": {
        'name': 'T Block 90°',
        'shape': [[0, 1], [1, 1], [0, 1]],
        'vectors': {
            'right_arm': 90, 'left_arm': 180,       # 오른팔 위, 왼팔 옆
            'right_leg': 270, 'left_leg': 270,
            'right_body': 90, 'left_body': 90
        }
    },

    # ============================================================
    # L BLOCK (몸 기울기 + 만세, 다리는 항상 아래)
    # ============================================================

    "L_0": {
        'name': 'L Block 0°',
        'shape': [[1, 0], [1, 0], [1, 1]],
        'vectors': {
            'right_arm': 90, 'left_arm': 90,
            'right_leg': 0, 'left_leg': 0,
            'right_body': 90, 'left_body': 90        
        }
    },

    "L_90": {
        'name': 'L Block 90°',
        'shape': [[1, 1, 1], [1, 0, 0]],
        'vectors': {
            'right_arm': 0, 'left_arm': 0,
            'right_leg': 270, 'left_leg': 270,
            'right_body': 0, 'left_body': 0     
        }
    },

    "L_180": {
        'name': 'L Block 180°',
        'shape': [[1, 1], [0, 1], [0, 1]],
        'vectors': {
            'right_arm': 180, 'left_arm': 180,
            'right_leg': 270, 'left_leg': 270,
            'right_body': 90, 'left_body': 90    
        }
    },

    "L_270": {
        'name': 'L Block 270°',
        'shape': [[0, 0, 1], [1, 1, 1]],
        'vectors': {
            'right_arm': 90, 'left_arm': 90,
            'right_leg': 180, 'left_leg': 180,
            'right_body': 0, 'left_body': 0      
        }
    },

    # ============================================================
    # J BLOCK (L의 좌우 반전)
    # ============================================================

    "J_0": {
        'name': 'J Block 0°',
        'shape': [[0, 1], [0, 1], [1, 1]],
        'vectors': {
            'right_arm': 90, 'left_arm': 90,
            'right_leg': 180, 'left_leg': 180,
            'right_body': 90, 'left_body': 90    
        }
    },

    "J_90": {
        'name': 'J Block 90°',
        'shape': [[1, 1, 1], [0, 0, 1]],
        'vectors': {
            'right_arm': 180, 'left_arm': 180,
            'right_leg': 270, 'left_leg': 270,
            'right_body': 180, 'left_body': 180     
        }
    },

    "J_180": {
        'name': 'J Block 180°',
        'shape': [[1, 1], [1, 0], [1, 0]],
        'vectors': {
            'right_arm': 0, 'left_arm': 0,
            'right_leg': 270, 'left_leg': 270,
            'right_body': 90, 'left_body': 90      
        }
    },

    "J_270": {
        'name': 'J Block 270°',
        'shape': [[1, 0, 0], [1, 1, 1]],
        'vectors': {
            'right_arm': 90, 'left_arm': 90,
            'right_leg': 0, 'left_leg': 0,
            'right_body': 180, 'left_body': 180  
        }
    },

    # ============================================================
    # S BLOCK 
    # ============================================================

    # S_0
    "S_0": {
        'name': 'S Block 0°',
        'shape': [[0, 1, 1], [1, 1, 0]],
        'vectors': {
            'right_arm': 0, 'left_arm': 0,          
            'right_leg': 180, 'left_leg': 180,     
            'right_body': 0, 'left_body': 0         
        }
    },

    # S_90 : 상체→위, 다리→왼쪽, 팔→위
    "S_90": {
        'name': 'S Block 90°',
        'shape': [[1, 0], [1, 1], [0, 1]],
        'vectors': {
            'right_arm': 90, 'left_arm': 90,        # 팔 위
            'right_leg': 180, 'left_leg': 180,      # 다리 왼쪽
            'right_body': 90, 'left_body': 90
        }
    },

    # ============================================================
    # Z BLOCK (S의 좌우 반전)
    # ============================================================

    # Z_0 : 상체→왼쪽, 다리→아래, 팔→왼쪽
    "Z_0": {
        'name': 'Z Block 0°',
        'shape': [[1, 1, 0], [0, 1, 1]],
        'vectors': {
            'right_arm': 180, 'left_arm': 180,      # 팔 왼쪽
            'right_leg': 0, 'left_leg': 0,      # 다리 아래
            'right_body': 180, 'left_body': 180     # 상체 왼쪽
        }
    },

    # Z_90 : 상체→위, 다리→오른쪽, 팔→위
    "Z_90": {
        'name': 'Z Block 90°',
        'shape': [[0, 1], [1, 1], [1, 0]],
        'vectors': {
            'right_arm': 90, 'left_arm': 90,        # 팔 위
            'right_leg': 270, 'left_leg': 270,          # 다리 오른쪽
            'right_body': 90, 'left_body': 90
        }
    }
}
