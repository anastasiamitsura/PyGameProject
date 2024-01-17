import pygame
import sys
import random

# размер блока
size_block = 20
# цвета
white = (255, 255, 255)
blue = (0, 170, 255)
frame_color = (0, 255, 255)
snake_color = (0, 200, 0)
# граница блоков
mar = 5
red = (255, 0, 0)
h_color = (0, 200, 150)
# размер поля в блоках
count_block = 20
# отступ сверху
h_mar = 70
# размер одного блока
size = [size_block * count_block + 2 * size_block + mar * count_block,
        size_block * count_block + 2 * size_block + mar * count_block + h_mar]
# установка самого окна
screen = pygame.display.set_mode(size)
pygame.display.set_caption("змейка")
# время
timer = pygame.time.Clock()


class SnakeB:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # функции проверки не вышла ли змейка за границы поля
    def is_inside(self):
        return 0 <= self.x < count_block and 0 <= self.y < count_block

    def __eq__(self, other):
        return isinstance(other, SnakeB) and self.x == other.x and self.y == other.y


# функция генерации координат рандомного пустого блока для создания цели
def random_block():
    x = random.randint(0, count_block - 1)
    y = random.randint(0, count_block - 1)
    empty_block = SnakeB(x, y)
    # проверка чтобы блок не был в границах поля или в самой змейке
    while empty_block in snake_block:
        empty_block.x - random.randint(0, count_block - 1)
        empty_block.y = random.randint(0, count_block - 1)
    return empty_block


# функция создания блока
def draw_block(color, row, col):
    pygame.draw.rect(screen, color, [size_block + col * size_block + mar * (col + 1),
                                     h_mar + size_block + row * size_block + mar * (row + 1), size_block,
                                     size_block])


# координаты начала игры
snake_block = [SnakeB(9, 8), SnakeB(9, 9), SnakeB(9, 10)]
apple = random_block()
d_row = 0
d_col = 1
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # при нажатии на клавишу:
        elif event.type == pygame.KEYDOWN:
            # стрелочка вверх
            if event.key == pygame.K_UP and d_col != 0:
                d_row = -1
                d_col = 0
            # стрелочка вниз
            elif event.key == pygame.K_DOWN and d_col != 0:
                d_row = 1
                d_col = 0
            # стрелочка влево
            elif event.key == pygame.K_LEFT and d_row != 0:
                d_row = 0
                d_col = -1
            # стрелочка вправо
            elif event.key == pygame.K_RIGHT and d_row != 0:
                d_row = 0
                d_col = 1
    # заполнение экрана цветом фона
    screen.fill(frame_color)
    pygame.draw.rect(screen, h_color, [0, 0, size[0], h_mar])
    # создание клетчатого поля
    for row in range(count_block):
        for col in range(count_block):
            if (row + col) % 2 == 0:
                color = blue
            else:
                color = white
            draw_block(color, row, col)
    # голова змеи
    head = snake_block[-1]
    if not head.is_inside():
        pygame.quit()
        sys.exit()
    draw_block(red, apple.x, apple.y)
    for block in snake_block:
        draw_block(snake_color, block.x, block.y)
    if apple == head:
        snake_block.append(apple)
        apple = random_block()
    new_head = SnakeB(head.x + d_row, head.y + d_col)
    snake_block.append(new_head)
    snake_block.pop(0)
    pygame.display.flip()
    timer.tick(3)
