from pyglet.math import Mat4, Vec3, Vec4
from geometry.geom import Geometry
import numpy as np

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
            phi0 = 0.5 * np.pi - (i * np.pi) / stacks
            phi1 = 0.5 * np.pi - ((i + 1) * np.pi) / stacks
            coord_v0 = 1.0 - float(i) / stacks
            coord_v1 = 1.0 - float(i + 1) / stacks

            y0 = scale * np.sin(phi0)
            r0 = scale * np.cos(phi0)
            y1 = scale * np.sin(phi1)
            r1 = scale * np.cos(phi1)
            y2 = y1
            y3 = y0

            for j in range(slices):
                theta0 = (j * 2 * np.pi) / slices
                theta1 = ((j + 1) * 2 * np.pi) / slices
                coord_u0 = float(j) / slices
                coord_u1 = float(j + 1) / slices

                x0 = r0 * np.cos(theta0)
                z0 = r0 * np.sin(-theta0)
                u0 = coord_u0
                v0 = coord_v0
                x1 = r1 * np.cos(theta0)
                z1 = r1 * np.sin(-theta0)
                u1 = coord_u0
                v1 = coord_v1
                x2 = r1 * np.cos(theta1)
                z2 = r1 * np.sin(-theta1)
                u2 = coord_u1
                v2 = coord_v1
                x3 = r0 * np.cos(theta1)
                z3 = r0 * np.sin(-theta1)
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