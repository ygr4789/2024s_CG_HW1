import pyglet
from pyglet import window, app
from pyglet.window import mouse,key

from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.gl import GL_TRIANGLES
from pyglet.math import Mat4, Vec3, Vec4
from pyglet.gl import *

import shader
from object import Object3D


class RenderWindow(pyglet.window.Window):
    '''
    inherits pyglet.window.Window which is the default render window of Pyglet
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch = pyglet.graphics.Batch()
        '''
        View (camera) parameters
        '''
        self.cam_eye = Vec3(0,2,4)
        self.cam_target = Vec3(0,0,0)
        self.cam_vup = Vec3(0,1,0)
        self.view_mat = None
        '''
        Projection parameters
        '''
        self.z_near = 0.1
        self.z_far = 100
        self.fov = 60
        self.proj_mat = None

        self.objects: list[Object3D] = []
        self.setup()

        self.animate = False
        self.mouse = None

    def setup(self) -> None:
        self.set_minimum_size(width = 400, height = 300)
        self.set_mouse_visible(True)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

        # 1. Create a view matrix
        self.view_mat = Mat4.look_at(
            self.cam_eye, target=self.cam_target, up=self.cam_vup)
        
        # 2. Create a projection matrix 
        self.proj_mat = Mat4.perspective_projection(
            aspect = self.width/self.height, 
            z_near=self.z_near, 
            z_far=self.z_far, 
            fov = self.fov)

    def on_draw(self) -> None:
        self.clear()
        self.batch.draw()

    def update(self,dt) -> None:
        view_proj = self.proj_mat @ self.view_mat
        for object in self.objects:
            '''
            Update position/orientation in the scene. In the current setting, 
            objects created later rotate faster while positions are not changed.
            '''
            if(object.parent is None):
                object.calc_transform_mat()
                
            object.group.shader_program['view_proj'] = view_proj
            
        if self.mouse is not None:
            x = self.mouse.x
            y = self.mouse.y
            cursor_norm_coord = Vec4(x, y, 0, 1)
            cursor_world_coord = view_proj.__invert__() @ cursor_norm_coord
            ray_target = cursor_world_coord.__getattr__('xyz') / cursor_world_coord.w
            ray_origin = self.cam_eye
            ray_dir = ray_target - ray_origin
            plane_normal = Vec3(0, 1, 0)
            t = -ray_origin.dot(plane_normal)/ray_dir.dot(plane_normal)
            intersect = ray_origin + ray_dir * t
            self.objects[0].set_position(intersect)

    def on_resize(self, width, height):
        glViewport(0, 0, *self.get_framebuffer_size())
        self.proj_mat = Mat4.perspective_projection(
            aspect = width/height, z_near=self.z_near, z_far=self.z_far, fov = self.fov)
        return pyglet.event.EVENT_HANDLED

    def add_object(self, object:Object3D):
        
        '''
        Assign a group for each object
        '''
        object.set_batch(self.batch)
        self.objects.append(object)
        
    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()

    