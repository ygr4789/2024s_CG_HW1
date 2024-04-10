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
        self.cam_eye = Vec3(20,13,20)
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
        '''
        Uniforms
        '''
        self.view_proj = None
        self.light_dir = Vec3(-10, 12, 8).normalize()
        
        self.objects: list[Object3D] = []
        self.setup()


    def setup(self) -> None:
        self.set_minimum_size(width = 400, height = 300)
        self.set_mouse_visible(True)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        self.calc_matrices()
        
    def calc_matrices(self) -> None:
        # 1. Create a view matrix
        self.view_mat = Mat4.look_at(
            self.cam_eye, target=self.cam_target, up=self.cam_vup)
        # 2. Create a projection matrix 
        # self.proj_mat = Mat4.perspective_projection(
        #     aspect = self.width/self.height, 
        #     z_near=self.z_near, 
        #     z_far=self.z_far, 
        #     fov = self.fov)
        aspect = self.width/self.height
        H = 12; W = H * aspect
        self.proj_mat = Mat4.orthogonal_projection(
            -W/2,W/2,-H/2,H/2,
            z_near=self.z_near, 
            z_far=self.z_far)
        
        # 2. Calc a view_proj matrix
        self.view_proj = self.proj_mat @ self.view_mat

    def on_draw(self) -> None:
        self.clear()
        self.batch.draw()
        
    def on_resize(self, width, height):
        glViewport(0, 0, *self.get_framebuffer_size())
        self.calc_matrices()
        return pyglet.event.EVENT_HANDLED
        
    def add_object(self, object:Object3D):
        '''
        Assign a group for each object
        '''
        object.set_batch(self.batch)
        self.objects.append(object)

    def update(self,dt) -> None:
        for object in self.objects:
            '''
            Update position/orientation in the scene. In the current setting, 
            objects created later rotate faster while positions are not changed.
            '''
            if(object.parent is None):
                object.calc_transform_mat()
                
            object.group.shader_program['view_proj'] = self.view_proj
            object.group.shader_program['light_dir'] = self.light_dir

    def fixed_update(self,dt,mouse) -> None:
        pass
        
    def run(self):
        pyglet.clock.schedule_interval(self.fixed_update, 1/120)
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()