# Напишите игру, в которой на персонаж, управляемый игроком с помощью мыши, сверху
# будут падать какие-нибудь тяжелые объекты, а он должен будет уворачиваться.
import pygame.time
from superwires import games, color
import random

games.init(screen_width=480, screen_height=640, fps=50)


class HiScores(object):

    def __init__(self):
        line = 200
        hiscores_title = games.Message(value="HIGH SCORES",
                                       size=80,
                                       color=color.blue,
                                       x=games.screen.width / 2,
                                       y=100,
                                       lifetime=150,
                                       is_collideable=False)
        games.screen.add(hiscores_title)
        player_hiscores = [("ТАНЯ", 999999),
                           ("ЯНА", 1000),
                           ("ПЕТР", 600),
                           ("ИВАН", 500),
                           ("МАРЬЯ", 250)]
        for name, score in player_hiscores:
            player_name = games.Message(value=name,
                                        size=50,
                                        color=color.blue,
                                        x=games.screen.width / 4,
                                        y=line,
                                        lifetime=150,
                                        is_collideable=False)
            games.screen.add(player_name)
            player_score = games.Message(value=score,
                                         size=50,
                                         color=color.blue,
                                         x=games.screen.width * 0.75,
                                         y=line,
                                         lifetime=150,
                                         is_collideable=False)
            games.screen.add(player_score)
            line += 80
        pygame.time.wait(200)
        Game()


class GameTitle(games.Sprite):
    image = games.load_image("title.png", transparent=True)

    def __init__(self):
        super(GameTitle, self).__init__(image=GameTitle.image,
                                        x=games.screen.width / 2,
                                        y=320,
                                        is_collideable=False)
        games.mouse.is_visible = True

    def update(self):
        if self.y <= 100:
            self.destroy()
            HiScores()
        if games.mouse.is_pressed(0) and self.y == 320:
            self.move_title()

    def move_title(self):
        self.dy -= 3


class Game(object):
    score_text = games.Text(value="SCORE",
                            size=25,
                            color=color.red,
                            top=5,
                            right=games.screen.width - 100,
                            is_collideable=False)
    games.screen.add(score_text)
    score = games.Text(value=0,
                       size=25,
                       color=color.red,
                       top=5,
                       right=games.screen.width - 10,
                       is_collideable=False)
    games.screen.add(score)
    defence_text = games.Text(value="DEFENCE",
                              size=25,
                              color=color.red,
                              top=25,
                              right=games.screen.width - 100,
                              is_collideable=False)
    games.screen.add(defence_text)
    laser_text = games.Text(value="LASER CHARGE",
                            size=25,
                            color=color.red,
                            top=45,
                            right=games.screen.width - 100,
                            is_collideable=False)
    games.screen.add(laser_text)
    running = True

    def __init__(self):
        games.mouse.is_visible = False
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
                                   x=random.randint(0, 479),
                                   dy=random.choice([1, 2, 3]),
                                   is_collideable=False)

    def update(self):
        # Instance loop:
        if Game.running:
            self.time_to_spawn -= 1
            if self.time_to_spawn == 0:
                wind_type = random.choice([Wind.WIND1, Wind.WIND2, Wind.WIND3])
                new_wind_element = Wind(wind_type=wind_type)
                games.screen.add(new_wind_element)
            if self.y >= games.screen.height:
                self.destroy()
        else:
            self.destroy()


