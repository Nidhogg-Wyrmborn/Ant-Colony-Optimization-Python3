import random
from array import array

import arcade
from arcade.gl import BufferDescription

WINDOW_WIDTH = 1150
WINDOW_HEIGHT = 750
GRAPH_WIDTH = 200
GRAPH_HEIGHT = 120
GRAPH_MARGIN = 5

class MyWindow(arcade.Window):
	def __init__(self):
		super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT,
						'Compute Shader',
						gl_version=(4,3),
						resizable=True)

		self.center_window()

		self.num_balls = 40000

		self.group_x = 256
		self.group_y = 1

		buffer_format = '4f 4x4 4f'

		initial_data = self.gen_initial_data()

		self.ssbo_1 = self.ctx.buffer(data=array('f', initial_data))
		self.ssbo_2 = self.ctx.buffer(reserve=self.ssbo_1.size)


		attributes = ['in_vertex', 'in_color']
		self.vao_1 = self.ctx.geometry(
					[BufferDescription(self.ssbo_1, buffer_format, attributes)],
					mode=self.ctx.POINTS)

		self.vao_2 = self.ctx.geometry(
					[BufferDescription(self.ssbo_2, buffer_format, attributes)],
					mode=self.ctx.POINTS)

		file = open('shaders/compute_shader.glsl')
		compute_shader_source = file.read()
		file = open('shaders/vertex_shader.glsl')
		vertex_shader_source = file.read()
		file = open('shaders/fragment_shader.glsl')
		fragment_shader_source = file.read()
		file = open('shaders/geometry_shader.glsl')
		geometry_shader_source = file.read()

		compute_shader_source = compute_shader_source.replace("COMPUTE_SIZE_X",
																str(self.group_x))
		compute_shader_source = compute_shader_source.replace("COMPUTE_SIZE_Y",
																str(self.group_y))
		self.compute_shader = self.ctx.compute_shader(source=compute_shader_source)

		self.program = self.ctx.program(
			vertex_shader=vertex_shader_source,
			geometry_shader=geometry_shader_source,
			fragment_shader=fragment_shader_source)

		arcade.enable_timings()

		self.perf_graph_list = arcade.SpriteList()

		graph = arcade.PerfGraph(GRAPH_WIDTH, GRAPH_HEIGHT, graph_data="FPS")
		graph.center_x = GRAPH_WIDTH/2
		graph.center_y = GRAPH_HEIGHT/2
		self.perf_graph_list.append(graph)

	def on_draw(self):
		self.clear()

		self.ctx.enable(self.ctx.BLEND)

		self.ssbo_1.bind_to_storage_buffer(binding=0)
		self.ssbo_2.bind_to_storage_buffer(binding=1)

		self.compute_shader.run(group_x=self.group_x, group_y=self.group_y)

		self.vao_2.render(self.program)

		self.ssbo_1, self.ssbo_2 = self.ssbo_2, self.ssbo_1

		self.vao_1, self.vao_2 = self.vao_2, self.vao_1

		self.perf_graph_list.draw()

	def gen_initial_data(self):
		for i in range(self.num_balls):
			yield random.randrange(0, self.width)
			yield random.randrange(0, self.height)
			yield 0.0
			yield 6.0

			yield 0.0
			yield 0.0
			yield 0.0
			yield 0.0

			yield 1.0
			yield 1.0
			yield 1.0
			yield 1.0

app = MyWindow()
arcade.run()