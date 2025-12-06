# -----------------------------------------------------------------------------
# block_templates.py
#
# 테트리스 블록 모양과 그에 해당하는 신체 포즈(각도 벡터)를 정의하는 파일.
# 사용자의 포즈와 여기에 정의된 템플릿을 비교하여 어떤 블록을 만들려는지 인식합니다.
# -----------------------------------------------------------------------------

# 각 포즈는 신체 부위별 목표 각도를 나타내는 딕셔너리입니다.
# 'right_arm', 'left_arm', 'right_leg', 'left_leg', 'right_body', 'left_body'
# 각도는 0~360도 사이의 값을 가집니다.

# 'shape'는 테트리스 블록의 모양을 2D 리스트로 표현합니다. 1은 블록, 0은 빈 공간.

POSE_TEMPLATES = {
    # ---------------------------------------------------
    # I BLOCK (2 rotations)
    # ---------------------------------------------------
    "I_0": {
        'name': 'I Block 0°',
        'shape': [[1, 1, 1, 1]],
        'vectors': {
            'right_arm': 180, 'left_arm': 180,
            'right_leg': 180, 'left_leg': 180,
            'right_body': 90, 'left_body': 270
        }
    },
    "I_90": {
        'name': 'I Block 90°',
        'shape': [[1], [1], [1], [1]],
        'vectors': {
            'right_arm': 90, 'left_arm': 270,
            'right_leg': 90, 'left_leg': 270,
            'right_body': 0, 'left_body': 180
        }
    },

    # ---------------------------------------------------
    # O BLOCK (1 rotation)
    # ---------------------------------------------------
    "O_0": {
        'name': 'O Block',
        'shape': [[1, 1], [1, 1]],
        'vectors': {
            'right_arm': 90, 'left_arm': 270,
            'right_leg': 90, 'left_leg': 270,
            'right_body': 135, 'left_body': 225
        }
    },

    # ---------------------------------------------------
    # T BLOCK (4 rotations)
    # ---------------------------------------------------
    "T_0": {
        'name': 'T Block 0°',
        'shape': [[0, 1, 0], [1, 1, 1]],
        'vectors': {
            'right_arm': 90, 'left_arm': 270,
            'right_leg': 180, 'left_leg': 180,
            'right_body': 180, 'left_body': 180
        }
    },
    "T_90": {
        'name': 'T Block 90°',
        'shape': [[1, 0], [1, 1], [1, 0]],
        'vectors': {
            'right_arm': 0, 'left_arm': 180,
            'right_leg': 90, 'left_leg': 270,
            'right_body': 180, 'left_body': 180
        }
    },
    "T_180": {
        'name': 'T Block 180°',
        'shape': [[1, 1, 1], [0, 1, 0]],
        'vectors': {
            'right_arm': 270, 'left_arm': 90,
            'right_leg': 180, 'left_leg': 180,
            'right_body': 180, 'left_body': 180
        }
    },
    "T_270": {
        'name': 'T Block 270°',
        'shape': [[0, 1], [1, 1], [0, 1]],
        'vectors': {
            'right_arm': 180, 'left_arm': 0,
            'right_leg': 90, 'left_leg': 270,
            'right_body': 0, 'left_body': 180
        }
    },

    # ---------------------------------------------------
    # L BLOCK (4 rotations)
    # ---------------------------------------------------
    "L_0": {
        'name': 'L Block 0°',
        'shape': [[1, 0], [1, 0], [1, 1]],
        'vectors': {
            'right_arm': 180, 'left_arm': 270,
            'right_leg': 180, 'left_leg': 180,
            'right_body': 90, 'left_body': 180
        }
    },
    "L_90": {
        'name': 'L Block 90°',
        'shape': [[1, 1, 1], [1, 0, 0]],
        'vectors': {
            'right_arm': 0, 'left_arm': 180,
            'right_leg': 90, 'left_leg': 270,
            'right_body': 180, 'left_body': 180
        }
    },
    "L_180": {
        'name': 'L Block 180°',
        'shape': [[1, 1], [0, 1], [0, 1]],
        'vectors': {
            'right_arm': 0, 'left_arm': 180,
            'right_leg': 180, 'left_leg': 180,
            'right_body': 270, 'left_body': 90
        }
    },
    "L_270": {
        'name': 'L Block 270°',
        'shape': [[0, 0, 1], [1, 1, 1]],
        'vectors': {
            'right_arm': 180, 'left_arm': 0,
            'right_leg': 90, 'left_leg': 270,
            'right_body': 180, 'left_body': 180
        }
    },

    # ---------------------------------------------------
    # J BLOCK (4 rotations)
    # ---------------------------------------------------
    "J_0": {
        'name': 'J Block 0°',
        'shape': [[0, 1], [0, 1], [1, 1]],
        'vectors': {
            'right_arm': 180, 'left_arm': 90,
            'right_leg': 180, 'left_leg': 180,
            'right_body': 270, 'left_body': 90
        }
    },
    "J_90": {
        'name': 'J Block 90°',
        'shape': [[1, 0, 0], [1, 1, 1]],
        'vectors': {
            'right_arm': 0, 'left_arm': 180,
            'right_leg': 90, 'left_leg': 270,
            'right_body': 180, 'left_body': 180
        }
    },
    "J_180": {
        'name': 'J Block 180°',
        'shape': [[1, 1], [1, 0], [1, 0]],
        'vectors': {
            'right_arm': 0, 'left_arm': 270,
            'right_leg': 180, 'left_leg': 180,
            'right_body': 180, 'left_body': 180
        }
    },
    "J_270": {
        'name': 'J Block 270°',
        'shape': [[1, 1, 1], [0, 0, 1]],
        'vectors': {
            'right_arm': 270, 'left_arm': 90,
            'right_leg': 90, 'left_leg': 270,
            'right_body': 180, 'left_body': 180
        }
    },

    # ---------------------------------------------------
    # S BLOCK (2 rotations)
    # ---------------------------------------------------
    "S_0": {
        'name': 'S Block 0°',
        'shape': [[0, 1, 1], [1, 1, 0]],
        'vectors': {
            'right_arm': 45, 'left_arm': 225,
            'right_leg': 180, 'left_leg': 180,
            'right_body': 135, 'left_body': 225
        }
    },
    "S_90": {
        'name': 'S Block 90°',
        'shape': [[1, 0], [1, 1], [0, 1]],
        'vectors': {
            'right_arm': 315, 'left_arm': 135,
            'right_leg': 90, 'left_leg': 270,
            'right_body': 180, 'left_body': 180
        }
    },

    # ---------------------------------------------------
    # Z BLOCK (2 rotations)
    # ---------------------------------------------------
    "Z_0": {
        'name': 'Z Block 0°',
        'shape': [[1, 1, 0], [0, 1, 1]],
        'vectors': {
            'right_arm': 315, 'left_arm': 135,
            'right_leg': 180, 'left_leg': 180,
            'right_body': 225, 'left_body': 135
        }
    },
    "Z_90": {
        'name': 'Z Block 90°',
        'shape': [[0, 1], [1, 1], [1, 0]],
        'vectors': {
            'right_arm': 45, 'left_arm': 225,
            'right_leg': 90, 'left_leg': 270,
            'right_body': 180, 'left_body': 180
        }
    }
}
