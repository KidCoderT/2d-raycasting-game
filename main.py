import math
import random
import sys

import pygame

pygame.init()


def get_hcf(a, b):
    while b:
        a, b = b, a % b
    return a


# TODO: MAKE THE WIDTH AND HEIGHT BASED ON TILE_SIZE, ROW AND COL CONST
SCREEN_WIDTH, HEIGHT = 1440, 720  # HCF = 80
WIDTH = SCREEN_WIDTH // 2
HCF = 72
print(HCF)

# 640, 720 -> 320, 360 -> 160, 180 -> 80, 90 -> 40, 45

MAZE_TILE_OPTIONS = [90, 72, 36, 18, 9, 3]
MAZE_TILE_INDEX = 2

MAZE_TILE_SIZE = MAZE_TILE_OPTIONS[MAZE_TILE_INDEX]
MAZE_ROWS, MAZE_COLS = HEIGHT // MAZE_TILE_SIZE, WIDTH // MAZE_TILE_SIZE
SCALE = MAZE_TILE_SIZE / HCF

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

screen = pygame.display.set_mode((SCREEN_WIDTH, HEIGHT))
map = pygame.Surface((WIDTH, HEIGHT))
render = pygame.Surface((WIDTH, HEIGHT))
clock = pygame.time.Clock()

pos = tuple[int, int] | tuple[float, float]

shape_list: list[list[pos]] = [
    [(221, 90), (93, 157), (119, 217), (252, 152)],
    [(126, 441), (238, 570), (196, 606), (87, 475)],
    [(560, 488), (441, 596), (474, 627), (596, 544)],
    [(479, 130), (510, 165), (521, 242), (559, 103), (612, 204)],
    [(81, 311), (79, 367), (130, 340)],
]

