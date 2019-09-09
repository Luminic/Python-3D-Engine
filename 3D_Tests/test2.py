"""
3D Engine
Created by: Lucas Purwosumarto
Email: lukas.dot.py@gmail.com
Last Modified: 8 September 2019
"""

import pygame
pygame.init()

from Hitboxes import *
from Matrices import *
from Obj_Loader import *

import numpy as np

import math
import random

"""
Right Handed System (Z points towards the player)
Player starts facing "Right" on the devscreen

Player Vision:
Down     | Y
Right    | X
Forwards | Z

Yaw Axis   | Y
Pitch Axis | X
Roll Axis  | Z

Dev Vision:
N/S | X
E/W | Z
Not Pictured: Y
"""

class Game:
    def __init__(self):
        self.dev_mode = True
        # Pygame Setup
        self.viewport = [0,0,800,1000]
        self.screen = pygame.display.set_mode((self.viewport[2], self.viewport[3]))
        self.screen.fill((25,50,185))
        pygame.display.set_caption('3D Engine 2.0')
        pygame.display.update()

        # Seconday Screen Setups
        self.gameviewport = [800,600]
        self.gamescreen = pygame.Surface(self.gameviewport)
        self.gamescreen.fill((200,0,0))

        if self.dev_mode:
            self.devviewport = [800,400]
            self.devscreen = pygame.Surface(self.devviewport)
            self.devscreen.fill((0,0,0))

        # Mouse Setup
        pygame.event.set_grab(False) # If the game crashes and this is set to True...
        pygame.mouse.set_visible(True)

        # Other Setup
        self.running = True
        self.clock = pygame.time.Clock()
        self.pressedkeys = {} # Keys currently pressed

        # 3D Setup
        self.sun_dir = [-0.35,0.5,0.15]
        self.ang = 0
        self.do_depth_test = False
        self.do_sorting = not self.do_depth_test # Pointless if depth testing is set to true
        if self.do_depth_test:
            self.depth_buffer = np.array([[0.0]*self.gameviewport[0]]*self.gameviewport[1])


    def mainloop(self):
        while self.running:
            self.update()

            p.update()

            if self.dev_mode:
                self.render_object(g.gamescreen, obj_points, obj_faces=obj_faces,\
                        translate=[g.gameviewport[i]/2 for i in range(2)],\
                        devscreen=g.devscreen, devscreen_trans=[g.devviewport[i]/2 for i in range(2)])
            else:
                self.render_object(g.gamescreen, obj_points, obj_edges, obj_faces, translate=[g.gameviewport[i]/2 for i in range(2)])

            self.screen.blit(self.gamescreen, (0,0))

            if self.dev_mode: self.screen.blit(self.devscreen, (0,self.viewport[3]-self.devviewport[1]))

            self.clock.tick()
            pygame.display.update()

        pygame.quit()

    def update(self):
        self.events_check()

        self.gamescreen.fill((200,0,0))
        if self.dev_mode:
            self.devscreen.fill((0,0,0))
            self.text(self.devscreen, "FPS: "+str(self.clock.get_fps()), [5,5], 25, color=[255,255,255])

        #self.ang += 1
        #if self.ang >= 360: self.ang = 0
        #self.sun_dir = mat_rot([[-0.35,0.5,0.15]], math.radians(self.ang), 'y')[0]

    def render_object(self, screen, obj_points, obj_edges=[], obj_faces=[], translate=[0,0], devscreen=False, devscreen_trans=[0,0]):
        """
        Input:  screen is the pygame surface the rendered object should be drawn on
                obj_points is a list of points
                obj_edges is a list containing pairs of point indexes (in list form) to be connected by an edge
                obj_faces has no functionality

                devscreen is the pygame surface the points will be drawn on from a top down orthographic view

        Output: None
        """
        obj_rendered_points = []
        for point in obj_points:
            if devscreen:
                pygame.draw.circle(devscreen, (0,0,235), [round(self.to_dev_coords(point)[i]+devscreen_trans[i]) for i in range(2)], 2)

            point = self.point_tranformation(point)

            if point:
                point = Point([round(point[i]+translate[i]) for i in range(2)]+[point[2]])
                obj_rendered_points.append(point)
                #pygame.draw.circle(screen, (0,0,245), point[:2], 2)

            else: obj_rendered_points.append(False)
        #for edge in obj_edges:
        #    if obj_rendered_points[edge[0]] and obj_rendered_points[edge[1]]:
        #        pygame.draw.aaline(screen, (50,245,245), obj_rendered_points[edge[0]][:2], obj_rendered_points[edge[1]][:2])

        if obj_faces:
            if self.do_depth_test: self.depth_buffer.fill(0)
            if self.do_sorting:
                all_face_points_rendered = [[obj_rendered_points[j] for j in o_face]+[obj_points[j] for j in o_face] for o_face in obj_faces]
                all_face_points_rendered.sort(key=lambda x:-sum([x[i][2] for i in range(3)])/3 if all(x) else 100)
            for i in range(len(obj_faces)):
                if self.do_sorting:
                    face_points = all_face_points_rendered[i][3:]
                    face_points_rendered = all_face_points_rendered[i][:3]
                else:
                    face_points = [obj_points[j] for j in obj_faces[i]]
                    face_points_rendered = [obj_rendered_points[j] for j in obj_faces[i]]

                if all(face_points_rendered):
                    face_norm = self.normal_vector(face_points, True)

                    col = self.sun_lighting(self.sun_dir, face_norm, obj_face_colors[i])
                    #try: obj_faces[i][4] = col
                    #except IndexError: obj_faces[i].append(col)

                    """
                    Get the equation of the polygon (which is assumed to be flat so any 3 points on the polygon can be used)
                    The normal vector can be found by getting the cross product of the plane's two vectors
                    The normal vector = [a,b,c] (Remember, the equation for a 3d plane is ax+by+cz=d)
                    Using the equation z' = z - (a*delta_x + b*delta_y)/c we cab get the depth of each pixel on the polygon
                    """
                    face_norm_local = self.normal_vector(face_points_rendered)
                    # Normalizing the cross product is unnecessary
                    #cp_magnitude = math.sqrt(a**2+b**2+c**2)
                    #a,b,c = [[a,b,c][i]/abs(cp_magnitude/50) for i in range(3)]

                    """
                    Back-face Culling
                    If the face's normal and the camera vector are facing the same direction then the dot product will be >1
                    if the face's normal and the camera vector are perpendicular, then the dot product will be 0
                    In both cases above, the face will not be seen by the camera (for closed objects) so the face can be discarded
                    """
                    if vec_dot_product(face_norm_local,[0,0,1]) >= 0:
                        continue

                    if not self.do_depth_test:
                        pygame.draw.polygon(screen, col, [face_points_rendered[i][:2] for i in range(3)])
                    else:
                        self.depth_test(self.gamescreen, face_points_rendered, face_norm_local, col)

    def normal_vector(self, face, normalize=False):
        """
        Input:  A list of 3d points forming a face (only the first 3 points will be used)
        Output: A 3d normal vector

        Method:
        The normal vector of a face can be found by getting the cross product of two vectors with the same origin
        """
        vec1 = [face[1][i]-face[0][i] for i in range(3)]
        vec2 = [face[2][i]-face[0][i] for i in range(3)]
        nv = vec_cross_product(vec1,vec2)
        if normalize:
            magnitude = math.sqrt(nv[0]**2+nv[1]**2+nv[2]**2)
            nv = [nv[i]/magnitude for i in range(3)]
        return nv

    def sun_lighting(self, sun_dir, face_norm, face_col):
        """
        Input:  sun_dir is a normalized 3d vector
                face_norm is a normalized 3d vector
                face_col is the face's original color

        Output: color: (0-255,0-255,0-255)
        """
        ang = -vec_dot_product(sun_dir, face_norm)
        if ang < 0: ang = 0
        col = [n*ang if n*ang <= 255 else 255 for n in face_col]
        return col

    def depth_test(self, screen, face_points, face_norm, face_col):
        """
        Method for depth testing:
        1) All z-values in the depth buffer should be set to infinity (0 is treated as infinity)
        2) Each polygon has its z-value at each pixel checked against the corresponding z-value in the depth buffer
        3) If the z-value of the polygon is less than the z-value in the depth buffer, the pixel of the polygon is
        drawn onto the gamesurface. Otherwise, the pixel is discarded
        """
        a,b,c = face_norm

        """
        Figure out the pixels the polygon occupies
        Only works for triangles
        """
        face_points.sort(key=lambda x:x[1])
        slopes = []
        for i in range(3):
            prev_i = i-1 if i else 2
            d_x = face_points[i][0]-face_points[prev_i][0]
            if d_x == 0:
                slopes.append("inf")
                continue
            d_y = face_points[i][1]-face_points[prev_i][1]
            slopes.append(d_y/d_x)

        p2_side = face_points[1][0] > x_val(face_points[1][1], face_points[0], slopes[0])
        y_lower = face_points[0][1]
        y_upper = face_points[2][1]
        if y_lower < 0: y_lower = 0
        if y_upper >= self.gameviewport[1]: y_upper = self.gameviewport[1]-1
        for y in range(y_lower, y_upper):
            if y < face_points[1][1]:
                other_side = x_val(y, face_points[0], slopes[1])
                # If the slope of the 2nd line is 0, then it can't be used to figure out the other
                # side. However, if the slope is 0 that means the other unused line can be used
                # instead. Because the 1st line is always used, the other unused line is the 3rd line
                if other_side is False: x_val(y, face_points[2], slopes[2])
            else:
                # Same as above but with 2nd and 3rd lines reversed
                other_side = x_val(y, face_points[2], slopes[2])
                if other_side is False: x_val(y, face_points[0], slopes[1])

            if p2_side:
                x_start = math.floor(x_val(y, face_points[0], slopes[0]))
                x_end = math.ceil(other_side)
            else:
                x_end = math.ceil(x_val(y, face_points[0], slopes[0]))
                x_start = math.floor(other_side)

            if x_start < 0: x_start = 0
            if x_end >= self.gameviewport[0]: x_end = self.gameviewport[0]-1
            for x in range(x_start, x_end):
                d_x = x-face_points[0][0]
                d_y = y-face_points[0][1]


                z = face_points[0][2]-(a*d_x + b*d_y)/c
                # The following 4 commented lines would shade the object based on its distance to the camera if uncommented
                #z_t = z
                #if z_t > 255: z_t=255
                #elif z_t < 0: z_t=0
                #col = [z_t]*3
                if False:
                    screen.set_at([x,y], face_col)
                    self.depth_buffer[y][x] = z
                    #continue

                elif z <= self.depth_buffer[y][x] or self.depth_buffer[y][x] == 0:
                    screen.set_at([x,y], face_col)
                    self.depth_buffer[y][x] = z

    def point_tranformation(self, point):
        #print(self.yaw)
        view_point_dist = dist_between3d(p.pos, point.pos)

        #if view_point_dist < self.nearvis: return False # The object is inside of the eye

        # Translate the point to its position if the player was at 0,0,0 (also convert it into a matrix from a lsit)
        point_trans = [[point.pos[i]-p.pos[i] for i in range(3)]]

        # Rotate the point to its position if the player had a pitch, yaw, and roll of 0
        # Transformation is applied in the order Yaw(Y) Pitch(X) Roll(Z) so to undo it, the opposite must be done
        # It is key to remember that transformations are applied backwards so it all ends up being in the order y,p,r
        point_rot = mat_rot(point_trans, math.radians(p.yaw),   'y')
        point_rot = mat_rot(point_rot,   math.radians(p.pitch), 'x')
        point_rot = mat_rot(point_rot,   math.radians(p.roll),  'z')

        # If the point is behind the camera or at at the same zcoord as the camera it should not be rendered
        # If a point is in front of the camera but behind the viewing plane it will be rendered (but it will be huge)

        if point_rot[0][2] <= 0:
            """
            Points behind the camera still need to be rendered so edges and faces can still be drawn when a point is behind the camera
            However, they cannot be rendered normally as the lines that would normally converge at the point end up diverging instead
            so idk what to do
            """
            #real_2d_ratio = point_rot[0][2] / p.nearvis
            #point_2d = [point_rot[0][i] / real_2d_ratio for i in range(2)] # The range is only 2 so the z value is discarded
            #point_2d.append(point_rot[0][2]) # The depth value of the point is needed for depth testing
            return False

        # Because the right triangle made by the point and the camera is similar to the right triangle made to the projected point
        # we can divide the point's coords by z_dist / nearvis (nearvis is the dist of the viewing plane from the camera)
        # to get the points coords on the viewing plane (because all the z values will end up being nearvis, only the x&y values are needed)
        real_2d_ratio = point_rot[0][2] / p.nearvis
        point_2d = [point_rot[0][i] / real_2d_ratio for i in range(2)] # The range is only 2 so the z value is discarded
        point_2d.append(point_rot[0][2]) # The depth value of the point is needed for depth testing

        return point_2d

    def to_dev_coords(self, coords):
        return [coords[2],coords[0]]

    def text(self, screen, message, pos, size=20, font="rachana", color=(0,0,0)):
        f = pygame.font.SysFont(font, size)
        t = f.render(message, True, color)
        screen.blit(t, pos)

    def key_pressed(self, key):
        try:
            result = self.pressedkeys[key]
        except KeyError:
            return False
        else:
            return result

    def events_check(self):
        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                pressed_key = pygame.key.name(event.key)
                #print(pressed_key)

                # Events that are only called once when the key is pressed
                if pressed_key == '`': # allow the ~ key be used to pause the game and type commands
                    if pygame.event.get_grab():
                        pygame.event.set_grab(False)
                        pygame.mouse.set_visible(True)
                    exec(input(">>> "))

                elif pressed_key == '1':
                    self.running = False

                elif pressed_key == 'escape':
                    if pygame.event.get_grab():
                        pygame.event.set_grab(False)
                        pygame.mouse.set_visible(True)
                    else:
                        pygame.event.set_grab(True)
                        pygame.mouse.set_visible(False)

                # Events that will be called every frame a key is pressed
                # This dict allows those events to figure out which keys are pressed
                else: self.pressedkeys[pressed_key] = True

            elif event.type == pygame.KEYUP:
                self.pressedkeys[pygame.key.name(event.key)] = False


            elif event.type == pygame.MOUSEMOTION:
                if pygame.event.get_grab():
                    if event.rel[0] < 120:
                        p.yaw += event.rel[0]/p.mouse_sensitivity
                        p.pitch -= event.rel[1]/(p.mouse_sensitivity*1.5)

            elif event.type == pygame.QUIT:
                self.running = False

