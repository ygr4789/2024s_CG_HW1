#version 330
layout(location =0) in vec3 vertices;
layout(location =1) in vec3 normals;
layout(location =2) in vec2 uvs;

out vec2 texCoord;
out float useTexture;
out float light;

// add a view-projection uniform and multiply it by the vertices

uniform vec3 dot_light;
uniform vec3 dir_light;
uniform vec3 cam_eye;

uniform mat4 model;
uniform mat4 view_proj;
uniform float textured;

float ambient = 0.5f;
float shininess = 100;

void main()
{
    vec4 world_pos = model * vec4(vertices, 1.0f);
    gl_Position = view_proj * world_pos; // local->world->vp
    
    vec3 normal = (model * vec4(normals, 0.0f)).xyz;
    vec3 pos_to_light = dot_light - world_pos.xyz;
    vec3 pos_to_eye = cam_eye - world_pos.xyz;
    
    vec3 pos_to_light_dir = normalize(pos_to_light);
    vec3 pos_to_eye_dir = normalize(pos_to_eye);
    vec3 half = normalize(pos_to_eye_dir + pos_to_light_dir);
    
    float light1 = max(dot(normal, dir_light), 0.0f);
    float light2 = max(dot(normal, pos_to_light_dir), 0.0f);
    
    float glare = dot(normal, half);
    float specular = 0.0f;
    if (glare > 0.0f) {
        specular = pow(dot(normal, half), shininess);
    }
    
    light = ambient + light1*0.5 + light2*0.5 + specular;
    
    texCoord = uvs;
    useTexture = textured;
}