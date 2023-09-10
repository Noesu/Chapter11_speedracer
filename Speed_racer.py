# Напишите игру, в которой на персонаж, управляемый игроком с помощью мыши, сверху
# будут падать какие-нибудь тяжелые объекты, а он должен будет уворачиваться.

from superwires import games, color
import random

games.init(screen_width=512, screen_height=512, fps=50)


class Roadside(games.Sprite):
    image = games.load_image("side_grass.png", transparent=False)
    image.convert()

    def __init__(self, bottom, right):
        super(Roadside, self).__init__(image=Roadside.image, bottom=bottom, right=right, is_collideable=False)


class Road(games.Sprite):
    image = games.load_image("road.png", transparent=False)
    image.convert()

    def __init__(self, bottom):
        super(Road, self).__init__(image=Road.image, bottom=bottom, right=461, is_collideable=False)


class Traffic(games.Sprite):
    image = games.load_image("car.png", transparent=True)
    image.convert()

    def __init__(self):
        traffic_car_position = random.randint(50, 462)
        super(Traffic, self).__init__(image=Traffic.image, bottom=0, x=traffic_car_position, dy=1)

    def handle_collision(self):
        games.load_sound("traffic_car_crash.wav").play()
        self.destroy()


class Player(games.Sprite):
    image = games.load_image("car.png", transparent=True)
    image.convert()

    def __init__(self):
        super(Player, self).__init__(image=Player.image, x=games.mouse.x, y=games.mouse.y, bottom=512)
        self.time_til_spawn = random.randint(100, 1000)
        # self.lives=False
        # self.score=False

        self.lives = games.Text(value=3, size=25, color=color.red, top=5,
                                right=games.screen.width - 30, is_collideable=False)
        games.screen.add(self.lives)

        self.score = games.Text(value=0, size=25, color=color.red, top=25,
                                right=games.screen.width - 30, is_collideable=False)
        games.screen.add(self.score)

    def update(self):
        """ Move to mouse x position. """
        self.x = games.mouse.x
        self.y = games.mouse.y

        if self.left < 0:
            self.left = 0

        if self.right > games.screen.width:
            self.right = games.screen.width

        self.check_spawn_traffic()
        self.check_collision()
        # self.lives.update()

    def check_spawn_traffic(self):
        self.lives = games.Text(value=3, size=25, color=color.red, top=5,
                                right=games.screen.width - 30, is_collideable=False)
        games.screen.add(self.lives)

        self.score = games.Text(value=0, size=25, color=color.red, top=25,
                                right=games.screen.width - 30, is_collideable=False)
        games.screen.add(self.score)

        if self.time_til_spawn > 0:
            self.time_til_spawn -= 1
        else:
            new_traffic_car = Traffic()
            games.screen.add(new_traffic_car)
            self.score.value += 10
            self.score.right = games.screen.width - 10
            self.time_til_spawn = random.randint(100, 1000)

    def check_collision(self):
        for traffic_car in self.overlapping_sprites:
            traffic_car.handle_collision()
            if self.lives.value == 3:
                self.destroy()
                # self.game_over()
                print("Game over. self.lives =", self.lives.value)
            else:
                self.lives.value -= 1
            explode = Explosion(x=self.x, y=self.y)
            games.screen.add(explode)

    # def game_over(self):
    #
    #     game_running = False
        # Roadside.game_over(self=)

        # game_over_screen = games.init(screen_width=512, screen_height=512, fps=50)

        # for i in range(0, 100):
        #     pygame.Surface.fill(i, i, i)

        # image = games.load_image("title0.png", transparent=False)
        # brighten = 128
        # games.screen.add(image)
        # image.fill((brighten, brighten, brighten), special_flags=games.pygame.BLEND_RGB_ADD)


class Explosion(games.Animation):
    images = ["car1-1.png", "car1-2.png", "car1-3.png", "car1-4.png", "car1-5.png"]

    def __init__(self, x, y):
        super(Explosion, self).__init__(images=Explosion.images,
                                        x=x,
                                        y=y,
                                        n_repeats=1,
                                        repeat_interval=10,
                                        is_collideable=False)


def main():
    games.mouse.is_visible = False
    rs_left = Roadside(bottom=511, right=49)
    rs_right = Roadside(bottom=511, right=511)
    road = Road(bottom=511)
    traffic_car = Traffic()
    player = Player()
    # score = 0
    # score = games.Text(value=score, size=25, color=color.red, top=5,
    #                    right=games.screen.width - 30, is_collideable=False)
    # games.screen.add(score)

    games.screen.add(rs_left)
    games.screen.add(rs_right)
    games.screen.add(road)
    games.screen.add(traffic_car)
    games.screen.add(player)
    games.screen.mainloop()


if __name__ == "__main__":
    main()
