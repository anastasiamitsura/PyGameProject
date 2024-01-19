import pygame
import pygame_menu
import random
import sys
from typing import Tuple, Any
from math import isclose
import sqlite3 as sl

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
MAIN_THEME = pygame_menu.themes.THEME_BLUE


class DataBase:
    con = sl.connect('records.db')

    with con:
        data = con.execute("select count(*) from sqlite_master \
        where type='table' and name='records'")
        for row in data:
            if row[0] == 0:
                con.execute("""
                            CREATE TABLE records (
                                name STRING,
                                score INTEGER
                            );
                        """)
    sqlite_insert_score = """ INSERT INTO records
                                             (name, score) VALUES (?, ?)"""


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
                                      theme=MAIN_THEME)
    start_menu.add.text_input("Ваше имя: ", default='Гость', onchange=set_player_name)
    start_menu.add.selector("Сложность: ",
                                [("Просто", 1), ("Нормально", 2), ("Сложно", 3)],
                                onchange=set_game_diff)
    start_menu.add.button("Играть", cat_start)
    start_menu.add.button("Рейтинг", show_records_screen)
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
    end_menu.add.button("Играть заново", show_start_screen)
    end_menu.add.button("Выйти", pygame_menu.events.EXIT)
    data = (str(player_name), game_score)
    DataBase.con.execute(DataBase.sqlite_insert_score, data)
    with DataBase.con:
        data = DataBase.con.execute("SELECT * FROM records")
        for row in data:
            print(row)
    end_menu.mainloop(screen)


# функция окна рекордов
def show_records_screen():
    records = []
    with DataBase.con:
        data = DataBase.con.execute("SELECT * FROM records")
        for i in data:
            records.append(i)

    # сортировка пузырьком всех результатов из бд для составления рейтинга
    for i in range(len(records) - 1):
        for j in range(len(records) - 2, i - 1, -1):
            if records[j + 1][1] > records[j][1]:
                records[j + 1], records[j] = records[j], records[j + 1]

    records_menu = pygame_menu.Menu(width=x, height=y,
                                    title='Таблица рекордов',
                                    theme=pygame_menu.themes.THEME_ORANGE)
    records_menu.add.table("table")

    # заполнение таблицы рекордами
    for i in records:
        records_menu.get_widgets()[0].add_row(i)
    records_menu.add.button("Главное меню", show_start_screen)
    records_menu.mainloop(screen)


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


# функция самой игры
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
        if keys[pygame.K_a]:
            new_direction = "LEFT"
        if keys[pygame.K_d]:
            new_direction = "RIGHT"
        if keys[pygame.K_w]:
            new_direction = "UP"
        if keys[pygame.K_s]:
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
            cat_finish(game_score)

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
            cat_finish(game_score)
        if snake_position[1] < 0 or snake_position[1] > (y - snake_height/2):
            cat_finish(game_score)
        show_score('consolas', 20, game_score)
        pygame.display.update()

        tic.tick(difficulty)


# класс для анимации кота после старта
class MyСat_Start(pygame.sprite.Sprite):
    def __init__(self):
        super(MyСat_Start, self).__init__()

        self.images = []
        self.images.append(pygame.image.load('0.png'))
        self.images.append(pygame.image.load('1.png'))

        self.index = 0

        self.image = self.images[self.index]

        self.rect = pygame.Rect(5, 5, 150, 198)

    def update(self):
        self.index += 1

        if self.index >= len(self.images):
            self.index = 0

        self.image = self.images[self.index]


# функция для запуска анимации на старте
def cat_start():
    screen = pygame.display.set_mode((250, 250))
    time = 0
    my_sprite = MyСat_Start()
    my_group = pygame.sprite.Group(my_sprite)

    while True:
        if time == 20:
            screen = pygame.display.set_mode((600, 400))
            game_loop()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        my_group.update()
        screen.fill(pygame.Color('white'))
        my_group.draw(screen)
        pygame.display.update()
        tic.tick(10)
        time += 1


