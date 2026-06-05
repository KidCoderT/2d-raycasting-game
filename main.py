import sys
import pygame

pygame.init()

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

shape_list = [[(120, 78), (108, 198), (192, 309), (283, 103)], [(105, 386), (162, 468), (90, 543)], [(360, 421), (316, 568), (541, 639), (498, 489)], [(748, 412), (688, 556), (878, 563), (958, 399)], [(852, 206), (875, 315), (1145, 230)], [(1035, 56), (1008, 105), (1065, 106)], [(507, 75), (766, 74), (771, 45), (507, 42)]]

class Wall:
    def __init__(self, p1, p2):
        self.start_pt = p1
        self.end_pt = p2
    
    def render(self, screen: pygame.Surface, color="grey"):
        pygame.draw.line(screen, color, self.start_pt, self.end_pt)

    @classmethod
    def decompose_polygon(self, shape: list[tuple[int, int]]) -> list[Wall]:
        lines = []
        for i in range(0, len(shape)):
            lines.append(Wall(shape[i-1], shape[i]))
        return lines

walls: list[Wall] = []

for shape in shape_list:
    walls.extend(Wall.decompose_polygon(shape))

def main():
    running = True

    while running:
        x, y = pygame.mouse.get_pos()

        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("white")

        # RENDER YOUR GAME HERE
        for shape in shape_list:
            pygame.draw.polygon(screen, "grey", shape, 2)
        
        for line in walls:
            line.render(screen, "red")

        pygame.draw.circle(screen, 'red', (x, y), 5)

        pygame.display.update()
        clock.tick(60)  # limits FPS to 60
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
