# Human Tetris (인간 테트리스)

**Human Tetris**는 웹캠을 통해 사용자의 **신체 포즈를 인식하여 플레이하는 인터랙티브 테트리스 게임**입니다.
키보드 대신 **몸동작**으로 테트리스 블록(테트로미노)의 모양을 만들고, 위치를 조작하여 게임을 즐겨보세요!

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose%20Estimation-orange.svg)
![Pygame](https://img.shields.io/badge/Pygame-Game%20Engine-red.svg)

## 주요 기능 (Key Features)

* **실시간 포즈 인식**: Google MediaPipe를 활용하여 신체 관절을 실시간으로 추적하고 분석합니다.
* **포즈 매칭 알고리즘**: 코사인 유사도(Cosine Similarity)를 이용해 사용자의 포즈와 미리 정의된 블록 템플릿(I, O, T, L, J, S, Z)을 비교합니다.
* **인터랙티브 게임 플레이**:
    * **Recognition**: 원하는 블록 모양을 몸으로 표현하여 후보를 생성합니다.
    * **Selection**: 화면 상단의 구역(Zone)으로 몸을 움직여 블록을 선택합니다.
    * **Playing**: 몸의 위치(왼쪽/오른쪽)를 통해 떨어지는 블록을 조작합니다.
* **직관적인 UI**: 내 모습이 비치는 거울 모드 화면과 실시간 점수, 가이드 UI를 제공합니다.

## 설치 방법 (Installation)

이 프로젝트는 Python 3.12 환경에서 실행됩니다.

1.  **저장소 클론 (또는 다운로드)**
    ```bash
    git clone [https://github.com/your-username/human-tetris.git](https://github.com/your-username/human-tetris.git)
    cd human-tetris
    #가상화면 만드는거 추천! 알아서 하기!
    ```

2.  **필수 라이브러리 설치**
    `requirements.txt`에 명시된 패키지들을 설치합니다. 
    ```bash
    pip install -r requirements.txt
    ```
    *(주요 의존성: `opencv-python`, `mediapipe`, `pygame`, `numpy`)*

## 실행 방법 (How to Run)

터미널에서 `main.py`를 실행하면 게임이 시작됩니다.

```bash
python main.py

