import pygame
import os
from settings import * # settings.py의 모든 변수를 가져옴

class Player:
    def __init__(self):
        self.money = START_MONEY    
        self.mental = 70      
        self.health = 70
        self.is_alive = True
        self.cause_of_death = ""
        self.food_history = {}

    def get_food_count(self, food_name):
        return self.food_history.get(food_name, 0)

    def eat(self, tray):
        total_cost = sum(f.cost for f in tray)
        total_mental = sum(f.mental for f in tray)
        total_health = sum(f.health for f in tray)
        
        for f in tray:
            self.food_history[f.name] = self.food_history.get(f.name, 0) + 1

        types = [f.nutrition_type for f in tray]
        balance_msg = "영양 밸런스 적절함."
        
        if len(set(types)) == 1: 
            total_health -= 50
            total_mental -= 30
            balance_msg = "영양 붕괴!! (한 종류만 섭취)"
        elif "PROT" not in types:
            total_health -= 20
            balance_msg = "단백질 부족 (건강 악화)"
        elif types.count("SUGAR") >= 2:
            total_health -= 40
            total_mental += 20
            balance_msg = "당류 과다 (혈당 쇼크)"

        self.money -= total_cost
        self.mental += total_mental
        self.health += total_health

        self.mental = min(100, self.mental)
        self.health = min(100, self.health)

        return balance_msg, total_cost

    def check_status(self):
        if self.money < 0:
            self.cause_of_death = "파산 (잔고 부족)"
            return False
        if self.mental <= 0:
            self.cause_of_death = "멘탈 붕괴"
            return False
        if self.health <= 0:
            self.cause_of_death = "건강 악화 (입원)"
            return False
        return True

class Food:
    def __init__(self, index, name, cost, mental, health, n_type, color, keywords):
        self.index = index
        self.name = name
        self.cost = cost
        self.mental = mental
        self.health = health
        self.nutrition_type = n_type
        self.color = color
        self.keywords = keywords 
        self.rect = None 
        self.image = self.load_image()

    def load_image(self):
        img_path = os.path.join(ASSETS_DIR, f"food_{self.index}.png")
        try:
            # 1. 원본 이미지 불러오기
            raw_image = pygame.image.load(img_path).convert_alpha()

            # 2. 여백 자동 제거 (Crop)
            content_rect = raw_image.get_bounding_rect()
            cropped_image = raw_image.subsurface(content_rect)

            # 3. [수정됨] 크기를 40x40으로 더 작게 줄임! (아주 귀여운 사이즈)
            scaled_image = pygame.transform.scale(cropped_image, (40, 40))
            
            return scaled_image
        except Exception as e:
            print(f"이미지 로드 실패 ({img_path}): {e}")
            return None

    def draw(self, screen, count):
        is_soldout = count >= MAX_EAT_COUNT
        
        border_color = DARK_GRAY if is_soldout else BLACK
        text_color = DARK_GRAY if is_soldout else BLACK
        bg_color = (230, 230, 230) if is_soldout else WHITE

        pygame.draw.rect(screen, bg_color, self.rect, border_radius=12)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=12)
        
        # [수정됨] 이미지 그리기 위치 조정
        if self.image:
            if is_soldout:
                self.image.set_alpha(100) 
            else:
                self.image.set_alpha(255)
            
            # 작아진 만큼 오른쪽 구석으로 더 밀착시켰습니다.
            # (rect.right - 30 위치)
            img_rect = self.image.get_rect(center=(self.rect.right - 30, self.rect.centery))
            screen.blit(self.image, img_rect)

        # 텍스트 그리기
        name_surf = bold_font.render(self.name, True, text_color)
        screen.blit(name_surf, (self.rect.x + 10, self.rect.y + 10))
        
        cost_surf = small_font.render(f"-{self.cost}원", True, (80,80,80) if not is_soldout else DARK_GRAY)
        screen.blit(cost_surf, (self.rect.x + 10, self.rect.y + 32))
        
        y_offset = 60
        if not is_soldout:
            for key in self.keywords:
                k_color = BLACK
                if "붕괴" in key or "악화" in key: k_color = RED
                elif "초회복" in key or "회복" in key: k_color = BLUE
                
                key_surf = small_font.render(key, True, k_color)
                screen.blit(key_surf, (self.rect.x + 10, self.rect.y + y_offset))
                y_offset += 16
        else:
            sold_surf = bold_font.render("품절 (질림)", True, RED)
            screen.blit(sold_surf, (self.rect.x + 15, self.rect.y + 70))
        
        count_text = f"{count}/{MAX_EAT_COUNT}"
        screen.blit(small_font.render(count_text, True, text_color), (self.rect.right - 40, self.rect.bottom - 15))