#version 330
in vec2 texCoord;
in float useTexture;
in float light;

uniform sampler2D texture;

uniform vec4 color;

out vec4 outColor;


void main()
{
    outColor = useTexture > 0.5 ? texture2D(texture, texCoord) : color;
    outColor.xyz *= light;
}