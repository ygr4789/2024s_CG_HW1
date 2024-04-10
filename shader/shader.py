from pyglet.graphics.shader import Shader, ShaderProgram

# create vertex and fragment shader sources
vertex_source_default = open('shader/vert_shader.glsl', 'r').read()
fragment_source_default = open('shader/frag_shader.glsl', 'r').read()

def create_program(vs_source, fs_source):
    # compile the vertex and fragment sources to a shader program
    vert_shader = Shader(vs_source, 'vertex')
    frag_shader = Shader(fs_source, 'fragment')
    return ShaderProgram(vert_shader, frag_shader)