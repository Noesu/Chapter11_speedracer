# Напишите игру, в которой на персонаж, управляемый игроком с помощью мыши, сверху
# будут падать какие-нибудь тяжелые объекты, а он должен будет уворачиваться.

from superwires import games, color
import random

games.init(screen_width=480, screen_height=640, fps=50)


class Wind(games.Sprite):
    wind1 = games.load_image("wind4.png", transparent=True)
    wind2 = games.load_image("wind5.png", transparent=True)
    wind3 = games.load_image("wind6.png", transparent=True)
    time_to_spawn = 10

    def __init__(self):
        t = random.randint(1, 3)
        wind_x_pos = random.randint(0, 639)
        wind_y_speed = random.randint(1, 3)
        if t == 1:
            super(Wind, self).__init__(image=self.wind1, y=0, x=wind_x_pos,
                                       dy=wind_y_speed, is_collideable=False)
        if t == 2:
            super(Wind, self).__init__(image=self.wind2, y=0, x=wind_x_pos,
                                       dy=wind_y_speed, is_collideable=False)
        if t == 3:
            super(Wind, self).__init__(image=self.wind3, y=0, x=wind_x_pos,
                                       dy=wind_y_speed, is_collideable=False)

    def update(self):
        self.time_to_spawn -= 1
        if self.time_to_spawn == 0:
            new_element = Wind()
            games.screen.add(new_element)
        if self.y >= games.screen.height:
            self.destroy()


class Asteroid(games.Sprite):
    time_to_spawn = 100
    image = games.load_image("spaceMeteors_r001.png",
                             transparent=True)

    def __init__(self):
        ast_x_pos = random.randint(0, 639)
        ast_y_speed = random.randint(1, 3)
        super(Asteroid, self).__init__(image=Asteroid.image,
                                       x=ast_x_pos,
                                       y=0,
                                       dy=ast_y_speed,
                                       is_collideable=True)

    def update(self):
        if self.top >= games.screen.height:
            self.destroy()
            # Player.score += 10
            # print(Player.score)

    def handle_hit(self):
        self.destroy()


class Player(games.Sprite):
    image = games.load_image("spaceShips_001.png", transparent=True)

    def __init__(self):
        super(Player, self).__init__(image=Player.image,
                                     x=games.mouse.x,
                                     y=games.mouse.y,
                                     is_collideable=True)
        self.reload_timer = 0
        self.time_to_spawn_asteroid = 50
        self.score = games.Text(value=0,
                                size=25,
                                color=color.red,
                                top=5,
                                right=games.screen.width - 10)
        games.screen.add(self.score)

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
        print(self.time_to_spawn_asteroid)
        if self.time_to_spawn_asteroid == 0:
            self.time_to_spawn_asteroid = 50
            new_asteroid = Asteroid()
            games.screen.add(new_asteroid)

    def shoot(self):
        if self.reload_timer == 0:
            shot = Missle(self.x, self.y-55)
            self.reload_timer = 50
            games.screen.add(shot)

    def handle_hit(self):
        return


class Missle(games.Sprite):

    image = games.load_image("spaceMissiles_001.png")
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


def main():
    space_background = games.load_image("seamless space.PNG",
                                        transparent=False)
    games.screen.background = space_background

    games.mouse.is_visible = False

    wind_element = Wind()
    games.screen.add(wind_element)

    asteroid_element = Asteroid()
    games.screen.add(asteroid_element)

    player = Player()
    games.screen.add(player)

    games.screen.mainloop()


if __name__ == "__main__":
    main()
