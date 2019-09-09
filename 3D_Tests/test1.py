GameVersion = ("Alpha", "0","1","8")

import pygame
pygame.init()

from Hitboxes import *

import math
import random

class Game:
    def __init__(self):
        # Screen Setup
        self.viewport = [0,0,800,600]#1000]
        self.screen = pygame.display.set_mode((self.viewport[2], self.viewport[3]))
        self.screen.fill([120,150,250])
        pygame.display.set_caption('3D Engine (%s %s.%s.%s)' %GameVersion)
        pygame.display.update()

        self.gameviewport = [800,600]
        self.gamescreen = pygame.Surface(self.gameviewport)

        self.devviewport = [800,400]
        self.devscreen = pygame.Surface(self.devviewport)

        self.screen.fill([180,180,180])


        # Game Setup
        self.sunangle = 0


        # Other Setup
        self.running = True
        self.resolution = 160
        self.clock = pygame.time.Clock()
        self.pressedkeys = [] # Keys currently pressed

        pygame.event.set_grab(False) # EXTREME DANGER
        pygame.mouse.set_visible(True)
        self.mousevisible = True


        self.dev = False
        # For creating walls
        self.devline = []
        self.devcursorsnap = False
        self.devshowcoords = False

    def mainloop(self):
        while self.running:
            self.screen.fill([180,180,180])
            self.gamescreen.fill([120,150,250])
            self.devscreen.fill([180,180,180])
            self.key()

            # ==================== Gamescreen ====================

            # Moving the "Sun" & updating the colors of the walls
            self.sunangle = 20#(self.sunangle+1)%360
            for wall in w: wall.update_sunpos(self.sunangle)

            # Floor
            pygame.draw.rect(self.gamescreen, (120,120,120), [0,self.gameviewport[1]/2,self.gameviewport[0],self.gameviewport[1]/2])
            # Walls
            p.rendering(w, resolution = self.resolution)

            # ==================== Devscreen ====================
            r = p.rays(self.resolution,200)
            for ray in r:
                pygame.draw.aaline(self.devscreen, [255,255,50], ray[0], ray[1])
            for i in range(len(w)):
                pygame.draw.aaline(self.devscreen, [0,0,0], w[i].endpoints[0], w[i].endpoints[1])

            text(str(self.clock.get_fps()), [350,100], self.devscreen, 30)

            pygame.draw.aaline(self.screen, [0,0,0], [0,self.viewport[3]/2], [self.viewport[2],self.viewport[3]/2])

            if self.dev:
                pos = pygame.mouse.get_pos()
                if self.devcursorsnap: pos = [round(pygame.mouse.get_pos()[i]/10)*10 for i in [0,1]]
                if self.devshowcoords: text(str(pos[0])+", "+str(pos[1]), [pos[0]+5,pos[1]-5-600], self.devscreen, 8)

                if len(self.devline) == 1:
                    pygame.draw.aaline(self.devscreen, [255,0,0], self.devline[0], [pos[0],pos[1]-self.gameviewport[1]])
                elif len(self.devline) == 2:
                    pygame.draw.aaline(self.devscreen, [255,0,0], self.devline[0], self.devline[1])

                self.screen.blit(self.devscreen, (0,self.gameviewport[1]))

            self.screen.blit(self.gamescreen, (0,0))

            self.events_check()
            self.clock.tick(60)
            pygame.display.update()

        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        self.mousevisible = True
        pygame.quit()

    def key(self):
        self.devcursorsnap = False
        self.devshowcoords = False
        movedir = angle_to_coords(p.angle+90, h=1.5, radians=False)
        sidemovedir = angle_to_coords(p.angle, h=1, radians=False)

        for k in self.pressedkeys:

            if k == "`":
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
                exec(input('>>> '))
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)

            elif k == "w":
                p.location[0] -= movedir[0]
                p.location[1] -= movedir[1]
            elif k == "a":
                p.location[0] -= sidemovedir[0]
                p.location[1] -= sidemovedir[1]
            elif k == "s":
                p.location[0] += movedir[0]
                p.location[1] += movedir[1]
            elif k == "d":
                p.location[0] += sidemovedir[0]
                p.location[1] += sidemovedir[1]

            elif k == "left": p.angle -= 1.5
            elif k == "right": p.angle += 1.5

            elif k == "left ctrl": self.devcursorsnap = True
            elif k == "left shift": self.devshowcoords = True

    def events_check(self):
        for event in pygame.event.get():


            if event.type == pygame.KEYDOWN: # When a key is pressed
                k = pygame.key.name(event.key)
                if k == "escape":
                    self.mousevisible = True
                    pygame.event.set_grab(False)
                    pygame.mouse.set_pos([self.viewport[2]/2,self.viewport[3]/2])
                    if pygame.mouse.set_visible(True):
                        pygame.event.set_grab(True)
                        pygame.mouse.set_visible(False)
                        self.mousevisible = False

                if self.dev:
                    if k == "home": self.devline = []
                    elif k == "backspace" and len(self.devline) >= 1: del(self.devline[-1])
                    elif k == "return":
                        print("Wall([["+str(self.devline[0][0])+","+str(self.devline[0][1])+"],["+str(self.devline[1][0])\
                                            +","+str(self.devline[1][1])+"""]], 10, color="rc")""")
                        w.append(Wall(self.devline, 10, color="rc"))
                        self.devline = []
                self.pressedkeys.append(k)

            elif event.type == pygame.KEYUP: # When a key is unpressed
                try: self.pressedkeys.remove(pygame.key.name(event.key))
                except ValueError: pass

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.dev and event.button == 2 and len(self.devline) < 2:
                    pos = [event.pos[0],event.pos[1]-self.gameviewport[1]]
                    if self.devcursorsnap: pos = [round(pos[i]/10)*10 for i in [0,1]]
                    print(pos)
                    self.devline.append(pos)

            elif event.type == pygame.MOUSEMOTION:
                if self.mousevisible == False:
                    if event.rel[0] < 120: p.angle += event.rel[0]/10
                    #print(event.pos,event.rel, event.buttons)

            elif event.type == pygame.QUIT:
                self.running = False


