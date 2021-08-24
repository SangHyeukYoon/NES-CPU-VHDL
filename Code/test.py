import pygame
import numpy

def ReadTile():
    tile = numpy.zeros((8, 8))

    for y in range(0, 8):
        tmp = int(file.read(1).hex(), 16)

        for x in range(7, -1, -1):
            if tmp % 2 == 1:
                tile[y, x] = 1

            tmp >>= 1

    for y in range(0, 8):
        tmp = int(file.read(1).hex(), 16)

        for x in range(7, -1, -1):
            if tmp % 2 == 1:
                if tile[y, x] == 1:
                    tile[y, x] = 3
                else:
                    tile[y, x] = 2

            tmp >>= 1

    return tile

def ReadPatternTabel(screen):
    for y in range(0, 16):
        for x in range(0, 16):
            tile = ReadTile()

            for t_y in range(0, 8):
                for t_x in range(0, 8):
                    if tile[t_y, t_x] == 1:
                        screen[x * 64 + t_x * 8 : x * 64 + t_x * 8 + 8,
                                y * 64 + t_y * 8 : y * 64 + t_y * 8 + 8, :] = 64
                    elif tile[t_y, t_x] == 2:
                        screen[x * 64 + t_x * 8 : x * 64 + t_x * 8 + 8,
                                y * 64 + t_y * 8 : y * 64 + t_y * 8 + 8, :] = 128
                    elif tile[t_y, t_x] == 3:
                        screen[x * 64 + t_x * 8 : x * 64 + t_x * 8 + 8,
                                y * 64 + t_y * 8 : y * 64 + t_y * 8 + 8, :] = 192

pygame.init()
display = pygame.display.set_mode((1024, 1024))

file = open('super-mario-bros.nes', 'rb')
file.read(16)
file.read(32768)

screen1 = numpy.zeros((1024, 1024, 3))
ReadPatternTabel(screen1)

screen2 = numpy.zeros((1024, 1024, 3))
ReadPatternTabel(screen2)

running = True
i = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if i > 200:
            i = 0
        elif i > 100:
            pygame.surfarray.blit_array(display, screen2)
        else:
            pygame.surfarray.blit_array(display, screen1)

        pygame.display.update()
        i += 1

        print(i)

pygame.quit()
