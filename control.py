import pyglet
from pyglet import window, app, shapes
from pyglet.window import mouse,key
from pyglet.math import Mat4, Vec4, Vec3, Vec2



class Control:
    """
    Control class controls keyboard & mouse inputs.
    """
    def __init__(self, window):
        window.on_key_press = self.on_key_press
        window.on_key_release = self.on_key_release
        window.on_mouse_motion = self.on_mouse_motion
        window.on_mouse_drag = self.on_mouse_drag
        window.on_mouse_press = self.on_mouse_press
        window.on_mouse_release = self.on_mouse_release
        window.on_mouse_scroll = self.on_mouse_scroll
        self.window = window
        self.setup()
        
    def __getitem__(self, key):
        return self.data.get(key, False)
    
    def __getattr__(self, name):
        return self.data.get(name, False)

    def setup(self):
        self.data = {
            "cursor": Vec3(),
            "target": Vec3()
        }

    def update(self, vector):
        pass

    def on_key_press(self, symbol, modifier):
        pass
    
    def on_key_release(self, symbol, modifier):
        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def on_mouse_motion(self, x, y, dx, dy):
        self.data["cursor"] = self.intersect(x, y)
        if self[mouse.RIGHT]:
            self.data["target"] = self.data["cursor"]

    def on_mouse_press(self, x, y, button, modifier):
        self.data[button] = True
        if self[mouse.RIGHT]:
            self.data["target"] = self.data["cursor"]

    def on_mouse_release(self, x, y, button, modifier):
        self.data[button] = False

    def on_mouse_drag(self, x, y, dx, dy, button, modifier):
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass
    
    def intersect(self, x, y):
        nx = (x / self.window.width) * 2 - 1
        ny = (y / self.window.height) * 2 - 1
        cursor_norm_coord = Vec4(nx, ny, 0, 1)
        cursor_world_coord = ~(self.window.view_proj) @ cursor_norm_coord
        ray_target = cursor_world_coord.xyz / cursor_world_coord.w
        
        # ray_origin = self.window.cam_eye
        # ray_dir = ray_target - ray_origin
        ray_origin = ray_target
        ray_dir = self.window.cam_target - self.window.cam_eye
        
        plane_normal = Vec3(0, 1, 0)
        t = -ray_origin.dot(plane_normal)/ray_dir.dot(plane_normal)
        intersect = ray_origin + ray_dir * t
        return intersect