class Asteroid(games.Sprite):
    TYPE1, TYPE2, TYPE3, TYPE4 = 1, 2, 3, 4
    images = {TYPE1: games.load_image("asteroid1.png"),
              TYPE2: games.load_image("asteroid2.png"),
              TYPE3: games.load_image("asteroid3.png"),
              TYPE4: games.load_image("asteroid4.png")}
    hit_sound = games.load_sound("asteroid_hit1.wav")
    crash_sound = games.load_sound("ast_crash1.wav")
    strength_value = 20
    asteroid_bonus = 10
    object_upgrade = 0

    def __init__(self, ast_type):
        super(Asteroid, self).__init__(image=Asteroid.images[ast_type],
                                       x=random.randint(0, 479),
                                       y=0,
                                       dy=random.randint(1, 3),
                                       is_collideable=True)
        self.strength_value *= ast_type
        self.asteroid_bonus *= ast_type

    def update(self):
        """Instance loop.
        During the game destroying asteroids, flying off the screen and calls
        their collision check with other objects.
        Destroys all asteroids if game stopped"""

        if Game.running:
            if self.top >= games.screen.height:
                self.destroy()
            self.check_collision()
        else:
            self.destroy()

    def check_collision(self):
        """Checks collisions with other objects.
        Sending to every colliding object self strength value and destroying asteroid in case
        this object reporting of taking damage.
        Before destroying spawning explosion animation with same trajectory"""
        for space_object in self.overlapping_sprites:
            collision_confirmed = space_object.handle_collision(self.strength_value)
            if collision_confirmed:
                games.screen.add(AsteroidExplosion(self.x, self.y, self.dy))
                self.destroy()

    @staticmethod
    def receive_upgrade(*upgrade_value):
        """Reports of refusal of upgrade receiving"""
        return False

    def handle_missle_hit(self, missle_power):
        """
        Notifies of taking damage to the collided missle
        In case received missle power is higher than asteroid strength
        - increasing game score on the pre-set asteroid value bonus
        - displaying asteroid value bonus on the asteroid coordinates for 1 second
        - calling asteroid explosion animation with own trajectory
        - playing asteroid explosion sound and destroying asteroid
        In other cases decreasing asteroid strength value on the missle power value
        and playing asteroid hit sound.
        """
        if self.strength_value - missle_power <= 0:
            Game.score.value += self.asteroid_bonus
            score_up = games.Message(value=self.asteroid_bonus,
                                     size=15,
                                     color=color.green,
                                     x=self.x,
                                     y=self.y,
                                     lifetime=50,
                                     is_collideable=False)
            games.screen.add(score_up)
            games.screen.add(AsteroidExplosion(self.x, self.y, self.dy))
            self.crash_sound.play()
            self.destroy()
        else:
            self.strength_value -= missle_power
            self.hit_sound.play()
        return True

    def handle_blast_hit(self, laser_power):
        """
        Notifies of taking damage to the collided laser element
        In case received laser power is higher than asteroid strength
        - increasing game score on the pre-set asteroid value bonus
        - displaying asteroid value bonus on the asteroid coordinates for 1 second
        - calling asteroid explosion animation with own trajectory
        - playing asteroid explosion sound and destroying asteroid
        In other cases decreasing asteroid strength value on the laser power value
        and playing asteroid hit sound.
        """
        if self.strength_value - laser_power <= 0:
            Game.score.value += self.asteroid_bonus
            score_up = games.Message(value=self.asteroid_bonus,
                                     size=15,
                                     color=color.green,
                                     x=self.x,
                                     y=self.y,
                                     lifetime=50,
                                     is_collideable=False)
            games.screen.add(score_up)
            games.screen.add(AsteroidExplosion(self.x, self.y, self.dy))
            self.crash_sound.play()
            self.destroy()
        else:
            self.strength_value -= laser_power
            self.hit_sound.play()
        return True

    def handle_collision(self, strength_value):
        """Reports of refusal of collision with other asteroids"""
        return False


class AsteroidExplosion(games.Animation):
    """Spawns asteroid explosion animation according to received trajectory
    and playing asteroid explosion sound"""
    sound = games.load_sound("ast_crash1.wav")
    images = ['asteroid_crash_1.png',
              'asteroid_crash_2.png',
              'asteroid_crash_3.png',
              'asteroid_crash_4.png',
              'asteroid_crash_5.png',
              'asteroid_crash_6.png']

    def __init__(self, x, y, dy):
        super(AsteroidExplosion, self).__init__(images=AsteroidExplosion.images,
                                                x=x,
                                                y=y,
                                                dy=dy,
                                                repeat_interval=4,
                                                n_repeats=1,
                                                is_collideable=False)
        AsteroidExplosion.sound.play()


