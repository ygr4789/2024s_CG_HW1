from pyglet.math import Mat4, Vec3, Vec4
from geometry.geom import Geometry
import numpy as np
            
class Sphere(Geometry):
    def __init__(self, radius=1, widthSegments=32, heightSegments=16, phiStart=0, phiLength=2 * np.pi, thetaStart=0, thetaLength=np.pi):
        super().__init__()

        self.parameters = {
            'radius': radius,
            'widthSegments': widthSegments,
            'heightSegments': heightSegments,
            'phiStart': phiStart,
            'phiLength': phiLength,
            'thetaStart': thetaStart,
            'thetaLength': thetaLength
        }

        widthSegments = int(max(3, np.floor(widthSegments)))
        heightSegments = int(max(2, np.floor(heightSegments)))

        thetaEnd = min(thetaStart + thetaLength, np.pi)

        self.indices = []
        self.vertices = []
        self.normals = []
        self.uvs = []

        index = 0
        grid = []

        # generate vertices, normals, and uvs
        for iy in range(heightSegments + 1):
            verticesRow = []

            v = iy / heightSegments

            # special case for the poles
            uOffset = 0
            if iy == 0 and thetaStart == 0:
                uOffset = 0.5 / widthSegments
            elif iy == heightSegments and thetaEnd == np.pi:
                uOffset = -0.5 / widthSegments

            for ix in range(widthSegments + 1):
                u = ix / widthSegments

                # vertex
                x = -radius * np.cos(phiStart + u * phiLength) * np.sin(thetaStart + v * thetaLength)
                y = radius * np.cos(thetaStart + v * thetaLength)
                z = radius * np.sin(phiStart + u * phiLength) * np.sin(thetaStart + v * thetaLength)

                self.vertices.extend([x, y, z])

                # normal
                normal = np.array([x, y, z])
                normal /= np.linalg.norm(normal)
                self.normals.extend(normal)

                # uv
                self.uvs.extend([u + uOffset, 1 - v])

                verticesRow.append(index)
                index += 1

            grid.append(verticesRow)

        # indices
        for iy in range(heightSegments):
            for ix in range(widthSegments):
                a = grid[iy][ix + 1]
                b = grid[iy][ix]
                c = grid[iy + 1][ix]
                d = grid[iy + 1][ix + 1]

                if iy != 0 or thetaStart > 0:
                    self.indices.extend([a, b, d])
                if iy != heightSegments - 1 or thetaEnd < np.pi:
                    self.indices.extend([b, c, d])