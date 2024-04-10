#version 330
in vec4 color;
in vec2 texCoord;
in float useTexture;
in float light;

uniform sampler2D texture;

out vec4 outColor;

void main()
{
    outColor = useTexture > 0.5 ? texture2D(texture, texCoord) : color;
    outColor.xyz *= light;
}