class Upgrade(games.Sprite):
    TYPE1, TYPE2, TYPE3, TYPE4 = 1, 2, 3, 4
    images = {TYPE1: games.load_image("upgrade1.png", transparent=True),
              TYPE2: games.load_image("upgrade2.png", transparent=True),
              TYPE3: games.load_image("upgrade3.png", transparent=True),
              TYPE4: games.load_image("upgrade4.png", transparent=True)}
    descriptions = {TYPE1: "MISSLE SPEED UPGRADE",
                    TYPE2: "RECHARGE UPGRADE",
                    TYPE3: "DEFENCE UPGRADE",
                    TYPE4: "LASER"}
    sound = games.load_sound("missle_speed_upgrade.mp3")
    upgrade_value = 1

    def __init__(self, upg_type):
        x_pos = random.randint(5, 474)
        y_speed = 1
        super(Upgrade, self).__init__(image=Upgrade.images[upg_type],
                                      x=x_pos,
                                      y=0,
                                      dy=y_speed,
                                      is_collideable=True)
        self.upgrade_type = upg_type

    def update(self):
        if self.top >= games.screen.height:
            self.destroy()
        self.check_upgrade()

    def check_upgrade(self):
        for space_object in self.overlapping_sprites:
            upgrade_received = space_object.receive_upgrade(self.upgrade_type)
            if upgrade_received:
                upgrade_up = games.Message(value=Upgrade.descriptions[self.upgrade_type],
                                           size=15,
                                           color=color.yellow,
                                           x=self.x,
                                           y=self.y,
                                           lifetime=50,
                                           is_collideable=False)
                games.screen.add(upgrade_up)
                self.sound.play()
                self.destroy()

    def handle_collision(self, *strength):
        return False

    @staticmethod
    def handle_missle_hit(*missle_power):
        return False

    @staticmethod
    def handle_blast_hit(*laser_power):
        return False


class Player(games.Sprite):
    image = games.load_image("spaceShips_001.png", transparent=True)
    defence = 60
    object_upgrade = 0
    reload_timer = 50
    laser_charge = 0
    hit_sound = games.load_sound("player_hit1.wav")

    def __init__(self):
        super(Player, self).__init__(image=Player.image,
                                     x=games.screen.width / 2,
                                     y=games.screen.height / 2,
                                     is_collideable=True)
        self.defence = games.Text(value=self.defence,
                                  size=25,
                                  color=color.red,
                                  top=25,
                                  right=games.screen.width - 10,
                                  is_collideable=False)
        games.screen.add(self.defence)
        self.laser_charge = games.Text(value=self.laser_charge,
                                       size=25,
                                       color=color.red,
                                       top=45,
                                       right=games.screen.width - 10,
                                       is_collideable=False)
        games.screen.add(self.laser_charge)
        self.reload_timer = 50
        self.time_to_spawn_asteroid = 50
        self.last_upgrade = 0

    def update(self):
        # Spaceship orientation
        self.x = games.mouse.x
        self.y = games.mouse.y
        if self.x < 0:
            self.x = 0
        if self.x > games.screen.width:
            self.x = games.screen.width

        # Weapon control
        if self.reload_timer > 0:
            self.reload_timer -= 1
        if games.mouse.is_pressed(0):
            self.launch_missle()
        if games.mouse.is_pressed(2):
            if self.laser_charge.value > 0:
                self.activate_laser()

        # Asteroid generator
        self.time_to_spawn_asteroid -= 1
        if self.time_to_spawn_asteroid == 0:
            self.time_to_spawn_asteroid = 50
            self.spawn_asteroid()

        # Upgrade generator
        if Game.score.value % 100 == 0 and Game.score.value != self.last_upgrade:
            self.last_upgrade = Game.score.value
            self.spawn_upgrade()

    def launch_missle(self):
        if self.reload_timer <= 0:
            shot = Missle(self.x, self.y - 55)
            Missle.sound.play()
            self.reload_timer = 50
            games.screen.add(shot)
            print(Game.running)

    def activate_laser(self):
        laser1 = Laser(self.x - 20, self.y - 55)
        laser2 = Laser(self.x + 20, self.y - 55)
        Laser.sound.play()
        self.laser_charge.value -= 2
        games.screen.add(laser1)
        games.screen.add(laser2)

    def handle_collision(self, asteroid_strength):
        self.defence.value -= 20
        self.hit_sound.play()
        if self.defence.value <= 0:
            self.destroy()
            games.screen.add(PlayerExplosion(self.x, self.y))
            games.screen.add(GameOver())
            Game.running = False
        return True

    def spawn_upgrade(self):
        upgrade_type = random.choice([Upgrade.TYPE1, Upgrade.TYPE2, Upgrade.TYPE3, Upgrade.TYPE4])
        new_upgrade = Upgrade(upg_type=upgrade_type)
        games.screen.add(new_upgrade)

    def spawn_asteroid(self):
        if Game.score.value < 99:
            asteroid_type = Asteroid.TYPE1
        elif Game.score.value in range(100, 199):
            asteroid_type = random.choice([Asteroid.TYPE1, Asteroid.TYPE2])
        elif Game.score.value in range(200, 299):
            asteroid_type = random.choice([Asteroid.TYPE1, Asteroid.TYPE2, Asteroid.TYPE3])
        else:
            asteroid_type = random.choice([Asteroid.TYPE1, Asteroid.TYPE2, Asteroid.TYPE3, Asteroid.TYPE4])
        new_asteroid = Asteroid(ast_type=asteroid_type)
        games.screen.add(new_asteroid)

    @staticmethod
    def handle_missle_hit(*missle_power):
        return False

    @staticmethod
    def handle_blast_hit(*laser_power):
        return False

    def receive_upgrade(self, upgrade_type):
        if upgrade_type == 1:
            Missle.speed -= 1
        if upgrade_type == 2:
            Player.reload_timer *= .9
            self.reload_timer = Player.reload_timer
        if upgrade_type == 3:
            self.defence.value += 10
        if upgrade_type == 4:
            self.laser_charge.value += 100
        return True


