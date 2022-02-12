import pyglet
from pyglet.window import FPSDisplay, key
import numpy as np
from Functions import distance, normalize_vector, magnitude, get_vector, set_magnitude, limit_vector, vector_from_angle

window_width = 1280
window_height = 720
FPS = 1/144

pyglet.resource.path = ['res/']
pyglet.resource.reindex()

player_image = pyglet.image.load("triangle.png")
player_image.anchor_x = player_image.width//2
player_image.anchor_y = player_image.height//2

asteroid_batch = pyglet.graphics.Batch()
player_batch = pyglet.graphics.Batch()

asteroids = []
projectiles = []

w_pressed = False
a_pressed = False
s_pressed = False
d_pressed = False

space_pressed = False

keys = key.KeyStateHandler()

class Player():
    def __init__(self, x, y, boost_force, max_speed, projectile_speed, shoot_time):
        self.velocity = np.array([0, 0])
        self.position = np.array([x, y])
        self.acceleration = np.array([0, 0], dtype=np.float64)

        self.boost_force = boost_force
        self.max_speed = max_speed
        self.projectile_speed = projectile_speed
        self.shoot_time = shoot_time
        self.shoot_timer = float(0)

        self.image = pyglet.sprite.Sprite(player_image, window_width / 2, window_height / 2, batch = player_batch)

    def update(self, dt):

        self.velocity = self.velocity + self.acceleration
        self.velocity = limit_vector(self.max_speed, self.velocity)

        self.position = self.position + self.velocity
        self.image.position = self.position
        self.acceleration = np.array([0, 0])

        if keys[key.W]:
            print("boosting")
            self.Boost()
        if keys[key.A]:
            self.Turn(-1)
        if keys[key.D]:
            self.Turn(1)
        if keys[key.SPACE]:
            if self.shoot_timer > self.shoot_time:
                self.Shoot()
                self.shoot_timer = 0

        self.shoot_timer += dt

    def Boost(self):
        boost_vector = vector_from_angle(self.boost_force, self.image.rotation)
        boost_vector = np.array([boost_vector[0], boost_vector[1]], dtype=np.float64)
        self.velocity = self.velocity + boost_vector

    def Turn(self, direction_multiplier):
        self.image.rotation += .8 * direction_multiplier

    def Shoot(self):
        projectiles.append(Projectile(self.position[0], self.position[1], vector_from_angle(self.projectile_speed, self.image.rotation)))


class Projectile():
    def __init__(self, x, y, move_vector = (0, 0)):
       self.position = np.array([x, y])
       self.velocity = np.array([move_vector[0], move_vector[1]])

       self.image = pyglet.shapes.Circle(self.position[0], self.position[1], 4, color=(80, 200, 80), batch=player_batch)

    def update(self):
        self.position += self.velocity
        self.image.position = self.position


class Asteroid():
    def __init__(self):
        self.velocity = np.array([0, 0])


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.FPS_label = FPSDisplay(self)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.A:
            player.Turn(-1)
        if symbol == key.D:
            player.Turn(1)
        if symbol == key.SPACE:
            player.Boost()

    def on_key_release(self, symbol, modifiers):
        if symbol == key.A:
            a_pressed = False
        if symbol == key.D:
            d_pressed = True
        if symbol == key.SPACE:
            space_pressed = False

    def update(self, dt):
        player.update(dt)

        for projectile in projectiles:
            projectile.update()

            if projectile.position[0] > self.width:
                projectiles.remove(projectile)
            if projectile.position[0] < 0:
                projectiles.remove(projectile)

            if projectile.position[1] > self.height:
                projectiles.remove(projectile)
            if projectile.position[1] < 0:
                projectiles.remove(projectile)

        self.keepInBounds()

        if player.position[0] > self.width:
            player.position[0] = 0
        if player.position[0] < 0:
            player.position[0] = self.width

        if player.position[1] > self.height:
            player.position[1] = 0
        if player.position[1] < 0:
            player.position[1] = self.height

    def on_draw(self):
        self.clear()
        self.FPS_label.draw()

        player_batch.draw()
        asteroid_batch.draw()

    def keepInBounds(self):
        for asteroid in asteroids:
            if asteroid.position[0] > self.width:
                asteroid.position[0] = 0
            if asteroid.position[0] < 0:
                asteroid.position[0] = self.width

            if asteroid.position[1] > self.height:
                asteroid.position[1] = 0
            if asteroid.position[1] < 0:
                asteroid.position[1] = self.height


if __name__ == "__main__":
    main_window = Window(window_width, window_height, "Python Asteroids", resizable = False)
    main_window.push_handlers(keys)

    player = Player(window_width / 2, window_height / 2, 0.04, 5, 10, .65)

    pyglet.clock.schedule_interval(main_window.update, FPS)

    pyglet.app.run()
