# Напишите игру, в которой на персонаж, управляемый игроком с помощью мыши, сверху
# будут падать какие-нибудь тяжелые объекты, а он должен будет уворачиваться.

from superwires import games, color
import random

games.init(screen_width=480, screen_height=640, fps=50)


class GameObject(object):
    score = games.Text(value=0, size=25, color=color.red, top=5, right=games.screen.width - 10, is_collideable=False)
    games.screen.add(score)

    def __init__(self):
        player = Player()
        games.screen.add(player)
        wind_element = Wind(1)
        games.screen.add(wind_element)


class Wind(games.Sprite):
    WIND1, WIND2, WIND3 = 1, 2, 3
    images = {WIND1: games.load_image("wind1.png"),
              WIND2: games.load_image("wind2.png"),
              WIND3: games.load_image("wind3.png")}

    time_to_spawn = 10

    def __init__(self, wind_type):
        super(Wind, self).__init__(image=Wind.images[wind_type],
                                   y=0,
                                   x=random.randint(0, 639),
                                   dy=random.choice([1, 2, 3]),
                                   is_collideable=False)

    def update(self):
        self.time_to_spawn -= 1
        if self.time_to_spawn == 0:
            wind_type = random.choice([Wind.WIND1, Wind.WIND2, Wind.WIND3])
            new_wind_element = Wind(wind_type=wind_type)
            games.screen.add(new_wind_element)
        if self.y >= games.screen.height:
            self.destroy()


class Asteroid(games.Sprite):
    TYPE1, TYPE2, TYPE3, TYPE4 = 1, 2, 3, 4
    images = {TYPE1: games.load_image("asteroid1.png"),
              TYPE2: games.load_image("asteroid2.png"),
              TYPE3: games.load_image("asteroid3.png"),
              TYPE4: games.load_image("asteroid4.png")}

    def __init__(self, ast_type):
        super(Asteroid, self).__init__(image=Asteroid.images[ast_type],
                                       x=random.randint(0, 639),
                                       y=0,
                                       dy=random.randint(1, 3),
                                       is_collideable=True)

    def update(self):
        if self.top >= games.screen.height:
            self.destroy()

    def handle_hit(self):
        self.destroy()
        GameObject.score.value += 10

    def receive_upgrade(self):
        return


class Upgrade(games.Sprite):
    image = games.load_image("missle1.png", transparent=True)

    def __init__(self):
        x_pos = random.randint(0, 639)
        y_speed = 1
        super(Upgrade, self).__init__(image=Upgrade.image,
                                      x=x_pos,
                                      y=0,
                                      dy=y_speed,
                                      is_collideable=True)

    def update(self):
        if self.top >= games.screen.height:
            self.destroy()
        self.check_upgrade()

    def handle_hit(self):
        return

    def check_upgrade(self):
        for upgrade_object in self.overlapping_sprites:
            upgrade_object.receive_upgrade()
            self.destroy()


class Player(games.Sprite):
    image = games.load_image("spaceShips_001.png", transparent=True)

    def __init__(self):
        super(Player, self).__init__(image=Player.image,
                                     x=games.screen.width/2,
                                     y=games.screen.height/2,
                                     is_collideable=True)
        self.reload_timer = 0
        self.time_to_spawn_asteroid = 50
        self.last_upgrade = 0

    def update(self):
        """ Move to mouse x position. """
        self.x = games.mouse.x
        self.y = games.mouse.y

        if self.reload_timer > 0:
            self.reload_timer -= 1

        if self.x < 0:
            self.x = 0

        if self.x > games.screen.width:
            self.x = games.screen.width

        if games.mouse.is_pressed(0):
            self.shoot()

        self.time_to_spawn_asteroid -= 1

        if self.time_to_spawn_asteroid == 0:
            self.time_to_spawn_asteroid = 50
            asteroid_type = random.choice([Asteroid.TYPE1, Asteroid.TYPE2, Asteroid.TYPE3, Asteroid.TYPE4])
            new_asteroid = Asteroid(ast_type=asteroid_type)
            games.screen.add(new_asteroid)

        if GameObject.score.value % 100 == 0 and GameObject.score.value != self.last_upgrade:
            upgrade_object = Upgrade()
            self.last_upgrade = GameObject.score.value
            games.screen.add(upgrade_object)
            GameObject.score.value += 50

    def shoot(self):
        if self.reload_timer == 0:
            shot = Missle(self.x, self.y - 55)
            self.reload_timer = 50
            games.screen.add(shot)
            print(Missle.speed)

    def handle_hit(self):
        return

    @staticmethod
    def receive_upgrade():
        Missle.speed -= 1
        Missle.image = games.load_image("missle2.png")


class Missle(games.Sprite):
    image = games.load_image("missle1.png")
    speed = -5

    def __init__(self, x, y):
        super(Missle, self).__init__(image=Missle.image,
                                     x=x,
                                     y=y,
                                     dy=Missle.speed,
                                     is_collideable=True)

    def update(self):
        self.check_hit()

    def check_hit(self):
        for space_object in self.overlapping_sprites:
            space_object.handle_hit()
            self.destroy()

    def receive_upgrade(self):
        return


def main():
    games.load_sound("Space_walk.mp3").play()
    space_background = games.load_image("seamless space.PNG", transparent=False)
    games.screen.background = space_background

    games.mouse.is_visible = False

    GameObject()

    games.screen.mainloop()


if __name__ == "__main__":
    main()
