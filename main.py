import pyglet
from pyglet.window import FPSDisplay, key
import numpy as np
import random
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

game_end = False


game_over_label = pyglet.text.Label('GAME OVER',
                font_name='Times New Roman',
                font_size=45,
                x=window_width/2 - 180, y=window_height/2)
r_to_restart = pyglet.text.Label('R to Restart',
                font_name='Times New Roman',
                font_size=20,
                x=window_width/2 - 80, y=window_height/2 - 40)
#print({game_over_label.width}, "label width")
#game_over_label.anchor_x = game_over_label.width//2
#game_over_label.anchor_y = game_over_label.height//2

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

        self.game_end = False

    def update(self, dt):

        if not self.game_end:
            self.velocity = self.velocity + self.acceleration
            self.velocity = limit_vector(self.max_speed, self.velocity)

            self.position = self.position + self.velocity
            self.image.position = self.position
            self.acceleration = np.array([0, 0])

            if keys[key.W]:
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

        if self.game_end:
            if keys[key.R]:
                main_window.startGame()

    def Boost(self):
        boost_vector = vector_from_angle(self.boost_force, self.image.rotation)
        boost_vector = np.array([boost_vector[0], boost_vector[1]], dtype=np.float64)
        self.velocity = self.velocity + boost_vector

    def Turn(self, direction_multiplier):
        self.image.rotation += 1.4 * direction_multiplier

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

        for asteroid in asteroids:
            if distance(self.position, asteroid.position) < self.image.radius + asteroid.image.radius:
                asteroids.remove(asteroid)


class Asteroid():
    def __init__(self, x, y):
        self.position = np.array([x, y])
        self.velocity = np.array([random.uniform(-1, 1), random.uniform(-1, 1)])

        self.image = pyglet.shapes.Circle(self.position[0], self.position[1], random.uniform(13, 19), color=(80, 255, 80), batch=asteroid_batch)

    def update(self):
        self.position = self.position + self.velocity
        self.image.position = self.position

        if distance(self.position, player.position) < self.image.radius + 5:
            print(game_end)
            player.game_end = True


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.FPS_label = FPSDisplay(self)

        self.asteroid_time = 1.5
        self.asteroid_timer = float(0)

    def on_key_press(self, symbol, modifiers):
        if player.game_end:
            self.startGame()

    def update(self, dt):
        if not player.game_end:
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

            for asteroid in asteroids:
                asteroid.update()

            self.keepInBounds()

            if player.position[0] > self.width:
                player.position[0] = 0
            if player.position[0] < 0:
                player.position[0] = self.width

            if player.position[1] > self.height:
                player.position[1] = 0
            if player.position[1] < 0:
                player.position[1] = self.height

            if self.asteroid_timer > self.asteroid_time:
                self.createAsteroid(1)
                self.asteroid_timer = 0

            self.asteroid_timer += dt

    def on_draw(self):
        self.clear()
        self.FPS_label.draw()

        player_batch.draw()
        asteroid_batch.draw()

        if player.game_end:
            game_over_label.draw()
            r_to_restart.draw()

    def keepInBounds(self):
        for asteroid in asteroids:
            if asteroid.position[0] > self.width + asteroid.image.radius:
                asteroid.position[0] = 0 - asteroid.image.radius
            if asteroid.position[0] < 0 - asteroid.image.radius:
                asteroid.position[0] = self.width + asteroid.image.radius

            if asteroid.position[1] > self.height + asteroid.image.radius:
                asteroid.position[1] = 0 - asteroid.image.radius
            if asteroid.position[1] < 0 - asteroid.image.radius:
                asteroid.position[1] = self.height + asteroid.image.radius

    def createAsteroid(self, num_asteroids):
        for i in range(num_asteroids):
            asteroid_x = random.randint(0, window_width)
            asteroid_y = random.randint(0, window_height)
            while distance(player.position, (asteroid_x, asteroid_y)) < 150:
                asteroid_x = random.randint(0, window_width)
                asteroid_y = random.randint(0, window_height)

            asteroids.append(Asteroid(asteroid_x, asteroid_y))

    def startGame(self):
        player.position[0] = window_width // 2
        player.position[1] = window_height // 2

        for asteroid in asteroids:
            asteroids.remove(asteroid)

        self.createAsteroid(5)

        player.velocity = np.array([0, 0])
        player.game_end = False


if __name__ == "__main__":
    main_window = Window(window_width, window_height, "Python Asteroids", resizable = False)
    main_window.push_handlers(keys)

    player = Player(window_width / 2, window_height / 2, 0.02, 2.5, 8, .65)

    main_window.createAsteroid(5)

    pyglet.clock.schedule_interval(main_window.update, FPS)

    pyglet.app.run()
