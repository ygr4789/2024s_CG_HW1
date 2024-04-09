import pyglet
from pyglet.math import Mat4, Vec3

from render import RenderWindow
from geometry import *

from object import Object3D

class Engine:
    def __init__(self, renderer: RenderWindow):
        self.renderer = renderer
        self.__setup__()
      
    def __setup__(self):
        body_geo = Cube(Vec3(1.0, 0.2, 1.0))
        leg_offsets: list[Vec3] = [
            Vec3(0.5, -0.1, 0.5),
            Vec3(-0.5, -0.1, 0.5),
            Vec3(0.5, -0.1, -0.5),
            Vec3(-0.5, -0.1, -0.5)
        ]
        body_obj = Object3D(body_geo)
        self.renderer.add_object(body_obj)
        
        for offset in leg_offsets:
            len = 0.5
            rod = Rod(width=0.07, length=len)
            rod_obj = Object3D(rod)
            rod_obj.set_position(offset)
            self.renderer.add_object(rod_obj)
            body_obj.add_child(rod_obj)
            sublen = 0.3
            subrod = Rod(width=0.05, length=sublen)
            subrod_obj = Object3D(subrod)
            subrod_obj.set_position(Vec3(len, 0.0, 0.0))
            self.renderer.add_object(subrod_obj)
            rod_obj.add_child(subrod_obj)