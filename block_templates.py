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
    # 1. I 모양 (일자 블록) - 양팔과 양다리를 쭉 뻗은 자세
    "I_shape": {
        'name': 'I Block',
        'shape': [[1, 1, 1, 1]],
        'vectors': {
            'right_arm': 180, 'left_arm': 180, 'right_leg': 180, 
            'left_leg': 180, 'right_body': 90, 'left_body': 270
        }
    },
    # 2. T 모양 - 양팔을 수평으로 들고 있는 자세
    "T_shape": {
        'name': 'T Block',
        'shape': [[0, 1, 0], [1, 1, 1]],
        'vectors': {
            'right_arm': 90, 'left_arm': 270, 'right_leg': 180, 
            'left_leg': 180, 'right_body': 180, 'left_body': 180
        }
    },
    # 3. L 모양 - 한 팔은 위로, 한 팔은 옆으로 뻗은 자세
    "L_shape": {
        'name': 'L Block',
        'shape': [[1, 0], [1, 0], [1, 1]],
        'vectors': {
            'right_arm': 180, 'left_arm': 270, 'right_leg': 180, 
            'left_leg': 180, 'right_body': 90, 'left_body': 180
        }
    },
    # 4. O 모양 (네모 블록) - 팔과 다리로 원을 만드는 듯한 자세
    "O_shape": {
        'name': 'O Block',
        'shape': [[1, 1], [1, 1]],
        'vectors': {
            'right_arm': 90, 'left_arm': 270, 'right_leg': 90,
            'left_leg': 270, 'right_body': 135, 'left_body': 225
        }
    },
    # 5. S 모양 - 한 팔은 위, 다른 팔은 아래로 향하는 자세
    "S_shape": {
        'name': 'S Block',
        'shape': [[0, 1, 1], [1, 1, 0]],
        'vectors': {
            'right_arm': 45, 'left_arm': 225, 'right_leg': 180,
            'left_leg': 180, 'right_body': 135, 'left_body': 225
        }
    },
    
    # 여기에 계속해서 다른 템플릿(J, Z 등)을 추가할 수 있습니다.
    # 각도 값은 실제 테스트를 통해 가장 인식률이 좋은 값으로 조정하는 것이 좋습니다.
}
