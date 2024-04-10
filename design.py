import pyglet
from pyglet.math import Mat4, Vec3, Vec4

import numpy as np

from object import Object3D
from render import RenderWindow
from geometry import *

class RobotBody:
    def __init__(self, root:Object3D, renderer:RenderWindow, texture:pyglet.image.Texture) -> None:
        # parameters
        support_w = 1.0
        support_h = 0.3
        support_offset = -0.1
        
        col_w = 0.5
        col_h = 0.5
        col_offset = support_offset + col_w/2 + support_h/2
        
        head_s = Vec3(1.6,1.0,1.0)
        head_offset = col_offset + col_h/2 + head_s.y/2
        
        arm_s = Vec3(0.8,0.6,0.3)
        arm_offset = head_s.z/2 + arm_s.z/2 + 0.1
        
        # build
        support_geo = Cube(translate=(0,-support_offset,0),scale=(support_w,support_h,support_w))
        support_obj = Object3D(support_geo, texture)
        support_obj.set_rotation(Mat4.from_rotation(np.pi/4,Vec3(0,1,0)))
        root.add_child(support_obj)
        renderer.add_object(support_obj)
        
        col_geo = Cube(translate=(0,col_offset,0),scale=(col_w,col_h,col_w))
        col_obj = Object3D(col_geo, texture)
        col_obj.set_rotation(Mat4.from_rotation(np.pi/4,Vec3(0,1,0)))
        root.add_child(col_obj)
        renderer.add_object(col_obj)
        
        head_geo = Cube(scale=head_s)
        head_obj = Object3D(head_geo, texture)
        head_obj.set_position(Vec3(0,head_offset,0))
        root.add_child(head_obj)
        renderer.add_object(head_obj)
        
        eye_geo = Cube(translate=(0.55,0.25,0),scale=(0.8, 0.8, 0.4))
        eye_obj = Object3D(eye_geo, color=Vec4(0,255,255,255))
        head_obj.add_child(eye_obj)
        renderer.add_object(eye_obj)
        
        left_armor_geo = Cube(scale=arm_s)
        left_armor_obj = Object3D(left_armor_geo, texture)
        left_armor_obj.set_position((0,0,-arm_offset))
        head_obj.add_child(left_armor_obj)
        renderer.add_object(left_armor_obj)
        
        right_armor_geo = Cube(scale=arm_s)
        right_armor_obj = Object3D(right_armor_geo, texture)
        right_armor_obj.set_position((0,0,arm_offset))
        head_obj.add_child(right_armor_obj)
        renderer.add_object(right_armor_obj)
