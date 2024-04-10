import pyglet
from pyglet.window import mouse,key
from pyglet.math import Mat4, Vec4, Vec3, Vec2

import numpy as np

from render import RenderWindow
from geometry import *

from object import Object3D
from control import Control
from design import RobotBody, RigidSphere

class IK2Link:
    """
    Two link planar manipulator.
    Consider the case where the joint is angled downward.
    """
    def __init__(self, l1, l2):
        self._l1 = l1
        self._l2 = l2
        self._th1 = 0.0
        self._th2 = 0.0
        
    def set_target(self, x:float, y:float):
        l1 = self._l1
        l2 = self._l2
        r_sqr = x**2 + y**2
        c = ((l1**2+l2**2)-r_sqr)/(2*l1*l2)
        if c>1 or c<-1:
            if r_sqr > (l1+l2)**2:
                self._th1 = np.arctan2(y,x)
                self._th2 = 0.0
            if l2 > np.sqrt(r_sqr) + l1:
                self._th1 = np.pi + np.arctan2(y,x)
                self._th2 = np.pi
            if l1 > np.sqrt(r_sqr) + l2:
                self._th1 = np.arctan2(y,x)
                self._th2 = np.pi
            return
        alpha = np.arccos(c)
        self._th1 = np.arctan2(y,x) + np.arctan2(l2*np.sin(alpha),l1-l2*np.cos(alpha))
        self._th2 = alpha - np.pi
        
    @property
    def th1(self):
        return self._th1
        
    @property
    def th2(self):
        return self._th2

class SecondOrderDynamics:
    def __init__(self, f:float, z:float, r:float, x0) -> None:
        self._k1 = z/(np.pi*f)
        self._k2 = 1/((2*np.pi*f)**2)
        self._k3 = r*z/(2*np.pi*f)
        self._dt_crit = 0.8 * (np.sqrt(4*self._k2+self._k1**2)-self._k1)
        self._xp = x0 # previous input
        self._y = x0 # output position
        self._yd = None # output velocity
        
    def update(self, dt:float, x):
        xd = (x - self._xp) / dt
        if self._yd is None: self._yd = xd
        self._xp = x
        it = int(np.ceil(dt / self._dt_crit))
        dt /= it
        for i in range(it):
            self._y = self._y + self._yd * dt
            self._yd = self._yd + (x + xd*self._k3 - self._y - self._yd*self._k1) * dt/self._k2
            
    @property
    def y(self):
        return self._y
        
    @property
    def yd(self):
        return self._yd

