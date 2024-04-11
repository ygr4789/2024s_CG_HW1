#version 330
layout(location =0) in vec3 vertices;

// add a view-projection uniform and multiply it by the vertices

uniform mat4 model;
uniform mat4 view_proj;

void main()
{
    vec4 world_pos = model * vec4(vertices, 1.0f);
    gl_Position = view_proj * world_pos; // local->world->vp
}