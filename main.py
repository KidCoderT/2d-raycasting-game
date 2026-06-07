import math
import sys

import pygame

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
map = pygame.Surface((WIDTH / 2, HEIGHT))
render = pygame.Surface((WIDTH / 2, HEIGHT))
clock = pygame.time.Clock()

pos = tuple[int, int] | tuple[float, float]

shape_list: list[list[pos]] = [
    [(221, 90), (93, 157), (119, 217), (252, 152)],
    [(126, 441), (238, 570), (196, 606), (87, 475)],
    [(560, 488), (441, 596), (474, 627), (596, 544)],
    [(479, 130), (510, 165), (521, 242), (559, 103), (612, 204)],
    [(81, 311), (79, 367), (130, 340)],
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
    def decompose_polygon(cls, shape: list[pos]) -> list[Wall]:
        lines = []
        for i in range(0, len(shape)):
            lines.append(Wall(shape[i - 1], shape[i]))
        return lines


class Ray:
    def __init__(self, origin: pos, towards: pos):
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
            T1,  # dist from origin of ray
        )

    @classmethod
    def from_angle(cls, origin, azimutal_angle):
        vector = pygame.Vector2()
        vector.from_polar((1, azimutal_angle))
        assert vector.is_normalized()
        og_vec = pygame.Vector2(*origin)
        towards_vec = og_vec + vector
        return Ray(origin, (towards_vec.x, towards_vec.y))


class Player:
    def __init__(self, pos, speed=300, rot_speed=3):
        self.direction = 0  # right & clockwise direction
        self.position = pygame.Vector2(*pos)
        self.speed = speed
        self.rot_speed = rot_speed

    def update_position(self, dt):
        keys = pygame.key.get_pressed()
        speed = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            speed = self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            speed = self.speed * -0.3
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction -= self.rot_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction += self.rot_speed

        vector = pygame.Vector2()
        vector.from_polar((speed, self.direction))

        self.position.y += vector.y * dt
        self.position.x += vector.x * dt

    def render(self, screen: pygame.Surface):
        pygame.draw.circle(screen, "blue", self.position, 10)


walls: list[Wall] = [
    Wall((0, 0), (WIDTH, 0)),
    Wall((0, 0), (0, HEIGHT)),
    Wall((WIDTH, HEIGHT), (0, HEIGHT)),
    Wall((WIDTH, HEIGHT), (WIDTH, 0)),
]

for shape in shape_list:
    walls.extend(Wall.decompose_polygon(shape))

player = Player((WIDTH / 4, HEIGHT / 2))


def main():
    running = True
    dt = 0

    while running:
        mx, my = pygame.mouse.get_pos()

        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        map.fill("black")

        # RENDER YOUR GAME HERE
        for shape in shape_list:
            pygame.draw.polygon(map, "white", shape, 2)

        for line in walls:
            line.render(map, "grey")

        player.update_position(dt)

        # ray = Ray((WIDTH / 2, HEIGHT / 2), (x, y))
        n = 300
        rays = [Ray.from_angle(player.position.xy, (360 / n) * i) for i in range(n)]
        # rays = [Ray.from_angle(player.position.xy, player.direction)]
        # ray.render(screen, 700)

        for ray in rays:
            # ray.render(screen, 700, "grey")
            min_dist = math.inf
            point = None
            for wall in walls:
                out = ray.cast(wall)

                if out is None:
                    continue

                p, dist = out
                if dist < min_dist:
                    min_dist = dist
                    point = p

            if point is not None:
                ray.render(map, min_dist)
                pygame.draw.circle(map, "red", point, 5)

        player.render(map)

        screen.blit(map, (0, 0))
        screen.blit(render, (WIDTH / 2, 0))

        pygame.display.update()
        dt = clock.tick(60) / 1000

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
