from pyglet.math import Mat4, Vec3, Vec4
from geometry.geom import Geometry
import numpy as np

class Cylinder(Geometry):
    def __init__(self, radiusTop=1, radiusBottom=1, height=1, radialSegments=32,
                 heightSegments=1, openEnded=False, thetaStart=0, thetaLength=2 * np.pi):
        super().__init__()
        self.parameters = {
            'radiusTop': radiusTop,
            'radiusBottom': radiusBottom,
            'height': height,
            'radialSegments': radialSegments,
            'heightSegments': heightSegments,
            'openEnded': openEnded,
            'thetaStart': thetaStart,
            'thetaLength': thetaLength
        }

        self.vertices = []
        self.normals = []
        self.uvs = []
        self.indices = []
        self.index = 0
        self.index_array = []
        self.group_start = 0

        self.half_height = height / 2

        self.generate_torso()
        
        if not openEnded:
            if radiusTop > 0:
                self.generate_cap(True)
            if radiusBottom > 0:
                self.generate_cap(False)

        # Convert lists to NumPy arrays
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.normals = np.array(self.normals, dtype=np.float32)
        self.uvs = np.array(self.uvs, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.uint32)

    def generate_torso(self):
        slope = (self.parameters['radiusBottom'] - self.parameters['radiusTop']) / self.parameters['height']

        for y in range(self.parameters['heightSegments'] + 1):
            index_row = []
            v = y / self.parameters['heightSegments']
            radius = v * (self.parameters['radiusBottom'] - self.parameters['radiusTop']) + self.parameters['radiusTop']

            for x in range(self.parameters['radialSegments'] + 1):
                u = x / self.parameters['radialSegments']
                theta = u * self.parameters['thetaLength'] + self.parameters['thetaStart']
                sin_theta = np.sin(theta)
                cos_theta = np.cos(theta)

                # vertex
                vertex = np.array([
                    radius * sin_theta,
                    -v * self.parameters['height'] + self.half_height,
                    radius * cos_theta
                ])
                self.vertices.extend(vertex)

                # normal
                normal = np.array([sin_theta, slope, cos_theta])
                normal /= np.linalg.norm(normal)
                self.normals.extend(normal)

                # uv
                self.uvs.extend([u, 1 - v])

                # save index of vertex in respective row
                index_row.append(self.index)
                self.index += 1

            self.index_array.append(index_row)

        # generate indices
        for x in range(self.parameters['radialSegments']):
            for y in range(self.parameters['heightSegments']):
                a = self.index_array[y][x]
                b = self.index_array[y + 1][x]
                c = self.index_array[y + 1][x + 1]
                d = self.index_array[y][x + 1]

                self.indices.extend([a, b, d])
                self.indices.extend([b, c, d])

        self.group_start += len(self.indices)

    def generate_cap(self, top):
        center_index_start = self.index

        radius = self.parameters['radiusTop'] if top else self.parameters['radiusBottom']
        sign = 1 if top else -1

        for x in range(1, self.parameters['radialSegments'] + 1):
            self.vertices.extend([0, self.half_height * sign, 0])
            self.normals.extend([0, sign, 0])
            self.uvs.extend([0.5, 0.5])
            self.index += 1

        center_index_end = self.index

        for x in range(self.parameters['radialSegments'] + 1):
            u = x / self.parameters['radialSegments']
            theta = u * self.parameters['thetaLength'] + self.parameters['thetaStart']
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)

            # vertex
            vertex = np.array([
                radius * sin_theta,
                self.half_height * sign,
                radius * cos_theta
            ])
            self.vertices.extend(vertex)

            # normal
            self.normals.extend([0, sign, 0])

            # uv
            uv = np.array([
                (cos_theta * 0.5) + 0.5,
                (sin_theta * 0.5 * sign) + 0.5
            ])
            self.uvs.extend(uv)

            self.index += 1

        for x in range(self.parameters['radialSegments']):
            c = center_index_start + x
            i = center_index_end + x

            if top:
                self.indices.extend([i, i + 1, c])
            else:
                self.indices.extend([i + 1, i, c])

        self.group_start += len(self.indices)