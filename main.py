import pyglet
from pyglet.window import FPSDisplay, key
import numpy as np
from Functions import distance, normalize_vector, magnitude, get_vector, set_magnitude, limit_vector

window_width = 1280
window_height = 720
FPS = 1/144

pyglet.resource.path = ['res/']
pyglet.resource.reindex()

player_image = pyglet.image.load("triangle.png")
player_image.anchor_X = player_image.height//2
player_image.anchor_y = player_image.width//2

asteroid_batch = pyglet.graphics.Batch()
player_batch = pyglet.graphics.Batch()

w_pressed = False
a_pressed = False
s_pressed = False
d_pressed = False

space_pressed = False

keys = key.KeyStateHandler()


class Player():
    def __init__(self, x, y):
        self.velocity = np.array([0, 0])
        self.position = np.array([x, y])
        self.acceleration = np.array([0, 0])

        self.image = pyglet.sprite.Sprite(player_image, window_width / 2, window_height / 2, batch = player_batch)

    def update(self):
        self.image.position = self.position


class Projectile():
    def __init__(self, x, y, move_vector):
       self.position = np.array([x, y])
       self.velocity = np.array([move_vector[0], move_vector[1]])

       self.image = pyglet.shapes.Circle(self.position[0], self.position[1], 4, color=(100, 190, 100), batch=player_batch)

       self.push_handlers(keys)

    def update(self):
        self.position += self.velocity


class Asteroid():
    def __init__(self):
        self.velocity = np.array([0, 0])


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.FPS_label = FPSDisplay(self)

    def update(self, dt):
        pass

    def on_draw(self):
        self.clear()
        self.FPS_label.draw()

        player_batch.draw()
        asteroid_batch.draw()


if __name__ == "__main__":
    main_window = Window(window_width, window_height, "Python Asteroids", resizable = False)

    player = Player(window_width / 2, window_height / 2)

    pyglet.clock.schedule_interval(main_window.update, FPS)

    pyglet.app.run()
