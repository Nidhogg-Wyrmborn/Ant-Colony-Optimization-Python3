#version 430

layout (local_size_x = 16, local_size_y = 16) in;

layout (rgba8, location = 0) uniform restrict image2D trailMap;

uniform uint width;
uniform uint height;

uniform float diffusionStrength;
uniform bool evaporateExponentially;
uniform float evaporationStrength;
uniform float minimalAmount;

void main() {
	ivec2 texelPos = ivec2(gl_GlobalInvocationID.xy);
	vec3 texel = imageLoad(trailMap, texelPos).rgb;

	if (texelPos.x >= width || texelPos.y >= height)
		return;

	vec3 blur = vec3(0.0);

	for (int dy = -1; dy <= 1; dy++) {
		for (int dx = -1; dx <= 1; dx++) {
			int x = texelPos.x + dx;
			int y = texelPos.y + dy;

			if (x >= 0 && x < width && y >= 0 && y < height) {
				blur += imageLoad(trailMap, ivec2(x, y)).rgb;
			}
		}
	}

	blur /= 9.0;

	vec3 diffused = mix(texel, blur, diffusionStrength);

	if (evaporateExponentially) {
		diffused *= 1.0 - evaporationStrength;

		diffused = max(vec3(minimalAmount), diffused);
	} else {
		diffused = max(vec3(0.0), diffused - evaporationStrength);
	}

	imageStore(trailMap, texelPos, vec4(diffused, 1.0));
}