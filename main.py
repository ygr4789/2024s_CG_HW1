import pyglet
from pyglet.math import Mat4, Vec3

from render import RenderWindow
from geometry import *
from control import Control

from object import Object3D

if __name__ == '__main__':
    width = 1280
    height = 720

    # Render window.
    renderer = RenderWindow(width, height, "Hello Pyglet", resizable = True)   
    renderer.set_location(200, 200)

    # Keyboard/Mouse control. Not implemented yet.
    controller = Control(renderer)

    rod = Rod(width=0.2)
    rodObj = Object3D(rod)
    renderer.add_object(rodObj)
    
    # rodObj.set_translation(translate_mat1)

    #draw shapes
    renderer.run()