my_font = pygame.font.SysFont("Fira Code", 14)


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
    DEFAULT_ACCEL = 400
    DEFAULT_MAX_SPEED = 90
    DEFAULT_MAX_SPRINT_SPEED = 180
    DEFAULT_FRICTION = 12
    DEFAULT_ROT_SPEED = 250

    def __init__(
        self,
        pos,
        fov=60,
        accel=DEFAULT_ACCEL * SCALE,
        max_walk_speed=DEFAULT_MAX_SPEED * SCALE,
        max_sprint_speed=DEFAULT_MAX_SPRINT_SPEED * SCALE,
        friction=DEFAULT_FRICTION,
        rot_speed=DEFAULT_ROT_SPEED,
        extra_scaling=1,
    ):
        self.max_walk_speed = max_walk_speed * extra_scaling
        self.max_sprint_speed = max_sprint_speed * extra_scaling
        self.rot_speed = rot_speed
        self.fov = fov

        self.direction = 0  # right & clockwise direction
        self.position = pygame.Vector2(*pos)
        self.velocity = pygame.Vector2(0, 0)
        self.accel_speed = accel * extra_scaling
        self.friction = friction

        self.rays = []
        self.wall_distances = []
        self.wall_positions = []
        self.extra_scaling = extra_scaling

    def tiles_reset(self):
        # UNNESSERAY BUT FOR TEST CASE SO...
        old_max = self.max_walk_speed if self.max_walk_speed > 0 else 1.0

        # UPDATE THESE
        self.accel_speed = self.DEFAULT_ACCEL * SCALE * self.extra_scaling
        self.max_walk_speed = self.DEFAULT_MAX_SPEED * SCALE * self.extra_scaling
        self.max_sprint_speed = (
            self.DEFAULT_MAX_SPRINT_SPEED * SCALE * self.extra_scaling
        )
        # self.rot_speed = self.DEFAULT_ROT_SPEED

        # INCASE PLAYER MOVES WHILE WE ARE CHANING
        scale_ratio = self.max_walk_speed / old_max
        self.velocity *= scale_ratio * self.extra_scaling

    def update_position(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction -= self.rot_speed * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction += self.rot_speed * dt

        # 3. Determine if the character is moving forward or backward
        moving_forward = keys[pygame.K_w] or keys[pygame.K_UP]
        moving_backward = keys[pygame.K_s] or keys[pygame.K_DOWN]
        # 4. Determine if the character is sprinting
        sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        max_speed = self.max_walk_speed if not sprinting else self.max_sprint_speed

        # 2. Smoothly ramp up/down a singular speed scalar instead of a 2D vector
        # Extract the current length/speed from our tracking velocity
        current_speed = self.velocity.length()

        if moving_forward or moving_backward:
            # Determine target direction modifier (1 for forward, -1 for backward)
            direction_modifier = 1 if moving_forward else -1

            # if already accelerating from less keep same check
            if current_speed < max_speed:
                # Accelerate towards max_speed over time
                current_speed += self.accel_speed * dt
                if current_speed > max_speed:
                    current_speed = max_speed
            elif current_speed > max_speed:
                current_speed *= 1 - 4 * dt
                if current_speed < max_speed:
                    current_speed = max_speed

            # CRITICAL: Force the velocity vector to point EXACTLY where we are looking!
            # This completely eliminates the ice-skating drift.
            self.velocity = pygame.Vector2()
            self.velocity.from_polar(
                (current_speed * direction_modifier, self.direction)
            )

        else:
            # 3. Super fast slow down when no keys are pressed
            # Using a high friction multiplier (e.g., self.friction = 10.0 or higher)
            current_speed *= 1.0 - (self.friction * dt)

            if current_speed < 1.0:
                self.velocity = pygame.Vector2(0, 0)
            else:
                # Keep slowing down along the last known velocity heading
                self.velocity = self.velocity.normalize() * current_speed

        # 4. Move the character using frame-rate independent math
        self.position += self.velocity * dt

    def create_rays(self, walls, n=50):
        # ray = Ray((WIDTH / 2, HEIGHT / 2), (x, y))
        self.rays = [
            Ray.from_angle(
                self.position.xy,
                (self.direction - (self.fov / 2)) + (self.fov / n) * i,
            )
            for i in range(n)
        ]
        self.wall_distances = []
        self.wall_positions = []
        # rays = [Ray.from_angle(player.position.xy, player.direction)]

        for ray in self.rays:
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

            self.wall_positions.append(point)
            self.wall_distances.append(min_dist)

        return self.rays, self.wall_positions, self.wall_distances

    def render(self, screen: pygame.Surface):
        pygame.draw.circle(screen, "blue", self.position, 10 * SCALE)

        ray = Ray.from_angle(self.position.xy, self.direction)
        ray.render(screen, 50 * SCALE, "red")


class MazeCell:
    def __init__(self, x, y):
        self.i = x
        self.j = y
        self.index = y * MAZE_COLS + x
        self.walls = [True, True, True, True]  # TOP, RIGHT, BOTTOM, LEFT

        self.visited = False

    def reset(self):
        self.visited = False
        self.walls = [True, True, True, True]

    @property
    def ij(self):
        return self.i, self.j

    @property
    def cell_center(self):
        return ((self.i + 0.5) * MAZE_TILE_SIZE, (self.j + 0.5) * MAZE_TILE_SIZE)

    @property
    def cell_top_left(self):
        return ((self.i) * MAZE_TILE_SIZE, (self.j) * MAZE_TILE_SIZE)

    def render(
        self,
        screen: pygame.Surface,
        fill=False,
        width=1,
        line_color="white",
        fill_color="blue",
        DEBUG=False,
    ):
        points = []
        if self.walls[UP]:
            points.append(
                (
                    (self.i * MAZE_TILE_SIZE, self.j * MAZE_TILE_SIZE),
                    ((self.i + 1) * MAZE_TILE_SIZE, self.j * MAZE_TILE_SIZE),
                )
            )
        if self.walls[RIGHT]:
            points.append(
                (
                    ((self.i + 1) * MAZE_TILE_SIZE, self.j * MAZE_TILE_SIZE),
                    ((self.i + 1) * MAZE_TILE_SIZE, (self.j + 1) * MAZE_TILE_SIZE),
                )
            )
        if self.walls[DOWN]:
            points.append(
                (
                    (self.i * MAZE_TILE_SIZE, (self.j + 1) * MAZE_TILE_SIZE),
                    ((self.i + 1) * MAZE_TILE_SIZE, (self.j + 1) * MAZE_TILE_SIZE),
                )
            )
        if self.walls[LEFT]:
            points.append(
                (
                    (((self.i) * MAZE_TILE_SIZE), self.j * MAZE_TILE_SIZE),
                    (((self.i) * MAZE_TILE_SIZE), (self.j + 1) * MAZE_TILE_SIZE),
                )
            )

        if fill:
            pygame.draw.rect(
                screen,
                fill_color,
                (
                    self.i * MAZE_TILE_SIZE,
                    self.j * MAZE_TILE_SIZE,
                    MAZE_TILE_SIZE,
                    MAZE_TILE_SIZE,
                ),
            )

        for point in points:
            pygame.draw.line(screen, line_color, point[0], point[1], width)

        if DEBUG:
            text_surface = my_font.render(
                f"{self.index}\n{self.i},{self.j}", True, "white"
            )
            text_rect = text_surface.get_rect()
            text_rect.center = (
                (self.i + 0.5) * MAZE_TILE_SIZE,
                (self.j + 0.5) * MAZE_TILE_SIZE,
            )

            screen.blit(text_surface, text_rect)


class MazeGenerator:
    MAZE_TYPES = [
        "DFS",
        "BFS",
        "HUNT",
        "PRIM",
    ]

    @staticmethod
    def index_to_ij(index):
        i = index % MAZE_COLS
        j = index // MAZE_COLS
        return i, j

    @staticmethod
    def pos_to_index(i, j):
        return j * MAZE_COLS + i

    def __init__(self):
        self.cells: list[MazeCell] = []
        self.reset_tiles()

    def reset_maze(self):
        for cell in self.cells:
            cell.reset()

    def reset_tiles(self):
        self.cells: list[MazeCell] = []
        for index in range(MAZE_ROWS * MAZE_COLS):
            cell = MazeCell(*MazeGenerator.index_to_ij(index))
            assert cell.index == index
            self.cells.append(cell)

    def render(self, screen: pygame.Surface, DEBUG=False):
        for cell in self.cells:
            cell.render(screen, DEBUG=DEBUG)

    def highlight_cell(self, screen: pygame.Surface, index, color="red", DEBUG=False):
        self.cells[index].render(
            screen,
            fill=True,
            width=3,
            line_color="white",
            fill_color=color,
            DEBUG=DEBUG,
        )

    def highlight_cells(
        self, screen: pygame.Surface, indices, color="red", DEBUG=False
    ):
        for index in indices:
            self.highlight_cell(screen, index, color, DEBUG)

    def get_random_cell(self):
        index = random.randint(0, len(self.cells) - 1)
        return self.cells[index], index

    def get_cell_center(self, index):
        i, j = MazeGenerator.index_to_ij(index)
        return ((i + 0.5) * MAZE_TILE_SIZE, (j + 0.5) * MAZE_TILE_SIZE)

    def get_cell_top_left(self, index):
        i, j = MazeGenerator.index_to_ij(index)
        return (i * MAZE_TILE_SIZE, j * MAZE_TILE_SIZE)

    def get_neighbors_indices(self, index):
        o_i, o_j = MazeGenerator.index_to_ij(index)
        pos = [index - MAZE_COLS, index + 1, index + MAZE_COLS, index - 1]
        for idx in range(len(pos)):
            if pos[idx] < 0 or pos[idx] >= MAZE_ROWS * MAZE_COLS:
                pos[idx] = None
                continue

            n_i, n_j = MazeGenerator.index_to_ij(pos[idx])

            if n_i < 0 or n_i >= MAZE_COLS or n_j < 0 or n_j >= MAZE_ROWS:
                pos[idx] = None
                continue

            if abs(n_i - o_i) > 1 or abs(n_j - o_j) > 1:
                pos[idx] = None
                continue

        return pos

    @staticmethod
    def get_opposite_direction(direction):
        if direction == UP:
            return DOWN
        elif direction == RIGHT:
            return LEFT
        elif direction == DOWN:
            return UP
        elif direction == LEFT:
            return RIGHT
        else:
            raise ValueError("Invalid direction")

    def remove_walls(self, index, direction):
        neighbors = self.get_neighbors_indices(index)
        assert neighbors[direction] is not None, "No wall to remove"
        self.cells[index].walls[direction] = False
        self.cells[neighbors[direction]].walls[
            self.get_opposite_direction(direction)
        ] = False

    def remove_walls_between(self, index, neighbor, raise_error=True):
        og_i, og_j = self.cells[index].ij
        new_i, new_j = self.cells[neighbor].ij

        if new_i - og_i == 1 and new_j - og_j == 0:
            self.remove_walls(index, RIGHT)
        elif new_i - og_i == -1 and new_j - og_j == 0:
            self.remove_walls(index, LEFT)
        elif new_i - og_i == 0 and new_j - og_j == 1:
            self.remove_walls(index, DOWN)
        elif new_i - og_i == 0 and new_j - og_j == -1:
            self.remove_walls(index, UP)
        elif raise_error:
            raise ValueError("Invalid direction")

    def setup_maze(self, start_index=None, maze_type="BFS"):
        if maze_type == "PRIM":
            self.prims(start_index)
        elif maze_type == "HUNT":
            self.hunt_and_kill(start_index)
        elif maze_type == "DFS":
            self.dfs(start_index)
        elif maze_type == "BFS":
            self.bfs(start_index)
        else:
            raise ValueError("Invalid maze type")

    def dfs(self, start_index=None):
        self.reset_maze()

        if start_index is None:
            _, start_index = self.get_random_cell()

        self.cells[start_index].visited = True
        stack = [start_index]

        while stack:
            current_index = stack[-1]  # get the last element

            neighbors = [
                index
                for index in self.get_neighbors_indices(current_index)
                if index is not None and self.cells[index].visited is False
            ]

            if len(neighbors) == 0:
                stack.pop()  # remove the last element we reached an end
                continue

            next_index = random.choice(neighbors)

            self.remove_walls_between(current_index, next_index)
            self.cells[next_index].visited = True
            stack.append(next_index)

        # done!

    def bfs(self, start_index=None):
        self.reset_maze()

        if start_index is None:
            _, start_index = self.get_random_cell()

        self.cells[start_index].visited = True

        queue = []
        queue.extend(
            [idx for idx in self.get_neighbors_indices(start_index) if idx is not None]
        )

        while queue:
            current_index = random.choice(queue)  # get the first element
            queue.remove(current_index)

            if self.cells[current_index].visited:  # others already visited
                continue

            # we find the visited neighbors to connect back to
            visited_neighbors = [
                index
                for index in self.get_neighbors_indices(current_index)
                if index is not None and self.cells[index].visited
            ]

            if visited_neighbors:
                target_neighbor = random.choice(visited_neighbors)
                self.remove_walls_between(current_index, target_neighbor)

            # mark myself as visited
            self.cells[current_index].visited = True

            # add the unvisited neighbors to the queue
            queue.extend(
                [
                    idx
                    for idx in self.get_neighbors_indices(current_index)
                    if idx is not None and self.cells[idx].visited is False
                ]
            )

        # done!

    def hunt_and_kill(self, start_index=None):
        self.reset_maze()

        if start_index is None:
            _, start_index = self.get_random_cell()

        self.cells[start_index].visited = True

        current_index = start_index
        highest_indices = 0

        unvisited_count = (MAZE_ROWS * MAZE_COLS) - 1
        while unvisited_count > 0:
            neighbors = [
                idx
                for idx in self.get_neighbors_indices(current_index)
                if idx is not None and self.cells[idx].visited is False
            ]

            if neighbors:
                # KILL
                next_index = random.choice(neighbors)
                self.remove_walls_between(current_index, next_index)
                current_index = next_index
                self.cells[current_index].visited = True
                unvisited_count -= 1
            else:
                # HUNT
                found_new_start = False

                for idx in range(highest_indices, MAZE_ROWS * MAZE_COLS):
                    if self.cells[idx].visited:
                        if idx == highest_indices:
                            highest_indices += 1
                        continue

                    neighbors = [
                        idx
                        for idx in self.get_neighbors_indices(idx)
                        if idx is not None and self.cells[idx].visited
                    ]
                    if len(neighbors) == 0:
                        continue

                    prev = random.choice(neighbors)
                    self.remove_walls_between(prev, idx)
                    current_index = idx
                    self.cells[current_index].visited = True
                    unvisited_count -= 1
                    found_new_start = True
                    break

                if not found_new_start:
                    break

    def prims(self, start_index=None):
        self.reset_maze()

        if start_index is None:
            _, start_index = self.get_random_cell()

        self.cells[start_index].visited = True

        walls_list = [
            (start_index, idx)
            for idx in self.get_neighbors_indices(start_index)
            if idx is not None and self.cells[idx] is not None
        ]

        # remaining_loops = (ROWS * COLS) - 1
        while walls_list:
            rand_idx = random.randrange(len(walls_list))
            joint = walls_list.pop(rand_idx)
            start, new = joint
            if self.cells[new].visited:
                continue

            self.remove_walls_between(*joint)
            self.cells[new].visited = True

            walls_list.extend(
                [
                    (new, idx)
                    for idx in self.get_neighbors_indices(new)
                    if idx is not None
                    and self.cells[idx] is not None
                    and self.cells[idx].visited is False
                ]
            )


class GridCells:
    CELL_TYPES = {
        "WALL": 1,
        "SPACE": 0,
    }

    def __init__(self, i, j, grid: Grid, type=0):
        self.i = i
        self.j = j
        self.type = type
        self.index = grid.cols * j + i
        self.grid = grid

        assert self.type in self.CELL_TYPES.values()

    def reset(self):
        self.type = 0

    def convert_type(self, type):
        if type in self.CELL_TYPES.keys():
            self.type = self.CELL_TYPES[type]
        else:
            raise ValueError("Invalid type")

    def render(self, screen: pygame.Surface, DEBUG=False):
        pygame.draw.rect(
            screen,
            "black" if self.type == 0 else "grey",
            (
                self.i * self.grid.tile_size,
                self.j * self.grid.tile_size,
                self.grid.tile_size,
                self.grid.tile_size,
            ),
        )
        if DEBUG:
            text_surface = my_font.render(
                f"{self.index}\n{self.i},{self.j}", True, "white"
            )
            text_rect = text_surface.get_rect()
            text_rect.center = (
                (self.i + 0.5) * self.grid.tile_size,
                (self.j + 0.5) * self.grid.tile_size,
            )

            screen.blit(text_surface, text_rect)


class Grid:
    def __init__(self):
        self.cells: list[GridCells] = []
        self.reset_tiles()

    def index_to_ij(self, index):
        i = index % self.cols
        j = index // self.cols
        return i, j

    def pos_to_index(self, i, j):
        return j * self.cols + i

    def reset_tiles(self):
        self.cells: list[GridCells] = []
        self.rows = MAZE_ROWS * 3
        self.cols = MAZE_COLS * 3
        self.tile_size = MAZE_TILE_SIZE / 3

        for i in range(self.rows * self.cols):
            self.cells.append(
                GridCells(
                    i % self.cols,
                    i // self.cols,
                    self,
                )
            )

    def setup_maze(self, maze: MazeGenerator):
        for cell in self.cells:
            self.cells[cell.index].reset()

        for idx, maze_cell in enumerate(maze.cells):
            maze_i, maze_j = maze_cell.ij
            scalled_i = maze_i * 3
            scalled_j = maze_j * 3

            to_be_walled = []

            # Make all corners wall
            to_be_walled.append(self.pos_to_index(scalled_i, scalled_j))
            to_be_walled.append(self.pos_to_index(scalled_i + 2, scalled_j))
            to_be_walled.append(self.pos_to_index(scalled_i + 2, scalled_j + 2))
            to_be_walled.append(self.pos_to_index(scalled_i, scalled_j + 2))

            if maze_cell.walls[UP]:
                to_be_walled.append(self.pos_to_index(scalled_i + 1, scalled_j))
            if maze_cell.walls[RIGHT]:
                to_be_walled.append(self.pos_to_index(scalled_i + 2, scalled_j + 1))
            if maze_cell.walls[DOWN]:
                to_be_walled.append(self.pos_to_index(scalled_i + 1, scalled_j + 2))
            if maze_cell.walls[LEFT]:
                to_be_walled.append(self.pos_to_index(scalled_i, scalled_j + 1))

            for index in to_be_walled:
                self.cells[index].convert_type("WALL")

    def render(self, screen: pygame.Surface, DEBUG=False):
        for cell in self.cells:
            cell.render(screen, DEBUG=DEBUG)

    def maze_to_grid_idx(self, maze_idx, center_cell=False):
        maze_i, maze_j = MazeGenerator.index_to_ij(maze_idx)

        if center_cell:
            return self.pos_to_index(maze_i * 3 + 1, maze_j * 3 + 1)

        return self.pos_to_index(maze_i * 3, maze_j * 3)

    def get_cell_center(self, index):
        i, j = self.index_to_ij(index)
        return pygame.Vector2((i + 0.5) * self.tile_size, (j + 0.5) * self.tile_size)

    def get_random_cell(self):
        index = random.randint(0, len(self.cells) - 1)
        return self.cells[index], index


class Game:
    def __init__(self):
        self.maze = MazeGenerator()
        self.player1 = Player((0, 0))
        self.player2 = Player((0, 0), extra_scaling=3)
        self.grid = Grid()
        # self.walls = maze.get_walls()
        self.wall_size = SCREEN_WIDTH
        self.no_of_rays = 200
        self.max_depth = 800

        self.maze_type = "DFS"  # DEFAULT

        self.set_game()

    def reset_game_tiles(self):
        self.maze.reset_tiles()
        self.grid.reset_tiles()
        self.player1.tiles_reset()
        self.player2.tiles_reset()

    def set_game(self, new_maze_type=None):
        if new_maze_type is not None:
            self.maze_type = new_maze_type
        # TODO: MAKE IT POINT IN OPEN SPACE

        _, start_index = self.maze.get_random_cell()
        self.player1.position = self.maze.get_cell_center(start_index)
        self.player1.direction = 0
        self.maze.setup_maze(start_index, self.maze_type)
        self.grid.setup_maze(self.maze)

        grid_start_index = self.grid.maze_to_grid_idx(start_index, True)
        self.player2.position = self.grid.get_cell_center(grid_start_index)
        self.player2.direction = 0

    def update_and_render(self, map, render, dt):
        # fill the screen with a color to wipe away anything from last frame
        map.fill("black")

        # for shape in shape_list:
        #     pygame.draw.polygon(map, "white", shape, 2)
        #
        # for line in walls:
        #     line.render(map, "grey")

        self.player1.update_position(dt)
        self.player2.update_position(dt)

        # rays, wall_positions, wall_distances = player.create_rays(walls, no_of_rays)
        # corrected_distances = []
        # wall_heights = []
        # alpha_values = []

        # for i in range(len(rays)):
        #     if wall_positions[i] is not None:
        #         rays[i].render(map, wall_distances[i])
        #         pygame.draw.circle(map, "red", wall_positions[i], 5)
        #
        #     correct_dist = wall_distances[i] * math.cos(
        #         (i * (player.fov / no_of_rays) - (player.fov / 2)) * (math.pi / 180)
        #     )
        #
        #     wall_height = (wall_size * 15) / correct_dist
        #
        #     factor = pygame.math.clamp(1 - (wall_distances[i] / max_depth), 0, 1)
        #
        #     corrected_distances.append(correct_dist)
        #     wall_heights.append(wall_height)
        #     alpha_values.append(factor * 255)
        #

        self.maze.render(map)
        self.player1.render(map)

        self.grid.render(render)
        self.player2.render(render)

        # MAKEING THE PLAYER VIEW
        # render.fill("black")
        #
        # box_width = (WIDTH / 2) / no_of_rays
        # for i in range(no_of_rays):
        #     wall_top = (HEIGHT / 2) - (wall_heights[i] / 2)
        #     pygame.draw.rect(
        #         render,
        #         pygame.Color(alpha_values[i], alpha_values[i], alpha_values[i]),
        #         pygame.Rect(i * box_width, wall_top, box_width + 1, wall_heights[i]),
        #     )

        screen.blit(map, (0, 0))
        screen.blit(render, (WIDTH, 0))

        pygame.draw.line(screen, "white", (WIDTH, 0), (WIDTH, HEIGHT))


# walls: list[Wall] = [
#     Wall((-1, -1), (WIDTH, -1)),
#     Wall((-1, -1), (-1, HEIGHT)),
#     Wall((WIDTH, HEIGHT), (-1, HEIGHT)),
#     Wall((WIDTH, HEIGHT), (WIDTH, -1)),
# ]
#
# for shape in shape_list:
#     walls.extend(Wall.decompose_polygon(shape))


game = Game()


def main():
    global \
        MAZE_TILE_INDEX, \
        MAZE_TILE_SIZE, \
        MAZE_ROWS, \
        MAZE_COLS, \
        SCALE, \
        MAZE_TILE_OPTIONS
    running = True
    dt = 0

    while running:
        mx, my = pygame.mouse.get_pos()

        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game.set_game(MazeGenerator.MAZE_TYPES[0])
                elif event.key == pygame.K_2:
                    game.set_game(MazeGenerator.MAZE_TYPES[1])
                elif event.key == pygame.K_3:
                    game.set_game(MazeGenerator.MAZE_TYPES[2])
                elif event.key == pygame.K_4:
                    game.set_game(MazeGenerator.MAZE_TYPES[3])

                if (
                    event.key == pygame.K_EQUALS
                    and MAZE_TILE_INDEX < len(MAZE_TILE_OPTIONS) - 1
                ):
                    MAZE_TILE_INDEX += 1
                    MAZE_TILE_SIZE = MAZE_TILE_OPTIONS[MAZE_TILE_INDEX]
                    # TILE_SIZE = TILE_SIZE * 2

                    MAZE_ROWS, MAZE_COLS = (
                        HEIGHT // MAZE_TILE_SIZE,
                        WIDTH // MAZE_TILE_SIZE,
                    )
                    SCALE = MAZE_TILE_SIZE / HCF
                    game.reset_game_tiles()
                    game.set_game()

                if event.key == pygame.K_MINUS and MAZE_TILE_INDEX > 0:
                    MAZE_TILE_INDEX -= 1
                    MAZE_TILE_SIZE = MAZE_TILE_OPTIONS[MAZE_TILE_INDEX]
                    # TILE_SIZE = TILE_SIZE // 2

                    MAZE_ROWS, MAZE_COLS = (
                        HEIGHT // MAZE_TILE_SIZE,
                        WIDTH // MAZE_TILE_SIZE,
                    )
                    SCALE = MAZE_TILE_SIZE / HCF
                    game.reset_game_tiles()
                    game.set_game()

        game.update_and_render(map, render, dt)

        pygame.display.update()
        dt = clock.tick(60) / 1000

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