class PlayerExplosion(games.Animation):
    crash_sound = games.load_sound("player_crash1.wav")
    images = ['player_crash_1.png',
              'player_crash_2.png',
              'player_crash_3.png',
              'player_crash_4.png',
              'player_crash_5.png',
              'player_crash_6.png']

    def __init__(self, x, y):
        super(PlayerExplosion, self).__init__(images=PlayerExplosion.images,
                                              x=x,
                                              y=y,
                                              repeat_interval=4,
                                              n_repeats=1,
                                              is_collideable=False)
        PlayerExplosion.crash_sound.play()


class Missle(games.Sprite):
    image = games.load_image("upgrade1.png")
    speed = -5
    missle_power = 20
    sound = games.load_sound("shot_missle1.wav")

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
            object_was_hit = space_object.handle_missle_hit(self.missle_power)
            if object_was_hit:
                self.destroy()

    def receive_upgrade(self, *upgrade_value):
        # Can receive upgrade
        return False

    def handle_collision(self, strength_value):
        # Can be destroyed with asteroid
        return False

    def handle_missle_hit(self, *missle_power):
        # Can be destroyed with other missle
        return False

    def handle_blast_hit(self, *laser_power):
        # Can be destroyed with laser
        return False


class Laser(games.Sprite):
    image = games.load_image("upgrade4.png")
    speed = -50
    laser_power = 2
    sound = games.load_sound("shot_laser1.wav")

    def __init__(self, x, y):
        super(Laser, self).__init__(image=Laser.image,
                                    x=x,
                                    y=y,
                                    dy=Laser.speed,
                                    is_collideable=True)

    def update(self):
        self.check_blast()

    def check_blast(self):
        for space_object in self.overlapping_sprites:
            object_was_hit = space_object.handle_blast_hit(self.laser_power)
            if object_was_hit:
                self.destroy()

    def receive_upgrade(self, *upgrade_value):
        return False

    def handle_collision(self, strength_value):
        return False

    def handle_missle_hit(self, *missle_power):
        return False

    def handle_blast_hit(self, *laser_power):
        return False


class GameOver(games.Sprite):
    image = games.load_image("gameover.png", transparent=True)

    def __init__(self):
        super(GameOver, self).__init__(image=GameOver.image,
                                       x=games.screen.width / 2,
                                       bottom=0,
                                       dy=3,
                                       is_collideable=False)
        games.mouse.is_visible = True

    def update(self):
        if self.y >= games.screen.width / 2:
            self.dy = 0
            if games.mouse.is_pressed(0):
                self.destroy()
                hiscore_value = "YOUR SCORE IS " + str(Game.score.value)
                hiscore_text = games.Text(value=hiscore_value,
                                          size=50,
                                          color=color.red,
                                          y=games.screen.height/3,
                                          x=games.screen.width/2,
                                          is_collideable=False)
                games.screen.add(hiscore_text)


def main():
    games.load_sound("Space_walk.mp3").play()
    space_background = games.load_image("seamless space.PNG", transparent=False)
    games.screen.background = space_background

    game_title = GameTitle()
    games.screen.add(game_title)

    games.screen.mainloop()


if __name__ == "__main__":
    main()
