#version 430

layout(local_size_x=COMPUTE_SIZE_X, local_size_y=COMPUTE_SIZE_Y) in;

struct Ball
{
	vec4 pos;
	vec4 vel;
	vec4 color;
};

layout(std430, binding=0) buffer balls_in
{
	Ball balls[];
} In;

layout(std430, binding=1) buffer balls_out
{
	Ball balls[];
} Out;

void main()
{
	int curBallIndex = int(gl_GlobalInvocationID);

	Ball In_ball = In.balls[curBallIndex];

	vec4 p = In_ball.pos.xyzw;
	vec4 v = In_ball.vel.xyzw;

	p.xy += v.xy;

	for (int i; i < In.balls.length(); i++) {
		float dist = distance(In.balls[i].pos.xyzw.xy, p.xy);
		float distanceSquared = dist * dist;

		float minDistance = 0.02;
		float gravityStrength = 0.3;
		float simulationSpeed = 0.002;
		float force = min(minDistance, gravityStrength/distanceSquared * -simulationSpeed);

		vec2 diff = p.xy - In.balls[i].pos.xyzw.xy;

		vec2 delta_v = diff * force;
		v.xy += delta_v;
	}


	Ball out_ball;
	out_ball.pos.xyzw = p.xyzw;
	out_ball.vel.xyzw = v.xyzw;

	vec4 c = In_ball.color.xyzw;
	out_ball.color.xyzw = c.xyzw;

	Out.balls[curBallIndex] = out_ball;
}