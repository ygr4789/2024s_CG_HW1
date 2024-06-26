import pyglet
from pyglet.math import Mat4, Vec3, Vec4

import numpy as np

from object import Object3D
from object_line import ObjectLine
from render import RenderWindow
from ulility import SecondOrderDynamics
from geometry import *

class RobotBody:
    def __init__(self, root:Object3D, renderer:RenderWindow, texture:pyglet.image.Texture):
        # parameters
        support_w = 1.0
        support_h = 0.3
        support_offset = -0.1
        
        col_w = 0.5
        col_h = 0.5
        col_offset = support_offset + col_w/2 + support_h/2
        
        head_s = Vec3(1.6,1.0,1.0)
        head_offset = col_offset + col_h/2 + head_s.y/2
        
        arm_offset = head_s.z/2 + Weapon.scale.z/2 + 0.1
        
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
        eye_obj = Object3D(eye_geo, color=Vec4(128,255,255,128))
        head_obj.add_child(eye_obj)
        renderer.add_object(eye_obj)
        
        self.weapon1 = Weapon(head_obj, renderer, texture)
        self.weapon1.set_position((0,0,-arm_offset))
        
        self.weapon2 = Weapon(head_obj, renderer, texture)
        self.weapon2.set_position((0,0,arm_offset))
    
        self.toggle = False
    
    def attack(self):
        if self.toggle:
            self.weapon1.fire()
        else:
            self.weapon2.fire()
        self.toggle = ~self.toggle
        
    def update(self,dt):
        self.weapon1.update(dt)
        self.weapon2.update(dt)

class Weapon(Object3D):
    scale = Vec3(0.8,0.6,0.4)
    length = 1
    fire_speed = 50
    cooldown = 0.2
    def __init__(self, parent:Object3D, renderer:RenderWindow, texture: pyglet.image.Texture = None, color: Vec4 = Vec4(255,0,0,255)):
        weapon_geo = Cube(scale=Weapon.scale)
        super().__init__(weapon_geo, texture, color)
        parent.add_child(self)
        renderer.add_object(self)
        self.renderer = renderer
        self.system = SecondOrderDynamics(1.0,0.2,1.0,0)
        self.setup()
        
    def setup(self):
        barrel_geo = Cylinder(radiusTop=0.15, radiusBottom=0.12, height=Weapon.length)
        barrel_text = pyglet.image.load("textures/blue.jpg").get_texture()
        barrel_obj = Object3D(barrel_geo, texture=barrel_text)
        barrel_obj.set_position((Weapon.scale.x/2+self.length/2, 0, 0))
        barrel_obj.set_rotation(Mat4.from_rotation(np.pi/2,Vec3(0,0,1)))
        self.add_child(barrel_obj)
        self.renderer.add_object(barrel_obj)
        
    def fire(self):
        muzzle_pos = Vec3(Weapon.scale.x/2+Weapon.length,0,0)
        t = self.group.transform_mat
        x0 = (t @ Vec4(*muzzle_pos,1)).xyz
        y0 = (t @ Vec4(1,0,0,0)).xyz * Weapon.fire_speed
        bullet = Bullet(x0, y0)
        self.renderer.add_object(bullet)
        self.renderer.add_object(bullet.trajectory)
        self.system.yd = 3.0
    
    def update(self, dt):
        self.system.update(dt, 0)
        self.set_rotation(Mat4.from_rotation(self.system.y,Vec3(0,0,1)))

class RigidSphere(Object3D):
    r = 0.12
    g = Vec3(0, -9.8, 0)
    d = 0.01
    instance_list = []
    def __init__(self, x0:Vec3, v0:Vec3):
        rand = np.random.rand(3)
        rand /= np.linalg.norm(rand)
        rand = np.ones(3) - rand*0.3
        rand *= 255
        rand = rand.astype(int)
        color = Vec4(*rand,255)
        
        bullet_geo = Sphere(radius=self.r)
        super().__init__(geometry=bullet_geo, color=color)
        RigidSphere.instance_list.append(self)
        self.set_position(x0)
        self.x:Vec3 = x0
        self.v:Vec3 = v0
        
    def update(self, dt):
        self.x += self.v * dt
        v_mag = self.v.mag
        self.v += self.g * dt - self.v * v_mag**2 * self.d * dt
        if self.x.y < self.r:
            if self.v.y < 0: self.v.y *= -0.8
            self.x.y = self.r
        self.set_position(self.x)
        
    def delete(self):
        RigidSphere.instance_list.remove(self)
        super().delete()
        

class Bullet(RigidSphere):
    dur = 3.0
    def __init__(self, x0: Vec3, v0: Vec3):
        super().__init__(x0, v0)
        self.lifetime = 0
        self.trajectory = ObjectLine([*x0],self.color)
        
    def update(self, dt):
        super().update(dt)
        self.lifetime += dt
        s = self.lifetime / Bullet.dur
        s = 1 - s ** 3
        self.rotation_mat = Mat4().scale(Vec3(s,s,s))
        self.trajectory.vertices.extend(self.x)
        if len(self.trajectory.vertices) > 3 * 20:
            self.trajectory.vertices = self.trajectory.vertices[3:]
        self.trajectory.update()
        if self.lifetime > Bullet.dur:
            self.delete()
            
    def delete(self):
        super().delete()
        self.trajectory.delete()