import pygame
import pygame_menu
import random
import sys
from typing import Tuple, Any
from math import isclose

pygame.init()

x = 600
y = 400

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

'''
Значения уровней сложности:
* Easy = 25
* Medium = 50
* Hard = 100
'''
difficulty = 25
screen = pygame.display.set_mode((x, y))
pygame.display.set_caption('Snake Game')
tic = pygame.time.Clock()
player_name = ''
default_player_name = True


# функция для изменения позиции еды на поле по клеточкам размера 10 пикселей
def new_food_pose():
    pos = [random.randrange(1, (x // 10)) * 10,
           random.randrange(1, (y // 10)) * 10]
    return pos


# функция изменения позиции объекта с полигонами
def new_obj_pos():
    pos = [random.randrange(1, (x // 10)) * 10,
           random.randrange(1, (y // 10)) * 10]
    return pos


# функция изменения сложности игры
def set_game_diff(selected: Tuple, value: Any):
    if value == 1:
        difficulty = 25
    elif value == 2:
        difficulty = 50
    elif value == 3:
        difficulty = 100
    else:
        difficulty = 25


# функция для отображения счёта игры
def show_score(font, size, game_score):
    game_score_font = pygame.font.SysFont(font, size)
    game_score_surface = game_score_font.render("Счёт игры: " + str(game_score), True, white)
    game_score_rect = game_score_surface.get_rect()
    game_score_rect.midtop = (y / 5, 15)
    screen.blit(game_score_surface, game_score_rect)


# функция отображения объекта в игре
def show_obj(pos_obj, s_width, s_height):
    obj_rect = pygame.Rect(pos_obj[0], pos_obj[1], s_width, s_height)
    obj_image = pygame.image.load("./red-brick-wall.jpg")
    obj_image_resize = pygame.transform.scale(obj_image, (s_width, s_height))
    screen.blit(obj_image_resize, obj_rect)


# функция открытия стартового меню
def show_start_screen():
    start_menu = pygame_menu.Menu(width=x, height=y, title='Хорошей игры!',
                                  theme=pygame_menu.themes.THEME_BLUE)
    start_menu.add.text_input("Ваше имя: ", default='Гость')
    start_menu.add.selector("Сложность: ",
                            [("Просто", 1), ("Нормально", 2), ("Сложно", 3)],
                            onchange=set_game_diff)
    start_menu.add.button("Играть", game_loop)
    start_menu.add.button("Выйти", pygame_menu.events.EXIT)
    start_menu.mainloop(screen)


# функция запуска игры
def replay_game():
    game_loop()


# функция отображения экрана проигрыша
def show_end_screen(game_score):
    end_menu = pygame_menu.Menu(width=x, height=y,
                                title='Игра окончена',
                                theme=pygame_menu.themes.THEME_BLUE)
    end_menu.add.label("Вас счёт:" + str(game_score))
    end_menu.add.button("Играть заново", replay_game)
    end_menu.add.button("Выйти", pygame_menu.events.EXIT)
    end_menu.mainloop(screen)


# функция установки имени пользователя
def set_player_name(name):
    global player_name
    global default_player_name
    player_name = name
    default_player_name = False


# функция установки начального имени игрока
def set_def_p_name():
    global player_name
    global default_player_name
    player_name = "Гость"
    default_player_name = False


def game_loop():
    x1 = x/2
    y1 = y/2
    snake_position = [x1, y1]
    snake_body = [[x1, y1], [x1-10, y1], [x1-(2*10), x1]]
    snake_width = 20
    snake_height = 20
    snake_speed = 5
    snake_direction = "UP"
    new_direction = snake_direction
    gameExit = False
    game_score = 0

    food_position = new_food_pose()
    show_food = True

    collision_obj_position = new_obj_pos()
    show_collision = True

    while not gameExit:
        pygame.time.delay(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()
        if keys[pygame.K_LEFT]:
            new_direction = "LEFT"
        if keys[pygame.K_RIGHT]:
            new_direction = "RIGHT"
        if keys[pygame.K_UP]:
            new_direction = "UP"

        if keys[pygame.K_DOWN]:
            new_direction = "DOWN"
        if snake_direction != "UP" and new_direction == "DOWN":
            snake_direction = new_direction
        if snake_direction != "DOWN" and new_direction == "UP":
            snake_direction = new_direction
        if snake_direction != "LEFT" and new_direction == "RIGHT":
            snake_direction = new_direction
        if snake_direction != "RIGHT" and new_direction == "LEFT":
            snake_direction = new_direction

        if snake_direction == "UP":
            snake_position[1] -= snake_speed
        if snake_direction == "DOWN":
            snake_position[1] += snake_speed
        if snake_direction == "LEFT":
            snake_position[0] -= snake_speed
        if snake_direction == "RIGHT":
            snake_position[0] += snake_speed

        snake_body.insert(0, list(snake_position))
        if isclose(snake_position[0], food_position[0], abs_tol=5) and isclose(snake_position[1], food_position[1], abs_tol=5):
            game_score += 10
            show_food = False
        else:
            snake_body.pop()

        if isclose(snake_position[0], collision_obj_position[0], abs_tol=(snake_width - 10)) and isclose(snake_position[1], collision_obj_position[1], abs_tol=(snake_height - 10)):
            show_end_screen(game_score)

        if not show_food:
            food_position = new_food_pose()
            show_food = True
        if not show_collision:
            collision_obj_position = new_obj_pos()

            show_collision = True

        screen.fill(black)
        for pos in snake_body:
            # Изображение змейки
            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(pos[0], pos[1], snake_width/2, snake_height/2))

        # Изображение еды
        pygame.draw.rect(screen, (255, 0, 255), (food_position[0], food_position[1], snake_width/2, snake_height/2))

        show_obj(collision_obj_position, snake_width, snake_height)

        # Если змейка врезается в стену игра заканчивается
        if snake_position[0] < 0 or snake_position[0] > (x - snake_width/2):
            show_end_screen(game_score)
        if snake_position[1] < 0 or snake_position[1] > (y - snake_height/2):
            show_end_screen(game_score)
        show_score('consolas', 20, game_score)
        pygame.display.update()

        tic.tick(difficulty)


show_start_screen()
