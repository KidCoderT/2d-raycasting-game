import math
import sys

import pygame

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

shape_list = [
    [(120, 78), (108, 198), (192, 309), (283, 103)],
    [(105, 386), (162, 468), (90, 543)],
    [(360, 421), (316, 568), (541, 639), (498, 489)],
    [(748, 412), (688, 556), (878, 563), (958, 399)],
    [(852, 206), (875, 315), (1145, 230)],
    [(1035, 56), (1008, 105), (1065, 106)],
    [(507, 75), (766, 74), (771, 45), (507, 42)],
]


class Wall:
    def __init__(self, p1, p2):
        self.start_pt = p1
        self.end_pt = p2

        # its a line from the start pt to the end point
        x = p2[0] - p1[0]
        y = p2[1] - p1[1]
        self.direction = pygame.Vector2(x, y).normalize()
        self.magnitude = math.sqrt(x * x + y * y)

    def render(self, screen: pygame.Surface, color="grey"):
        pygame.draw.line(screen, color, self.start_pt, self.end_pt)

    @classmethod
    def decompose_polygon(self, shape: list[tuple[int, int]]) -> list[Wall]:
        lines = []
        for i in range(0, len(shape)):
            lines.append(Wall(shape[i - 1], shape[i]))
        return lines


class Ray:
    def __init__(self, origin: tuple[int, int], towards: tuple[int, int]):
        self.origin = origin
        self.towards = towards

        self.direction = pygame.Vector2(
            towards[0] - origin[0], towards[1] - origin[1]
        ).normalize()

    def render(self, screen, length, color="red"):
        end = (
            self.origin[0] + self.direction.x * length,
            self.origin[1] + self.direction.y * length,
        )
        pygame.draw.line(screen, color, self.origin, end)

    def cast(self, wall: Wall):
        # check if wall and ray ||
        if wall.direction.angle == self.direction.angle:
            return

        x2, y2 = wall.start_pt
        x1, y1 = self.origin
        rdx, rdy = self.direction.xy
        wdx, wdy = wall.direction.xy

        denom = wdy * rdx - wdx * rdy

        if denom == 0:
            return

        T2 = ((x2 - x1) * rdy + (y1 - y2) * rdx) / denom

        if not (0 < T2 < wall.magnitude):
            return

        T1 = ((x2 - x1) + T2 * wdx) / rdx if rdx != 0 else ((y2 - y1) + T2 * wdy) / rdy

        if not (T1 > 0):
            return

        x = self.origin[0] + T1 * self.direction.x
        y = self.origin[1] + T1 * self.direction.y

        return (
            (x, y),
            math.sqrt((x - x1) ** 2 + (y - y1) ** 2),  # dist from origin of ray
            pygame.Vector2(x, y).normalize(),
        )

    @classmethod
    def from_angle(self, origin, azimutal_angle):
        vector = pygame.Vector2()
        vector.from_polar((1, azimutal_angle))
        assert vector.is_normalized()
        og_vec = pygame.Vector2(*origin)
        towards_vec = og_vec + vector
        return Ray(origin, towards_vec.xy)


walls: list[Wall] = [
    Wall((0, 0), (WIDTH, 0)),
    Wall((0, 0), (0, HEIGHT)),
    Wall((WIDTH, HEIGHT), (0, HEIGHT)),
    Wall((WIDTH, HEIGHT), (WIDTH, 0)),
]

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

        # ray = Ray((WIDTH / 2, HEIGHT / 2), (x, y))
        n = 50
        rays = [Ray.from_angle((x, y), (360 / n) * i) for i in range(n)]
        # ray.render(screen, 700)

        for ray in rays:
            # ray.render(screen, 700, "grey")
            min_dist = math.inf
            point = None
            for wall in walls:
                out = ray.cast(wall)

                if out is None:
                    continue

                p, dist, _ = out
                if dist < min_dist:
                    min_dist = dist
                    point = p

            if point is not None:
                ray.render(screen, min_dist)
                pygame.draw.circle(screen, "red", point, 5)

        pygame.display.update()
        clock.tick(60)  # limits FPS to 60

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
