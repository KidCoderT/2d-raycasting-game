import sys
import pygame

pygame.init()

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()


def create_level():
    shapes_list = []
    point_list = []

    running = True
    i = 0

    while running:
        x, y = pygame.mouse.get_pos()

        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                point_list.append((x, y))

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("white")

        if pygame.key.get_pressed()[pygame.K_d] and len(point_list) >= 1:
            point_list.pop()

        if pygame.key.get_pressed()[pygame.K_a] and len(point_list) >= 3:
            shapes_list.append(point_list.copy())
            point_list = []

        # RENDER YOUR GAME HERE
        pygame.draw.circle(screen, 'red', (x, y), 5)

        for shape_points in shapes_list:
            for point in shape_points:
                pygame.draw.circle(screen, 'red', (point[0], point[1]), 5)

        for point in point_list:
            pygame.draw.circle(screen, 'yellow', (point[0], point[1]), 5)

        pygame.display.update()
        clock.tick(60)  # limits FPS to 60
        i += 1
    
    print(shapes_list)
    pygame.quit()
    sys.exit()