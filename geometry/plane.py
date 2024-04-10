from pyglet.math import Mat4, Vec3, Vec4
from geometry.geom import Geometry
import numpy as np

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