# класс для анимации кота после плохого результата в игре
class MyСat_Bad(pygame.sprite.Sprite):
    def __init__(self):
        super(MyСat_Bad, self).__init__()

        self.images = []
        self.images.append(pygame.image.load('2.png'))
        self.images.append(pygame.image.load('3.png'))
        self.images.append(pygame.image.load('4.png'))
        self.images.append(pygame.image.load('5.png'))
        self.images.append(pygame.image.load('6.png'))
        self.images.append(pygame.image.load('7.png'))
        self.images.append(pygame.image.load('8.png'))
        self.images.append(pygame.image.load('9.png'))
        self.images.append(pygame.image.load('10.png'))
        self.images.append(pygame.image.load('11.png'))
        self.images.append(pygame.image.load('12.png'))
        self.images.append(pygame.image.load('13.png'))
        self.images.append(pygame.image.load('14.png'))
        self.images.append(pygame.image.load('15.png'))
        self.images.append(pygame.image.load('16.png'))
        self.images.append(pygame.image.load('17.png'))
        self.images.append(pygame.image.load('18.png'))
        self.images.append(pygame.image.load('19.png'))

        self.index = 0

        self.image = self.images[self.index]

        self.rect = pygame.Rect(5, 5, 150, 198)

    def update(self):
        self.index += 1

        if self.index >= len(self.images):
            self.index = 0

        self.image = self.images[self.index]


# класс для анимации кота после среднего результата в игре
class MyСat_Midl(pygame.sprite.Sprite):
    def __init__(self):
        super(MyСat_Midl, self).__init__()

        self.images = []
        self.images.append(pygame.image.load('20.png'))
        self.images.append(pygame.image.load('21.png'))
        self.images.append(pygame.image.load('22.png'))
        self.images.append(pygame.image.load('23.png'))
        self.images.append(pygame.image.load('24.png'))
        self.images.append(pygame.image.load('25.png'))
        self.images.append(pygame.image.load('26.png'))
        self.images.append(pygame.image.load('27.png'))
        self.images.append(pygame.image.load('28.png'))
        self.images.append(pygame.image.load('29.png'))

        self.index = 0

        self.image = self.images[self.index]

        self.rect = pygame.Rect(5, 5, 150, 198)

    def update(self):
        self.index += 1

        if self.index >= len(self.images):
            self.index = 0

        self.image = self.images[self.index]


# класс для анимации кота после хорошего результата в игре
class MyСat_Cool(pygame.sprite.Sprite):
    def __init__(self):
        super(MyСat_Cool, self).__init__()

        self.images = []
        self.images.append(pygame.image.load('30.png'))
        self.images.append(pygame.image.load('31.png'))
        self.images.append(pygame.image.load('32.png'))
        self.images.append(pygame.image.load('33.png'))

        self.index = 0

        self.image = self.images[self.index]

        self.rect = pygame.Rect(5, 5, 150, 198)

    def update(self):
        self.index += 1

        if self.index >= len(self.images):
            self.index = 0

        self.image = self.images[self.index]


# функция запуска анимации кота после игры
def cat_finish(game_score):
    time = 0
    if game_score < 50:
        screen = pygame.display.set_mode((600, 500))
        my_sprite = MyСat_Bad()
    elif game_score < 100:
        screen = pygame.display.set_mode((600, 500))
        my_sprite = MyСat_Midl()
    else:
        screen = pygame.display.set_mode((300, 250))
        my_sprite = MyСat_Cool()
    my_group = pygame.sprite.Group(my_sprite)

    while True:
        if time == 20:
            screen = pygame.display.set_mode((600, 400))
            show_end_screen(game_score)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        my_group.update()
        screen.fill(pygame.Color('black'))
        my_group.draw(screen)
        pygame.display.update()
        tic.tick(10)
        time += 1


def change_theme():
    pass



show_start_screen()