class Wall:
    def __init__(self, endpoints, height=1, color=(255,255,255)):
        self.endpoints = endpoints
        self.height = height
        self.normal = 0

        if color == "rc": self.color = (0,255,0)#(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        else: self.color = color

        self.normals()

    def normals(self):
        """
        The endpoints of the wall must be entered in CW relative to the location of the camera for the normals to be properly calculated
        """
        tx = self.endpoints[1][0] - self.endpoints[0][0]
        ty = self.endpoints[1][1] - self.endpoints[0][1]
        if tx == 0: angle = 90 * abs(ty)/ty
        else:
            angle = math.degrees(math.atan(ty/tx))
            if ty < 0: angle += 180
            elif ty == 0 and tx > 0: angle += 180
        self.normal = (angle+90)%360
        self.update_sunpos(0)

    def update_sunpos(self, sun_angle):
        a = abs((self.normal-sun_angle+180)%360-180) # Range: [0,180]
        self.color = (a+50,a/4+12,a/4+12)

class Player(Game):
    def __init__(self, location=[200,200], angle=0, spread=60):
        self.location = location
        self.angle = angle
        self.spread = spread

    def rays(self, resolution, multiplier=1):
        r = []
        step = self.spread/resolution
        for i in range(resolution):
            rayangle = self.angle-self.spread/2-90 + step*i
            x = multiplier*math.cos(math.radians(rayangle))
            y = multiplier*math.sin(math.radians(rayangle))
            r.append([self.location,[x+self.location[0],y+self.location[1]]])
        return r

    def rendering(self, objects, resolution=200):
        interactions = [False for i in range(resolution)]

        for i in range(len(objects)):
            r = self.rays(resolution)
            for j in range(len(r)):
                collision = line_line(r[j],objects[i].endpoints,point=True, ray=True)
                if collision:
                    if interactions[j] == False: interactions[j]=[i, collision[2]]
                    elif interactions[j][1] >= collision[2]: interactions[j]=[i, collision[2]]#;print(collision[2])

        # 400x400 screen to work with
        step = g.gameviewport[0]/resolution
        for i in range(len(interactions)):
            if interactions[i]:
                if interactions[i][1] == 0: height = 0
                else: height = objects[interactions[i][0]].height *g.gameviewport[1]  /(interactions[i][1])
                if height > g.gameviewport[1]/2: height = g.gameviewport[1]/2
                pygame.draw.rect(g.gamescreen, objects[interactions[i][0]].color, [step*i,g.gameviewport[1]/2-height,step,height*2])

def text(message, pos, screen, size=20, font="rachana", color=(0,0,0)):
    f = pygame.font.SysFont(font, size)
    t = f.render(message, True, color)
    screen.blit(t, pos)


try:
    g = Game()
    p = Player()
    w = [Wall([[100,100],[300,100]], 10, color="rc"),\
         Wall([[300,300],[100,300]], 10, color="rc"),\
         Wall([[100,300],[100,100]], 10, color="rc"),\
         Wall([[300,100],[300,180]], 10, color="rc"),\
         Wall([[300,180],[310,180]], 10, color="rc"),\
         Wall([[310,180],[310,100]], 10, color="rc"),\
         Wall([[310,100],[510,100]], 10, color="rc"),\
         Wall([[510,100],[510,300]], 10, color="rc"),\
         Wall([[510,300],[310,300]], 10, color="rc"),\
         Wall([[310,300],[310,230]], 10, color="rc"),\
         Wall([[310,230],[300,230]], 10, color="rc"),\
         Wall([[300,230],[300,300]], 10, color="rc")]
    #w = Wall

    g.mainloop()
except Exception as e:
    pygame.event.set_grab(False)
    pygame.mouse.set_visible(True)
    print(e)
