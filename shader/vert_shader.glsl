#version 330
layout(location =0) in vec3 vertices;
layout(location =1) in vec4 colors;
layout(location =2) in vec3 normals;
layout(location =3) in vec2 uvs;

out vec4 color;
out vec2 texCoord;
out float useTexture;
out float light;

// add a view-projection uniform and multiply it by the vertices
uniform mat4 model;
uniform mat4 view_proj;
uniform vec3 light_dir;
uniform float textured;

float ambient = 0.3f;

void main()
{
    gl_Position = view_proj * model * vec4(vertices, 1.0f); // local->world->vp
    
    light = 1.0f;
    if(length(normals) != 0.0f) {
        vec3 normal = normalize(normals);
        normal = (model * vec4(normal, 0.0f)).xyz;
        light = max(dot(normal, light_dir), 0.0f);
        light += ambient;
    }
    
    color = colors;
    texCoord = uvs;
    useTexture = textured;
}