class Engine:
    def __init__(self, renderer: RenderWindow, controller: Control):
        renderer.fixed_update = self.fixed_update
        self.renderer = renderer
        self.controller = controller
        
        self.body_ground_position: Vec3 = Vec3()
        self.body_rotation = 0.0
        self.position_system = SecondOrderDynamics(0.3, 0.5, 0.5, self.body_ground_position)
        self.rotation_system = SecondOrderDynamics(1, 1, 1, self.body_rotation)
        
        self.body_obj: Object3D = None
        self.body_offset = 0.6
        
        self.leg1_objs: list[Object3D] = []
        self.leg2_objs: list[Object3D] = []
        self.leg1_length = 0.7
        self.leg2_length = 1.3
        self.invk = IK2Link(self.leg1_length, self.leg2_length)
        
        self.joint_offset = 1.0
        self.joint_positions: list[Vec3] = [
            Vec3(self.joint_offset/2, 0, self.joint_offset/2),
            Vec3(-self.joint_offset/2, 0, self.joint_offset/2),
            Vec3(-self.joint_offset/2, 0, -self.joint_offset/2),
            Vec3(self.joint_offset/2, 0, -self.joint_offset/2),
        ]
        
        self.stride = 1.2
        self.step_offsets: list[Vec3] = [
            Vec3(self.stride, 0, self.stride),
            Vec3(-self.stride, 0, self.stride),
            Vec3(-self.stride, 0, -self.stride),
            Vec3(self.stride, 0, -self.stride),
        ]
        self.grounded: list[bool] = [True] * 4
        self.step_dists: list[float] = [0] * 4
        self.curr_step_positions: list[Vec3] = self.step_offsets.copy()
        self.target_step_positions: list[Vec3] = self.step_offsets.copy()
        self.step_boundary = 0.7
        self.step_speed = 3.0
        self.avg_end_height = 0.0
        
        self.tracker_obj: Object3D = None
        
        self.setup()
      
    def setup(self):
        body_tex = pyglet.image.load("textures/steel.jpeg").get_texture()
        body_geo = Geometry()
        body_obj = Object3D(body_geo)
        self.body_obj = body_obj
        self.renderer.add_object(body_obj)
        
        # --------------------------- ----- ---------------------------
        self.robot_body = RobotBody(body_obj, self.renderer, body_tex)
        # --------------------------- ----- ---------------------------
        
        for joint_position in self.joint_positions:
            rod = Rod(self.leg1_length, 0.3, 0.4)
            rod_obj = Object3D(rod, body_tex)
            rod_obj.set_position(joint_position)
            self.leg1_objs.append(rod_obj)
            self.renderer.add_object(rod_obj)
            
            body_obj.add_child(rod_obj)
            subrod = Rod(self.leg2_length, 0.3, 0.4)
            subrod_obj = Object3D(subrod, body_tex)
            subrod_obj.set_position(Vec3(self.leg1_length, 0.0, 0.0))
            self.leg2_objs.append(subrod_obj)
            self.renderer.add_object(subrod_obj)
            rod_obj.add_child(subrod_obj)
        
        
        floor_geo = Plane(50, 50, 10, 10)
        floor_tex = pyglet.image.load("textures/floor.jpg").get_texture()
        floor_obj = Object3D(floor_geo, floor_tex)
        floor_obj.set_rotation(Mat4.from_rotation(-np.pi/2, Vec3(1,0,0)))
        self.floor_obj = floor_obj
        self.renderer.add_object(floor_obj)
        
        tracker_geo = Sphere(radius=0.3)
        tracker_obj = Object3D(tracker_geo, color=Vec4(255,0,0,128))
        self.tracker_obj = tracker_obj
        self.renderer.add_object(tracker_obj)
        
    def step_height(self, rem, step):
        h = 0.5
        x = rem/step
        return (x**2)*((x-1)**2)*8*h
        
    def attack(self):
        self.robot_body.attack()
    
    def procedural_animate(self, dt):
        body_T = self.body_obj.translate_mat @ self.body_obj.rotation_mat
        body_rot_y = Mat4.from_rotation(self.body_rotation, Vec3(0,1,0))
        pos_vel = self.position_system.yd
        pos_vel_dir = pos_vel.normalize()
        pos_vel_mag = pos_vel.mag
        
        self.avg_end_height = 0.0
        for i, step_offset in enumerate(self.step_offsets):
            target = self.body_ground_position + (body_rot_y @ Vec4(*(step_offset), 1)).xyz
            target += pos_vel_dir * min(pos_vel_mag * 0.1, 1.0)
            dist = (target - self.curr_step_positions[i]).mag
            end_position = self.curr_step_positions[i]
            
            if self.grounded[i]:
                if dist > self.step_boundary:
                    cross_grounded = True
                    for j, gr in enumerate(self.grounded):
                        if i%2!=j%2 and not gr:
                            cross_grounded = False
                    if cross_grounded:
                        self.target_step_positions[i] = target
                        self.grounded[i] = False
                        self.step_dists[i] = dist
            else:
                rem = self.target_step_positions[i] - self.curr_step_positions[i]
                rem_dist = rem.mag
                step_move_dir = rem.normalize()
                rot_vel_mag = self.rotation_system.yd * step_offset.mag
                velocity = max(np.sqrt(pos_vel_mag**2 + rot_vel_mag**2), 0.3)
                ds = self.step_speed * velocity * dt
                self.curr_step_positions[i] += step_move_dir * ds
                end_position += Vec3(0, self.step_height(rem_dist, self.step_dists[i]), 0)
                self.avg_end_height += end_position.y / 4
                if rem_dist < ds:
                    self.curr_step_positions[i] = self.target_step_positions[i]
                    self.grounded[i] = True
            
            local_joint_position = self.joint_positions[i]
            local_end_position = (~body_T @ Vec4(*(end_position), 1)).xyz
            v = local_end_position - local_joint_position
            
            pi = np.arctan2(-v.z, v.x)
            r = np.hypot(v.x, v.z)
            self.invk.set_target(r, v.y)
            th1 = self.invk.th1
            th2 = self.invk.th2
            
            R1 = Mat4.from_rotation(pi,Vec3(0,1,0))
            R1 = R1.rotate(th1,Vec3(0,0,1))
            R2 = Mat4.from_rotation(th2,Vec3(0,0,1))
            
            self.leg1_objs[i].set_rotation(R1)
            self.leg2_objs[i].set_rotation(R2)
    
    def fixed_update(self, dt):
        input_body_position = self.controller.target
        self.position_system.update(dt, input_body_position)
        output_body_position = self.position_system.y
        self.body_ground_position = output_body_position
        self.body_obj.set_position(output_body_position + Vec3(0, self.body_offset + self.avg_end_height / 2, 0))
        
        input_body_dir = (self.controller.cursor - self.body_ground_position).normalize()
        body_dir = (Mat4.from_rotation(self.body_rotation, Vec3(0,1,0)) @ Vec4(1,0,0,0)).xyz
        input_body_rotation = self.body_rotation + np.arcsin(body_dir.cross(input_body_dir).y)
        self.rotation_system.update(dt, input_body_rotation)
        output_body_rotation = self.rotation_system.y
        self.body_rotation = output_body_rotation
        
        pos_vel_mag = self.position_system.yd.mag
        tilt_angle = 0.3*(min(pos_vel_mag/10, 1))
        tilt_axis = Vec3(0,1,0).cross(self.position_system.yd).normalize()
        tilt_mat = Mat4.from_rotation(tilt_angle, tilt_axis)
        
        body_rot_mat = Mat4.from_rotation(output_body_rotation, Vec3(0,1,0))
        body_rot_mat = tilt_mat @ body_rot_mat
        self.body_obj.set_rotation(body_rot_mat)
        
        self.tracker_obj.set_position(self.controller.cursor)
        
        for obj in RigidSphere.obj_list:
            obj.update(dt)
        
        for cmd in self.controller.command_queue:
            try:
                getattr(self, cmd)()
            except:
                print("Unknown Command")
            self.controller.command_queue = []
        
        self.procedural_animate(dt)