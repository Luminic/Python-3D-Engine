import pygame
from pygame import gfxdraw
pygame.init()

import math
import time

def text(message, pos, screen, size=20, font="rachana", color=(0,0,0)):
    f = pygame.font.SysFont(font, size)
    t = f.render(message, True, color)
    screen.blit(t, pos)

def rectify(rect, normalize=False):
    r = rect[:]
    r[2] = r[2]-r[0]
    r[3] = r[3]-r[1]
    if normalize:
        if r[2] < 0: r[0] += r[2]; r[2] = abs(r[2])
        if r[3] < 0: r[1] += r[3]; r[3] = abs(r[3])
    return r

def point_rect(p,r,coords=True):
    if coords:
        # Untested
        if p[0] >= r[0] and p[0] <= r[2]:
            if p[1] >= r[1] and p[1] <= r[3]:
                return True
    else:
        # Tried and Tested
        if p[0] >= r[0] and p[0] <= r[0]+r[2]:
            if p[1] >= r[1] and p[1] <= r[1]+r[3]:
                return True
    return False

def rect_rect(a, b, coords=True):
    """
    Only works with normalized rects
    """
    if coords:
        # Untested
        if a[0] <= b[2] and b[0] <= a[2] and \
           a[1] <= b[3] and b[1] <= a[3]:
            return True
    else:
        # Tried and Tested
        if a[0] <= b[0]+b[2] and b[0] <= a[0]+a[2] and \
           a[1] <= b[1]+b[3] and b[1] <= a[1]+a[3]:
            return True
    return False

def line_line(a, b, count_overlap=True, point=False, ray=False):
    x1,y1 = a[0]
    x2,y2 = a[1]
    x3,y3 = b[0]
    x4,y4 = b[1]

    d     = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    num1  = (x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)
    num2  = (x1-x2)*(y1-y3) - (y1-y2)*(x1-x3)

    if d == 0:
        if count_overlap:
            return rect_rect(rectify([a[0][0],a[0][1],a[1][0],a[1][1]], normalize=True),\
                             rectify([b[0][0],b[0][1],b[1][0],b[1][1]], normalize=True), coords=False) and \
                             num1 == 0 and num2 == 0
        return False

    # t = dist(poi,a[1]) / len(a)
    t = num1 / d
    u =-num2 / d

    #print(t,u)

    # To make it a ray - line intersection, remove the inequality preventing t from being greater than 1
    if not (t>=0 and u>=0 and u<=1):
        return False
    if not ray and not t<=1: return False
    if not point: return True

    Px = x1+t*(x2-x1)
    Py = y1+t*(y2-y1)

    #print("\nPx: ",Px,"\nPy: ",Py,"\nt: ",t,"\nd:",d)

    if ray: return (Px,Py, t)
    return (Px,Py)

def infhorizline_line(a, b, count_overlap=True):
    """
    returns 0 for no intersection
    returns 1 for an intersection to the left of point a (if the point of intersection is on a, this is the default)
    returns 2 for an intersection to the right of point a
    """
    # Check if b is horizontal
    if b[0][1] == b[1][1]:
        if count_overlap:
            # Not perfect... not used so will do
            if b[0][1] == a[1]:
                if a[0] <= b[0][0]: return 1
                elif a[0] >= b[0][0]: return 2
        return 0

    # Edge case for polygonal collision so the intersection between two lines is only counted once unless it is a local minima or maxima
    # in which case it will be counted two or zero times
    if b[0][1] >= b[1][1]: highb = b[0]; lowb = b[1]
    else: highb = b[1]; lowb = b[0]
    if highb[1] == a[1]:
        if a[0] <= highb[0]: return 1
        else: return 2
    if lowb[1] == a[1]: return 0


    # Check if the points of b are on opposite sides of line a
    if (b[0][1] >= a[1] and b[1][1] <= a[1]) or (b[0][1] <= a[1] and b[1][1] >= a[1]):
        # Check if b is vertical
        if b[0][0] == b[1][0]:
            poi = b[0][0]
        else:
            slope = (b[1][1]-b[0][1]) / (b[1][0]-b[0][0])
            poi = (a[1]-b[0][1])/slope + b[0][0]
        if a[0] <= poi: return 1
        else: return 2
    return 0

def point_polygon(point, polygon):
    # Algorithm works by creating a horizontal line at the y-level of the point to intersect with the lines of the polygon.
    # If the number of intersections on the left (or right) of the polygon is odd, then the point lies within the polygon/
    # If the number of intersections on the left (or right) or the polygon is even, then the point lies outside of the polygon
    if len(polygon) <= 2: return False
    poly = polygon[:] + [polygon[0]]
    line_intersections = [0,0]
    for i in range(len(poly)-1):
        intersect = infhorizline_line(point, [poly[i],poly[i+1]], count_overlap=False)
        if intersect: line_intersections[intersect-1] += 1
    return line_intersections[0]%2 != 0

def dist_between(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

def dist_between3d(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)

#def normal()

# Rotations
def angle_to_coords(angle, h=1, radians=True):
    if not radians: angle=math.radians(angle)
    return [math.cos(angle)*h, math.sin(angle)*h]

def point_rotation(point, angle, pivot_point=[0,0], radians=True):
    if not radians: angle=math.radians(angle)
    s,c = math.sin(angle), math.cos(angle)

    point[0] -= pivot_point[0]
    point[1] -= pivot_point[1]

    (point[0], point[1]) = (point[0]*c-point[1]*s, point[0]*s+point[1]*c)

    point[0] += pivot_point[0]
    point[1] += pivot_point[1]

    return point

def polygon_rotation(polygon, angle, pivot_point=[0,0], radians=True):
    if not radians: angle=math.radians(angle)
    return [point_rotation(p, angle, pivot_point) for p in polygon]

def angle_between(p1,p2, radians=True):
    angle = 0
    x = p2[0]-p1[0]
    y = p2[1]-p1[1]
    h = math.sqrt(x**2+y**2)
    if h==0:
        if radians: return -math.pi
        return 270
    angle = math.asin(y/h)
    if x < 0: angle = math.pi - angle
    if radians: return angle
    return math.degrees(angle)

def between_angles(angle, first_lim, second_lim, radians=True, normalize=False):
    ang = 360
    if radians:
        ang = 2*math.pi
    if normalize:
        angle=angle%ang
        first_lim=first_lim%ang
        second_lim=second_lim%ang

    if second_lim >= angle >= first_lim: return True
    elif angle >= first_lim and first_lim >= second_lim: return True
    elif angle <= second_lim and second_lim <= first_lim: return True
    return False
