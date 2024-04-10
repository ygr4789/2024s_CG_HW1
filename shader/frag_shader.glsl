#version 330
in vec3 normal;
in vec2 texCoord;
in float useTexture;

in vec3 pos_to_light;
in vec3 pos_to_eye;

uniform sampler2D texture;

uniform vec4 color;
uniform mat4 model;
uniform vec3 dir_light;

out vec4 outColor;

float ambient = 0.5f;
float shininess = 100;

void main()
{
    vec3 n = normalize(normal);
    
    
    vec3 pos_to_light_dir = normalize(pos_to_light);
    vec3 pos_to_eye_dir = normalize(pos_to_eye);
    vec3 half = normalize(pos_to_eye_dir + pos_to_light_dir);
    
    float light1 = max(dot(n, dir_light), 0.0f);
    float light2 = max(dot(n, pos_to_light_dir), 0.0f);
    
    float glare = dot(n, half);
    float specular = 0.0f;
    if (glare > 0.0f) {
        specular = pow(dot(n, half), shininess);
    }
    
    float light = ambient + light1*0.5 + light2*0.5 + specular;
    
    outColor = useTexture > 0.5 ? texture2D(texture, texCoord) : color;
    outColor.xyz *= light;
}