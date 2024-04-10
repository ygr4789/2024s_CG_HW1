import pyglet
from pyglet import window, app, shapes
from pyglet.math import Mat4, Vec3, Vec4
import math
from pyglet.gl import *

import shader


class Geometry:
    def __init__(self):
        self.vertices = []
        self.indices = None
        self.normals = None
        self.uvs = None

class Plane(Geometry):
    '''
    default structure of plane
    '''
    def __init__(self, width:float=1.0, height:float=1.0, width_seg:int=1, height_seg:int=1):
        super().__init__()
        
        width_half = width / 2
        height_half = height / 2
        gridX = width_seg
        gridY = height_seg
        gridX1 = gridX + 1
        gridY1 = gridY + 1
        segment_width = width / gridX
        segment_height = height / gridY

        self.vertices = []
        self.normals = []
        self.uvs = []
        
        tmp_vertices = []
        tmp_normals = []

        for iy in range(gridY1):
            y = iy * segment_height - height_half
            for ix in range(gridX1):
                x = ix * segment_width - width_half
                tmp_vertices.append([ x, - y, 0 ])
                tmp_normals.append([ 0, 0, 1 ])

        for iy in range(gridY):
            for ix in range(gridX):
                a = ix + gridX1 * iy
                b = ix + gridX1 * ( iy + 1 )
                c = ( ix + 1 ) + gridX1 * ( iy + 1 )
                d = ( ix + 1 ) + gridX1 * iy
                
                self.vertices.extend(tmp_vertices[a])
                self.vertices.extend(tmp_vertices[b])
                self.vertices.extend(tmp_vertices[d])
                
                self.vertices.extend(tmp_vertices[b])
                self.vertices.extend(tmp_vertices[c])
                self.vertices.extend(tmp_vertices[d])
                
                self.uvs.extend([0, 0])
                self.uvs.extend([0, 1])
                self.uvs.extend([1, 0])
                
                self.uvs.extend([0, 1])
                self.uvs.extend([1, 1])
                self.uvs.extend([1, 0])
        
        cnt = len(self.vertices) // 3
        self.normals = [ 0, 0, 1 ] * cnt

class Cube(Geometry):
    '''
    default structure of cube
    '''
    def __init__(self, scale=Vec3(1.0, 1.0, 1.0), translate=Vec3()):
        super().__init__()

        self.vertices = [
            -0.5, -0.5,  -0.5,
            -0.5,  0.5,  -0.5,
            0.5, -0.5,  -0.5,
            -0.5,  0.5,  -0.5,
            0.5,  0.5,  -0.5,
            0.5, -0.5,  -0.5,

            -0.5, -0.5,   0.5,
            0.5, -0.5,   0.5,
            -0.5,  0.5,   0.5,
            -0.5,  0.5,   0.5,
            0.5, -0.5,   0.5,
            0.5,  0.5,   0.5,

            -0.5,   0.5, -0.5,
            -0.5,   0.5,  0.5,
            0.5,   0.5, -0.5,
            -0.5,   0.5,  0.5,
            0.5,   0.5,  0.5,
            0.5,   0.5, -0.5,

            -0.5,  -0.5, -0.5,
            0.5,  -0.5, -0.5,
            -0.5,  -0.5,  0.5,
            -0.5,  -0.5,  0.5,
            0.5,  -0.5, -0.5,
            0.5,  -0.5,  0.5,

            -0.5,  -0.5, -0.5,
            -0.5,  -0.5,  0.5,
            -0.5,   0.5, -0.5,
            -0.5,  -0.5,  0.5,
            -0.5,   0.5,  0.5,
            -0.5,   0.5, -0.5,

            0.5,  -0.5, -0.5,
            0.5,   0.5, -0.5,
            0.5,  -0.5,  0.5,
            0.5,  -0.5,  0.5,
            0.5,   0.5, -0.5,
            0.5,   0.5,  0.5,
        ]
        
        self.uvs = [
            0, 0,
            0, 1,
            1, 0,
            0, 1,
            1, 1,
            1, 0,
        ] * 6
        
        self.vertices = [scale[idx % 3] * x + translate[idx % 3] for idx,
                         x in enumerate(self.vertices)]

        self.normals = [0.0, 0.0, -1.0] * 6 \
                     + [0.0, 0.0, 1.0] * 6 \
                     + [0.0, 1.0, 0.0] * 6 \
                     + [0.0, -1.0, 0.0] * 6 \
                     + [-1.0, 0.0, 0.0] * 6 \
                     + [1.0, 0.0, 0.0] * 6

class Rod(Cube):
    def __init__(self, l=1.0, t=0.2, w=0.2):
        scale = Vec3(l, t, w)
        translate = Vec3(l/2, 0, 0)
        super().__init__(scale, translate)

class Sphere(Geometry):
    '''
    default structure of sphere
    '''

    def __init__(self, stacks=10, slices=10, scale=1.0):
        super().__init__()
        self.vertices = []
        self.indices = []

        num_triangles = 2 * slices * (stacks - 1)

        for i in range(stacks):
            phi0 = 0.5 * math.pi - (i * math.pi) / stacks
            phi1 = 0.5 * math.pi - ((i + 1) * math.pi) / stacks
            coord_v0 = 1.0 - float(i) / stacks
            coord_v1 = 1.0 - float(i + 1) / stacks

            y0 = scale * math.sin(phi0)
            r0 = scale * math.cos(phi0)
            y1 = scale * math.sin(phi1)
            r1 = scale * math.cos(phi1)
            y2 = y1
            y3 = y0

            for j in range(slices):
                theta0 = (j * 2 * math.pi) / slices
                theta1 = ((j + 1) * 2 * math.pi) / slices
                coord_u0 = float(j) / slices
                coord_u1 = float(j + 1) / slices

                x0 = r0 * math.cos(theta0)
                z0 = r0 * math.sin(-theta0)
                u0 = coord_u0
                v0 = coord_v0
                x1 = r1 * math.cos(theta0)
                z1 = r1 * math.sin(-theta0)
                u1 = coord_u0
                v1 = coord_v1
                x2 = r1 * math.cos(theta1)
                z2 = r1 * math.sin(-theta1)
                u2 = coord_u1
                v2 = coord_v1
                x3 = r0 * math.cos(theta1)
                z3 = r0 * math.sin(-theta1)
                u3 = coord_u1
                v3 = coord_v0

                if (i != stacks - 1):
                    self.vertices.append(x0)
                    self.vertices.append(y0)
                    self.vertices.append(z0)

                    self.vertices.append(x1)
                    self.vertices.append(y1)
                    self.vertices.append(z1)

                    self.vertices.append(x2)
                    self.vertices.append(y2)
                    self.vertices.append(z2)

                if (i != 0):
                    self.vertices.append(x2)
                    self.vertices.append(y2)
                    self.vertices.append(z2)

                    self.vertices.append(x3)
                    self.vertices.append(y3)
                    self.vertices.append(z3)

                    self.vertices.append(x0)
                    self.vertices.append(y0)
                    self.vertices.append(z0)

        for i in range(num_triangles*3):
            self.indices.append(i)
