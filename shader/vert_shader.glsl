#version 330
layout(location =0) in vec3 vertices;
layout(location =1) in vec3 normals;
layout(location =2) in vec2 uvs;

out vec2 texCoord;
out float useTexture;

out vec3 normal;
out vec3 pos_to_light;
out vec3 pos_to_eye;

// add a view-projection uniform and multiply it by the vertices

uniform vec3 dot_light;
uniform vec3 cam_eye;

uniform mat4 model;
uniform mat4 view_proj;
uniform float textured;

void main()
{
    vec4 world_pos = model * vec4(vertices, 1.0f);
    gl_Position = view_proj * world_pos; // local->world->vp
    
    pos_to_light = dot_light - world_pos.xyz;
    pos_to_eye = cam_eye - world_pos.xyz;
    
    normal = (model * vec4(normals, 0.0f)).xyz;
    
    texCoord = uvs;
    useTexture = textured;
}