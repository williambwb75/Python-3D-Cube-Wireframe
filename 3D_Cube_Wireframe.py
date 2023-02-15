import math
import pygame
pygame.init()

PI   = math.pi # 180
PI_2 = PI*2    # 360
PI_4 = PI/2    # 90

#   -   Class

class Camera:
    def __init__(self, 
        pos:         tuple[float, float, float], 
        focal_lengh: float, 
        surf_size:   tuple[int, int],

        width:   int   = 10,
        angle_x: float = PI_4, 
        angle_y: float = 0, 
        angle_z: float = 0,
        ):

        self.x, self.y, self.z = pos
        self.focal_lengh = focal_lengh
        self.width = width

        self.angle_x = angle_x
        self.angle_y = angle_y
        self.angle_z = angle_z

        self.surf_size = surf_size
        self.surf_size_2 = round(surf_size[0]/2), round(surf_size[1]/2)

    def project_point(self, 
        point: tuple[float, float, float],
        ):

        x, y, z = point
        surf_w, surf_h = self.surf_size
        surf_w2, surf_h2 = self.surf_size_2

        # Adapting To Camera

        x, y = rotate_around((x, y), (self.x, self.y), self.angle_z)
        z, y = rotate_around((z, y), (self.z, self.y), self.angle_x-PI_4)
        x, z = rotate_around((x, z), (self.x, self.z), self.angle_y)

        x -= self.x
        y -= self.y
        z -= self.z

        # Projection

        if y <= self.width: return None

        angle = math.atan(x/y)
        x_pos = math.tan(angle)*self.focal_lengh
        x_pos += surf_w2

        angle = math.atan(z/y)
        y_pos = math.tan(angle)*self.focal_lengh
        y_pos += surf_h2
        y_pos = surf_h - y_pos

        return round(x_pos), round(y_pos)

    def move(self, 
        amount: float,
        ):

        self.x += math.sin(self.angle_z) * amount
        self.y += math.cos(self.angle_z) * amount

    def slide(self, 
        amount: float,
        ):

        self.x += math.sin(self.angle_z+PI_4) * amount
        self.y += math.cos(self.angle_z+PI_4) * amount

class Mesh:
    def __init__(self,
        vertex_list: list[tuple[float, float, float]],
        face_list:   list[tuple[int, int, int]],
        ):

        self.vertex_list = vertex_list
        self.project_list = [None for _ in vertex_list]

        self.face_list = face_list
        self.face_order = [None for _ in face_list]

    def calculate_points(self, 
        camera: Camera,
        ):

        for i, vertex in enumerate(self.vertex_list):
            self.project_list[i] = camera.project_point(vertex)

    def order_faces(self,
        camera: Camera
        ):

        self.face_order = []

        for index, points in enumerate(self.face_list):
            dist = 0
            for i in points:
                x, y, z = self.vertex_list[i] 
                dist += abs(x-camera.x) + abs(y-camera.y) + abs(z-camera.z)
            self.face_order.append((dist, index))

        self.face_order.sort(key = lambda tuple : tuple[0], reverse = True)
    
        for index, (dist, i) in enumerate(self.face_order):
            self.face_order[index] = i

    def draw(self, 
        surf: pygame.Surface,
        ):

        for face_index in self.face_order:
            pos_1, pos_2, pos_3, pos_4 = self.face_list[face_index]

            pos_1 = self.project_list[pos_1]
            pos_2 = self.project_list[pos_2]
            pos_3 = self.project_list[pos_3]
            pos_4 = self.project_list[pos_4]

            try: pygame.draw.polygon(surf, (200, 200, 200), [pos_1, pos_2, pos_4, pos_3], 1)
            except: pass

#   -   Functions

def angle_check(
    angle: float,
    ):

    if angle < 0:    angle += PI_2
    if angle > PI_2: angle += PI_2
    return angle

def distance(
    pos_1: float, 
    pos_2: float,
    ):

    ax, ay = pos_1
    bx, by = pos_2
    return math.sqrt((bx - ax) * (bx - ax) + (by - ay) * (by - ay)) 

def angle_to_point(
    pos_1: float, 
    pos_2: float,
    ):

    ax, ay = pos_1
    bx, by = pos_2
    angle = math.atan2(by - ay, bx - ax)
    
    return angle

def rotate_around(
    point:          tuple[float, float], 
    around_point:   tuple[float, float], 
    amount:         float,
    ):

    dist = distance(point, around_point)
    angle = angle_to_point(point, around_point)
    angle += amount + PI
    angle = angle_check(angle)

    x, y = around_point
    x += math.cos(angle)*dist
    y += math.sin(angle)*dist

    return x, y

#   -   Variabels

win_size = 1280, 640
win = pygame.display.set_mode(win_size)
clock = pygame.time.Clock()

camera = Camera((0, 0, 0), 1280/3, win_size)
mesh = Mesh(
    [(-25, 325, -25), 
     ( 25, 325, -25), 
     (-25, 275, -25), 
     ( 25, 275, -25), 
     ( 25, 325,  25), 
     (-25, 325,  25), 
     ( 25, 275,  25), 
     (-25, 275,  25)]
    ,
    [(0, 1, 2, 3), # Front
     (4, 5, 6, 7), # Back
     (1, 4, 3, 6), # Left
     (5, 0, 7, 2), # Right
     (5, 4, 0, 1), # Top
     (2, 3, 7, 6)] # Base
    )

#   -   Main

engage = False

run = True
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False
        if event.type == pygame.MOUSEBUTTONDOWN: 
            engage = not engage
            pygame.mouse.set_visible(not engage)

    if engage: pygame.mouse.set_pos(camera.surf_size_2)

    pygame.display.update()
    clock.tick(60)
    win.fill((30, 30, 30))

    if engage:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: camera.move( 1)
        if keys[pygame.K_s]: camera.move(-1)
        if keys[pygame.K_a]: camera.slide(-1)
        if keys[pygame.K_d]: camera.slide( 1)

        if keys[pygame.K_SPACE]:  camera.z += 1
        if keys[pygame.K_LSHIFT]: camera.z -= 1

        mouse_rel = pygame.mouse.get_rel()
        camera.angle_z += mouse_rel[0]/1000
        camera.angle_x -= mouse_rel[1]/1000
        if camera.angle_x <= 0: camera.angle_x = 0
        if camera.angle_x >= PI: camera.angle_x = PI

    mesh.calculate_points(camera)
    mesh.order_faces(camera)
    mesh.draw(win)