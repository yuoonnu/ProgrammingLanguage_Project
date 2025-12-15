import pygame
import sys
import random
from settings import *
from game_classes import *

# --- UI 그리기 함수들 ---
def draw_intro(screen, start_btn_rect):
    screen.fill(INTRO_BG)
    
    title = huge_font.render("종강까지 살아남기", True, BLACK)
    sub_title = title_font.render("알바비 입금까지 2주... 남은 돈으로 버텨라!", True, RED) 
    
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
    screen.blit(sub_title, (SCREEN_WIDTH//2 - sub_title.get_width()//2, 150))

    rule_box = pygame.Rect(200, 220, 700, 320)
    pygame.draw.rect(screen, WHITE, rule_box, border_radius=20)
    pygame.draw.rect(screen, BLACK, rule_box, 3, border_radius=20)

    rules = [
        f"1. 상황: 현재 전재산 {START_MONEY//10000}만원.",
        "2. 목표: 14일 동안 파산하지 않고 생존하기.",
        "3. 패배 조건: 잔고, 멘탈, 건강 중 하나라도 0이 되면 끝!",
        "",
        "4. 생존 팁:",
        "   - 일주일이 지난 시점(Day 8), 부모님의 연락이 올 수도...? (40%)",
        "   - 같은 메뉴는 5번 이상 먹으면 질려서 못 먹습니다.",
        f"   - 제한 시간({int(TIME_LIMIT)}초) 안에 밥을 못 먹으면 굶습니다."
    ]

    y_pos = 250
    for line in rules:
        text = main_font.render(line, True, BLACK)
        screen.blit(text, (230, y_pos))
        y_pos += 35

    pygame.draw.rect(screen, BLUE, start_btn_rect, border_radius=15)
    btn_text = title_font.render("생존 시작하기", True, WHITE)
    text_rect = btn_text.get_rect(center=start_btn_rect.center)
    screen.blit(btn_text, text_rect)

def draw_ui_playing(screen, player, day, remaining_time, log_messages, warning_msg):
    pygame.draw.rect(screen, GRAY, (0, 0, SCREEN_WIDTH, 100))
    money_color = BLACK if player.money > 20000 else RED
    
    screen.blit(title_font.render(f"Day {day}/{MAX_DAYS}", True, BLACK), (30, 25))
    screen.blit(main_font.render(f"잔고: {player.money}원", True, money_color), (220, 35))
    screen.blit(main_font.render(f"멘탈: {player.mental}", True, BLUE if player.mental>40 else RED), (400, 35))
    screen.blit(main_font.render(f"건강: {player.health}", True, GREEN if player.health>40 else RED), (550, 35))

    ratio = remaining_time / TIME_LIMIT
    timer_color = RED if ratio < 0.3 else GREEN
    pygame.draw.rect(screen, timer_color, (30, 80, 600 * ratio, 10))

    panel_rect = pygame.Rect(620, 110, 450, 450)
    pygame.draw.rect(screen, MSG_BOX_COLOR, panel_rect, border_radius=15)
    screen.blit(bold_font.render("--- 생존 일지 ---", True, BLACK), (panel_rect.x + 20, panel_rect.y + 20))
    
    y_log = panel_rect.y + 60
    for log in log_messages:
        color = BLUE if "용돈" in log else (80, 80, 80)
        screen.blit(small_font.render(log, True, color), (panel_rect.x + 20, y_log))
        y_log += 25
    
    if warning_msg:
        screen.blit(bold_font.render(f"⚠️ {warning_msg}", True, RED), (panel_rect.x + 20, panel_rect.bottom - 40))

def draw_tray(screen, tray, eat_btn_rect):
    tray_bg_rect = pygame.Rect(0, 580, SCREEN_WIDTH, 170)
    pygame.draw.rect(screen, LIGHT_PURPLE, tray_bg_rect)
    screen.blit(title_font.render("MY TRAY", True, BLACK), (30, 600))
    screen.blit(small_font.render("우클릭하면 비워집니다", True, BLACK), (220, 620))

    for i, food in enumerate(tray):
        r = pygame.Rect(60 + i*140, 650, 100, 80)
        pygame.draw.rect(screen, WHITE, r, border_radius=10)
        pygame.draw.rect(screen, food.color, r, 3, border_radius=10)
        screen.blit(bold_font.render(food.name, True, BLACK), (r.x+10, r.y+10))
        if food.image:
            small_img = pygame.transform.scale(food.image, (40, 40))
            screen.blit(small_img, (r.x + 25, r.y + 25))

    b_col = BLUE if len(tray) == 3 else (180, 180, 180)
    pygame.draw.rect(screen, b_col, eat_btn_rect, border_radius=20)
    btn_txt = title_font.render("식사하기", True, WHITE)
    text_rect = btn_txt.get_rect(center=eat_btn_rect.center)
    screen.blit(btn_txt, text_rect)

# --- 메인 게임 루프 ---
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("대학생 생존 시뮬레이터 Final")
    clock = pygame.time.Clock()
    
    player = Player()
    
    # 메뉴 리스트 데이터
    raw_foods = [
        (0, "유통기한빵", 500, -20, -20, "CARB", (220, 200, 180), ["멘탈 붕괴", "건강 붕괴"]),
        (1, "종합비타민", 800, -5, 10, "VEGE", (255, 255, 100), ["건강 회복", "멘탈 악화"]),
        (2, "맨밥", 1000, -5, 5, "CARB", (250, 250, 250), ["건강 회복", "멘탈 악화"]),
        (3, "계란후라이", 1000, 5, 5, "PROT", (255, 255, 200), ["멘탈 회복", "건강 회복"]),
        (4, "삼각김밥", 1200, 5, -5, "CARB", (200, 200, 200), ["멘탈 회복", "건강 악화"]),
        (5, "컵라면", 1500, 10, -15, "CARB", (255, 200, 150), ["멘탈 회복", "건강 악화"]),
        (6, "닭가슴살바", 2000, -5, 10, "PROT", (220, 150, 100), ["건강 회복", "멘탈 악화"]),
        (7, "마카롱", 3500, 30, -15, "SUGAR", (255, 200, 220), ["멘탈 초회복", "건강 악화"]),
        (8, "아아", 4500, 20, -5, "SUGAR", (120, 90, 70), ["멘탈 회복", "건강 악화"]),
        (9, "제육볶음", 7000, 20, 0, "PROT", (220, 80, 80), ["멘탈 회복", "건강 회복"]),
        (10,"닭가슴살샐러드", 9000, -15, 40, "VEGE", (150, 230, 150), ["건강 초회복", "멘탈 악화"]),
        (11,"스테이크", 15000, 50, 20, "PROT", (180, 60, 60), ["멘탈 초회복", "건강 초회복"]),
    ]
    
    food_list = []
    start_x, start_y = 50, 130
    col_width, row_height = 135, 140

    for i, data in enumerate(raw_foods):
        row = i // 4
        col = i % 4
        x = start_x + (col * col_width)
        y = start_y + (row * row_height)
        f = Food(*data)
        f.rect = pygame.Rect(x, y, 115, 120)
        food_list.append(f)

    tray = []
    day = 1
    start_ticks = 0
    
    log_messages = ["게임을 시작합니다.", "2주를 버텨내세요!", "----------------"]
    warning_msg = ""
    
    game_state = "INTRO"
    intro_btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 125, 600, 250, 80)
    eat_btn_rect = pygame.Rect(800, 600, 250, 100)
    retry_btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 125, 500, 250, 80)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_state == "INTRO":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if intro_btn_rect.collidepoint(event.pos):
                        game_state = "PLAYING"
                        start_ticks = pygame.time.get_ticks()

            elif game_state == "PLAYING":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    for food in food_list:
                        if food.rect.collidepoint(pos):
                            if player.get_food_count(food.name) >= MAX_EAT_COUNT:
                                warning_msg = "그만 먹어... 질렸어!"
                            else:
                                if len(tray) < 3:
                                    tray.append(food)
                                    warning_msg = f"{food.name} 담기 완료."
                                else:
                                    warning_msg = "식판이 꽉 찼습니다!"
                    
                    if event.button == 3: 
                        tray = []
                        warning_msg = "식판을 비웠습니다."

                    if eat_btn_rect.collidepoint(pos):
                        if len(tray) == 3:
                            msg, cost = player.eat(tray)
                            log_messages.append(f"[Day {day}] 식사 완료")
                            log_messages.append(f"- 비용: {cost}원")
                            log_messages.append(f"- 결과: {msg}")
                            
                            warning_msg = ""
                            tray = []
                            day += 1
                            
                            # --- [수정됨] Day 8 용돈 이벤트 (2만원) ---
                            if day == 8: 
                                if random.random() < 0.4: # 40% 확률
                                    bonus = 20000 # [수정] 50,000 -> 20,000
                                    player.money += bonus
                                    log_messages.append(f"★ 2주차 격려금! (+{bonus}원)")
                                else:
                                    log_messages.append("...부모님의 연락이 없다.")

                            if len(log_messages) > 10: log_messages = log_messages[-10:]
                            start_ticks = pygame.time.get_ticks()
                            
                            if not player.check_status():
                                game_state = "GAMEOVER"
                            elif day > MAX_DAYS:
                                game_state = "CLEAR"
                        else:
                            warning_msg = "3개를 채워야 합니다!"

            elif game_state == "GAMEOVER" or game_state == "CLEAR":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if retry_btn_rect.collidepoint(event.pos):
                        player = Player()
                        tray = []
                        day = 1
                        log_messages = ["게임을 다시 시작합니다!", "이번엔 꼭 성공하세요!", "----------------"]
                        warning_msg = ""
                        game_state = "PLAYING"
                        start_ticks = pygame.time.get_ticks()

        # 시간 체크
        if game_state == "PLAYING":
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - start_ticks) / 1000
            remaining_time = max(0, TIME_LIMIT - elapsed_time)

            if remaining_time <= 0:
                player.health -= 30
                player.mental -= 30
                log_messages.append(f"[Day {day}] 시간 초과!!")
                log_messages.append("건강/멘탈 대폭 붕괴")
                tray = []
                day += 1
                start_ticks = pygame.time.get_ticks()
                if not player.check_status():
                    game_state = "GAMEOVER"
                elif day > MAX_DAYS:
                    game_state = "CLEAR"
        else:
            remaining_time = 0

        screen.fill(WHITE)

        if game_state == "INTRO":
            draw_intro(screen, intro_btn_rect)

        elif game_state == "PLAYING":
            draw_ui_playing(screen, player, day, remaining_time, log_messages, warning_msg)
            for food in food_list:
                food.draw(screen, player.get_food_count(food.name))
            draw_tray(screen, tray, eat_btn_rect)

        elif game_state == "GAMEOVER":
            screen.fill(BLACK)
            t = title_font.render("GAME OVER", True, RED)
            r = title_font.render(f"사인: {player.cause_of_death}", True, WHITE)
            screen.blit(t, (SCREEN_WIDTH//2 - 100, 250))
            screen.blit(r, (SCREEN_WIDTH//2 - 150, 330))
            
            pygame.draw.rect(screen, BLUE, retry_btn_rect, border_radius=15)
            btn_txt = title_font.render("다시 도전하기", True, WHITE)
            text_rect = btn_txt.get_rect(center=retry_btn_rect.center)
            screen.blit(btn_txt, text_rect)

        elif game_state == "CLEAR":
            screen.fill((255, 255, 200)) 
            t = title_font.render("★ 졸업 축하합니다! ★", True, BLUE)
            r = title_font.render(f"남은 돈: {player.money}원", True, BLACK)
            screen.blit(t, (SCREEN_WIDTH//2 - 180, 250))
            screen.blit(r, (SCREEN_WIDTH//2 - 150, 330))

            pygame.draw.rect(screen, BLUE, retry_btn_rect, border_radius=15)
            btn_txt = title_font.render("다시 도전하기", True, WHITE)
            text_rect = btn_txt.get_rect(center=retry_btn_rect.center)
            screen.blit(btn_txt, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()