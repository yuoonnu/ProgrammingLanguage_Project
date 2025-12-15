import pygame
import os
import sys

# --- 초기화 및 경로 설정 ---
pygame.init()

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 750
FPS = 30

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 60, 60)
BLUE = (60, 100, 255)
GREEN = (50, 180, 50)
GRAY = (240, 240, 240)
DARK_GRAY = (100, 100, 100)
LIGHT_PURPLE = (230, 220, 255)
MSG_BOX_COLOR = (245, 245, 250)
INTRO_BG = (255, 250, 240)

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# --- [핵심 수정] 폰트 설정 ---
# 1순위: assets 폴더에 'Jua.ttf'가 있으면 사용
# 2순위: 없으면 윈도우 '맑은 고딕' 사용 (한글 깨짐 방지)
# 3순위: 맥(Mac)이면 'AppleGothic' 사용

font_path = os.path.join(ASSETS_DIR, "Jua.ttf")

def get_font(size):
    try:
        # 1. assets 폴더의 폰트 시도
        return pygame.font.Font(font_path, size)
    except:
        # 2. 실패 시 시스템 한글 폰트 시도
        if sys.platform == 'win32': # 윈도우
            try:
                return pygame.font.Font("C:/Windows/Fonts/malgun.ttf", size)
            except:
                return pygame.font.SysFont("malgungothic", size)
        elif sys.platform == 'darwin': # 맥
            return pygame.font.SysFont("AppleGothic", size)
        else:
            return pygame.font.SysFont("arial", size) # 최후의 수단 (한글 깨질 수 있음)

# 폰트 객체 생성
main_font = get_font(18)
small_font = get_font(13) 
bold_font = get_font(16)
title_font = get_font(35)
huge_font = get_font(45)

# 게임 밸런스 설정
MAX_DAYS = 14
TIME_LIMIT = 5.0      
MAX_EAT_COUNT = 5
START_MONEY = 100000