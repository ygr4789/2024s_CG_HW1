
## Requirements
This is a programming assignmet for **SNU Computer Graphics (4190.410)**.
This code uses [Pyglet](https://github.com/pyglet/pyglet) which is a cross-platform windowing library under Python 3.8+. 
Supported platforms are:

* Windows 7 or later
* Mac OS X 10.3 or later
* Linux, with the following libraries (most recent distributions will have these in a default installation):

## Installation
Pyglet is installable from PyPI:

    pip install --upgrade --user pyglet

You can run the code easily by:

    python3 main.py
    
## Instruction

| Input | Response |
|---|---|
| cursor | The robot looks at your cursor. If you move the cursor to a different location, the robot will rotate to the cursor direction. |
| right click | The robot moves toward the specified location. If the button is pressed, the target point is updated to the cursor's position. |
| left click | The robot fires bullets from its muzzle. Each click fires one bullet alternately left and right. |