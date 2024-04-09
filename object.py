import pyglet
from pyglet import window, app, shapes
from pyglet.math import Mat4, Vec3, Vec4
import math
from pyglet.gl import *

import shader
from geometry import Geometry


class CustomGroup(pyglet.graphics.Group):
    __totGroup__ = 0
    '''
    To draw multiple 3D shapes in Pyglet, you should make a group for an object.
    '''

    def __init__(self):
        super().__init__(CustomGroup.__totGroup__)
        CustomGroup.__totGroup__ += 1

        '''
        Create shader program for each shape
        '''
        self.shader_program = shader.create_program(
            shader.vertex_source_default, shader.fragment_source_default
        )

        self.transform_mat = Mat4()
        self.indexed_vertices_list = None
        self.shader_program.use()

    def set_state(self):
        self.shader_program.use()
        model = self.transform_mat
        self.shader_program['model'] = model

    def unset_state(self):
        self.shader_program.stop()

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.order == other.order and
                self.parent == other.parent)

    def __hash__(self):
        return hash((self.order))


class Object3D:
    def __init__(self, geometry: Geometry):
        self.group = CustomGroup()
        self.geometry = geometry
        self.parent: Object3D = None
        self.children: list[Object3D] = []
        self.translate_mat: Mat4 = Mat4()
        self.rotation_mat: Mat4 = Mat4()

    def set_batch(self, batch: pyglet.graphics.Batch):
        self.group.indexed_vertices_list = self.group.shader_program.vertex_list_indexed(len(self.geometry.vertices)//3, GL_TRIANGLES,
                                                                                         batch=batch,
                                                                                         group=self.group,
                                                                                         indices=self.geometry.indices,
                                                                                         vertices=(
                                                                                             'f', self.geometry.vertices),
                                                                                         colors=('Bn', self.geometry.colors))

    def set_position(self, position: Vec3):
        self.translate_mat = Mat4.from_translation(vector=position)
        
    def calc_transform_mat(self):
        parent_transform_mat = Mat4()
        if self.parent is not None:
            parent_transform_mat = self.parent.group.transform_mat
        self.group.transform_mat = parent_transform_mat @ self.translate_mat @ self.rotation_mat
        for child in self.children:
            child.calc_transform_mat()