class Camera(Game):
    def __init__(self):
        self.pos = [0,0,-8]
        # Rotation is applied in order: Yaw, Pitch, Roll
        # If this is changed the rendering engine will probably break
        self.yaw = 0 # - is left, + is right, starts pointing east
        self.pitch = 0
        self.roll = 0

        self.view_angle = 60
        self.nearvis = (g.gameviewport[0]*math.cos(math.radians(self.view_angle/2)))/math.sin(math.radians(self.view_angle)) # Dist of the viewing plane
        self.farvis = 840 # Not used rn

        self.move_dir = [0,0]
        self.side_move_dir = [0,0]
        self.speed = 0.13
        self.mouse_sensitivity = 10 # The higher the num, the lower the sensitivity

        self.position_rounding = 6

    def move(self):
        if g.key_pressed("w"):
            self.pos[2] += self.move_dir[0]
            self.pos[0] += self.move_dir[1]
        if g.key_pressed("a"):
            self.pos[2] -= self.side_move_dir[0]
            self.pos[0] -= self.side_move_dir[1]
        if g.key_pressed("s"):
            self.pos[2] -= self.move_dir[0]
            self.pos[0] -= self.move_dir[1]
        if g.key_pressed("d"):
            self.pos[2] += self.side_move_dir[0]
            self.pos[0] += self.side_move_dir[1]

        if g.key_pressed("space"): self.pos[1]      -= self.speed
        if g.key_pressed("left shift"): self.pos[1] += self.speed

        if g.key_pressed("left"): self.yaw -= 1.5
        if g.key_pressed("right"): self.yaw += 1.5

        if g.key_pressed("q"): self.roll -= 1.5
        if g.key_pressed("e"): self.roll += 1.5

        self.pos = [round(self.pos[i], self.position_rounding) for i in range(3)]

        self.yaw  %= 360
        self.roll %= 360
        if self.pitch > 90: self.pitch = 90
        elif self.pitch < -90: self.pitch = -90

    def update(self):
        # coords of the directions the player can move
        self.move_dir = angle_to_coords(self.yaw, h=self.speed, radians=False)
        self.side_move_dir = angle_to_coords(self.yaw+90, h=self.speed, radians=False)

        self.move()

        if g.dev_mode: self.draw()

    def draw(self):
        # Find the endpoints of the rays
        ray1_ep = angle_to_coords(self.yaw-self.view_angle/2, radians=False)
        ray2_ep = angle_to_coords(self.yaw+self.view_angle/2, radians=False)

        # Translate player position so that (0,0) is the middle of the dev screen
        tmp_pos = [round(g.to_dev_coords(self.pos)[i]+g.devviewport[i]/2) for i in range(0,2)]

        pygame.draw.line(g.devscreen, (200,200,0), tmp_pos, [ray1_ep[i]*self.farvis+tmp_pos[i] for i in range(0,2)])
        pygame.draw.line(g.devscreen, (200,200,0), tmp_pos, [ray2_ep[i]*self.farvis+tmp_pos[i] for i in range(0,2)])

        pygame.draw.arc(g.devscreen, (200,200,0),\
                        [tmp_pos[0]-self.nearvis,tmp_pos[1]-self.nearvis,self.nearvis*2,self.nearvis*2],\
                        math.radians(-self.yaw-self.view_angle/2), math.radians(-self.yaw+self.view_angle/2))

        pygame.draw.circle(g.devscreen, (245,0,0), tmp_pos, 2)

class Point:
    def __init__(self, pos):
        self.pos = pos

    def __getitem__(self,i):
        return self.pos[i]

    def __add__(self, other):
        return Point([self.pos[i]+other[i] for i in range(len(self.pos))])

    def __div__(self, other):
        pass#return Point([])

    def draw(self):
        if g.dev_mode:
            tmp_pos = [round(g.to_dev_coords(self.pos)[i]+g.devviewport[i]/2) for i in range(0,2)]
            pygame.draw.circle(g.devscreen, (0,0,245), tmp_pos, 2)

g = Game()
p = Camera()

def x_val(y, point, slope):
    """
    Returns the x value of a line at y
    The line uses point_slope form
    """
    if slope == "inf": return point[0]
    elif slope == 0: return False
    return (y-point[1])/slope + point[0]

def rc():
    return [255]*3#[random.randint(0,255),random.randint(0,255),random.randint(0,255)]


obj_points, obj_edges, obj_faces = open_obj_file("Ray.obj", index=0)
for i in range(len(obj_points)):
    obj_points[i] = Point(obj_points[i])
obj_face_colors = [[255]*3]*len(obj_faces)
#try:
g.mainloop()
#except Exception as e:
#    pygame.quit()
#    print(e)
