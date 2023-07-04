import pygame
import random
import sys
import math
from enum import Enum
import neat

width = 1280
height = 720
bg = (255, 255, 255, 255)

score = 0
score_speedup = 100
game_speed = 8.0
skins = ["default", "aqua", "black", "bloody", "cobalt", "gold", "insta",
         "lime", "magenta", "magma", "navy", "neon", "orange", "pinky",
         "purple", "rgb", "silver", "subaru", "sunny", "toxic"]#берет картинки динозавриков
names = ["Флафи", "Фалафель", "Ведьмак", "Лютик", "Пучеглазик", "Слайм", "Шустрый", "Следопыт",
         "Малыш", "Субарик", "Т-Рекс", "Птенец", "Рядовой", "Опытный", "Ветеран", "Геймер",
         "Самурай", "Странник"]# подписывает имена динозаврикам
generation = 0


class DinoState(Enum):# дефолт енум
    RUN = 1
    JUMP = 2


class Dino:
    name = "Carl"# обьявляется набор переменных по умолчанию при создании класса
    jump_power = 10
    cur_jump_power = jump_power
    color = "default"
    sprites = {#задает словарь с ключами ран джумп которые зочем то массивы
        "run": [],
        "jump": []
    }
    image = None
    run_animation_index = [0, 5]
    hitbox = None
    state = DinoState.RUN#стратегия или действие по умолчанию

    def __init__(self, x, y, color="default", name=None):
        self.color = color
        self.load_sprites()#загружает модельки с его цветом
        self.hitbox = pygame.Rect(x, y, self.sprites["run"][0].get_width(), self.sprites["run"][0].get_height())#создается пугейм хитбокс с начальной точкой х у и размерами модельки run 0
        self.image = self.sprites["run"][0]#начальная позиция динозаврика ран 0

        if name is not None:
            self.name = name#если имя не назначено назначет ему имя

    def load_sprites(self):#загружает модельки для прыжка и бега
        self.sprites["jump"].append(pygame.image.load(f"sprites/dino/{self.color}_jump.png"))
        self.sprites["run"].append(pygame.image.load(f"sprites/dino/{self.color}_run1.png"))
        self.sprites["run"].append(pygame.image.load(f"sprites/dino/{self.color}_run2.png"))

    def update(self):
        if self.state == DinoState.RUN:#сравнивает текущую стратегию и вызывает соответствующее действие
            self.run()
        elif self.state == DinoState.JUMP:
            self.jump()

    def run(self):#не разбирая будем считать что оно просто реализовывает движение
        self.sprites["run"][0] = pygame.image.load(f"sprites/dino/{self.color}_run1.png")
        self.sprites["run"][1] = pygame.image.load(f"sprites/dino/{self.color}_run2.png")

        self.image = self.sprites["run"][self.run_animation_index[0] // self.run_animation_index[1]]

        self.run_animation_index[0] += 1
        if self.run_animation_index[0] >= self.run_animation_index[1] * 2:
            self.run_animation_index[0] = 0

    def jump(self):#не разбирая будем считать что оно просто реализовывает прыжок
        if self.state == DinoState.JUMP:
            self.hitbox.y -= self.cur_jump_power * (2 * (game_speed / 8))
            self.cur_jump_power -= 0.5 * (game_speed / 8)

            # if self.cur_jump_power <= -self.jump_power:
            #    self.hitbox.y -= self.cur_jump_power * (2 * (game_speed / 8))
            #    self.state = DinoState.RUN
            #    self.cur_jump_power = self.jump_power
            if self.hitbox.y >= height - 170:
                self.hitbox.y = height - 170
                self.state = DinoState.RUN
                self.cur_jump_power = self.jump_power
        else:
            self.state = DinoState.JUMP
            self.image = pygame.image.load(f"sprites/dino/{self.color}_jump.png")
            # self.image = self.sprites["jump"][0]

    def draw(self, scr, fnt=None):#рисует динозавра с его текущим изображением которое обновляется в различных методах а так же на позициях которые берутся из хитбокса
        scr.blit(self.image, (self.hitbox.x, self.hitbox.y))
        #fnt=None
        if fnt is not None:#если передан обьект шрифта, то ну рисует шрифт вобщем это часть кода которая отрисовывает имена над динозавриками в нужном месте
            c_label = fnt.render(self.name.capitalize(), True, (100, 100, 100))
            c_label_rect = c_label.get_rect()
            c_label_rect.center = (self.hitbox.x + 45, self.hitbox.y - 30)
            scr.blit(c_label, c_label_rect)


class Cactus:
    available_types = ["1", "2", "3", "4", "5", "6"]#типы кактусов
    cactus_type = None
    image = None
    hitbox = None
    is_active = True

    def __init__(self, x, y, forced_type=None):
        if forced_type is not None:
            self.cactus_type = forced_type

        self.load_image()#вызывает метод загрузки хитбокса который ниже
        self.hitbox.x = x#х принимает как есть
        #print("work!",self.hitbox.height)
        self.hitbox.y = y - self.hitbox.height  # origin from bottom

    def randomize_cactus(self):#случайным образом выбирает тип кактуса
        self.cactus_type = random.choice(self.available_types)

    def load_image(self):
        if self.cactus_type is None:#если типа кактуса нету то его выберет
            self.randomize_cactus()

        self.image = pygame.image.load(f"sprites/cactus/{self.cactus_type}.png")#картинка какутуса= загружает нужную картинку
        self.hitbox = self.image.get_rect()#хитбокс= размеры картинки, обращаем внимание что хитбокс в пугейме видимо спец вида должен быть
        #содержит х у координаты угла и widh heigt размеры изображения

    def update(self):
        self.hitbox.x -= game_speed#ам сдвигает влево на скорость игры
        if self.hitbox.x < -self.hitbox.width:#если  расположение хитбокса меньше его ширины то кактус более не активен крч если расположение хитбокс кактуса уходит за левую часть экрана
            # remove this cactus
            self.is_active = False

    def draw(self, scr):
        scr.blit(self.image, self.hitbox)#отрисовывает изображение типа pygame.image.load в координаты заданые hitbox , (x y) задает левый верхний угол


def calc_dist(a, b):#вычисляет дистанцию
    dx = a[0] - b[0]
    dy = a[1] - b[1]

    return math.sqrt(dx ** 2 + dy ** 2)


def run_game(genomes, config):
    global game_speed, score, enemies, dinosaurs, generation, score_speedup

    generation += 1
    game_speed = 8.0
    score = 0
    score_speedup = 100
    enemies = [Cactus(width + 300 / random.uniform(0.8, 3), height - 85),
               Cactus(width * 2 + 200 / random.uniform(0.8, 3), height - 85),
               Cactus(width * 3 + 400 / random.uniform(0.8, 3), height - 85)]# задает список препятствий конструктор кактуса принимает координаты где его заспавнить
    dinosaurs = []
    nets = []
    skins_copy = skins[:]#выполняет копирование, : написано именно для создания нового экземпляра
    names_copy = names[:]

    # init genomes
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)#заполняет нейросетями которые будут подключены к динозаврам
        g.fitness = 0  # every genome is not successful at the start

        skin = "default"
        if len(skins_copy):#при очередной итерации цикла берет скин из списка удаляя этот скин
            skin = skins_copy.pop()

        name = "Дино"
        if len(names_copy):#аналогично для имени
            name = names_copy.pop()

        dinosaurs.append(Dino(30, height - 170, skin, name))#в массив динозавнов закидывается динозавр с нужным именем скином и иными параметрами

    # init
    pygame.init()#подготовительная функция вызывается в начале работы с пугаме
    screen = pygame.display.set_mode((width, height))#создание окна с задаными размерами
    clock = pygame.time.Clock()#кажется это как то связано с скоростью игры или фпсом
    road_chunks = [
        [pygame.image.load('sprites/road.png'), [0, height - 100]],
        [pygame.image.load('sprites/road.png'), [2404, height - 100]]
    ]#подгрузка спрайта дороги
    font = pygame.font.SysFont("Roboto Condensed", 30)#загрузка шрифтов всяких там
    score_font = pygame.font.SysFont("Roboto Condensed", 40)
    dname_font = pygame.font.SysFont("Roboto Condensed", 30)
    heading_font = pygame.font.SysFont("Roboto Condensed", 70)

    # dinosaurs = [Dino(30, height-170, "subaru", "Howdy")]

    # the loop
    while True:
        for event in pygame.event.get():#обрабатывает событие закрытия окна игры, наверняка там интерестные иные есть
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # display bg & road
        screen.fill(bg)#очищает экран перед отрисовкой нового кадра
        for road_chunk in road_chunks:
            if road_chunk[1][0] <= -2400:#если чанк ушел за экран, то его координату прибавляют на 2400
                road_chunk[1][0] = road_chunks[len(road_chunks) - 1][1][0] + 2400

                road_chunks[0], road_chunks[1] = road_chunks[1], road_chunks[0]
                break

            road_chunk[1][0] -= game_speed
            screen.blit(road_chunk[0], (road_chunk[1][0], road_chunk[1][1]))#отрисовывает чанки если они угли за экран заного

        # draw dino
        for dino in dinosaurs:
            dino.update()#вызывает действие согласно текущей стратегии у каждого динозавра
            dino.draw(screen, font)#выполняет отрисовку динозавров

        # quit if there is no dinos left
        if len(dinosaurs) == 0:#если динозавры кончились ломает цикл ну и видимо игра запускается заного из функции p.run
            break

        # generate enemies
        if len(enemies) < 3:#если число кактусов меньше трех то создает новый кактус
            enemies.append(Cactus(enemies[len(enemies) - 1].hitbox.x + width / random.uniform(0.8, 3), height - 85))

        # draw enemies
        rem_list = []
        for i, enemy in enumerate(enemies):
            enemy.update()#перемещает кактусы по экрану влево и ставит не актив метку кактус если он улетел за экран
            enemy.draw(screen)

            if not enemy.is_active:# если кактус не активный то он добавляется в лист на удаление и переходит к обработке следующего кактуса
                rem_list.append(i)
                continue
            #если все таки кактус был активным
            for j, dinosaur in enumerate(dinosaurs):
                if dinosaur.hitbox.colliderect(enemy.hitbox):#проверяет на слоткновение динозавр в кактус(по их прямоугольникам) если это так то
                    genomes[j][1].fitness -= 10  # lower fitness (failed) фитнес динозавра с этим номером уменьшается(ну точнее берется номер той нейросети и её геном уменьшается)
                    dinosaurs.pop(j)#удаляется динозавр столкнувшийся с кактусом

                    genomes.pop(j)#удаляется его геном
                    nets.pop(j)#удаляется нейросеть связанная с ним

        for i in rem_list:#Удаление неактивных кактусов
            enemies.pop(i)

            for j, dinosaur in enumerate(dinosaurs):#выжившим динозаврам добавляется 5 фитнеса
                genomes[j][1].fitness += 5  # raise fitness (+5 for every enemy)


        # controls
        for i, dinosaur in enumerate(dinosaurs):#для каждого динозавра
            output = nets[i].activate((dinosaur.hitbox.y,
                                       calc_dist((dinosaur.hitbox.x, dinosaur.hitbox.y), enemies[0].hitbox.midtop),
                                       enemies[0].hitbox.width,
                                       game_speed))#спрашивается выход сети, которой на вход подают положение по y, дистанцию до ближайшего кактуса(центра хитбокса), ширину хитбокса и скорость игры

            if output[0] > 0.5 and dinosaur.state is not DinoState.JUMP:#видимо если выход больше 0.5 я полагаю т.к 2 действия то и выход так же делит и стратегия динозавра не прыжок
                dinosaur.jump()#то динозавр прыгает и уменьшает свой фитнес на 1
                genomes[i][1].fitness -= 1  # every jump lowers the fitness (assuming it's false jump)

        # read user input (jump test)
        # user_input = pygame.key.get_pressed()
        # if user_input[pygame.K_SPACE]:
        #     for dino in dinosaurs:
        #         if not dino.state == DinoState.JUMP:
        #             dino.jump()

        # score & game speed
        score += 0.5 * (game_speed / 4)
        if score > score_speedup:
            score_speedup += 100 * (game_speed / 2)
            game_speed += 200
            print(f"Game speed increased - {game_speed}")

        score_label = score_font.render("Очки: " + str(math.floor(score)), True, (50, 50, 50))
        score_label_rect = score_label.get_rect()
        score_label_rect.center = (width - 100, 50)
        screen.blit(score_label, score_label_rect)

        # display dinosaurs names
        for i, dinosaur in enumerate(dinosaurs):
            dname_label = dname_font.render(dinosaur.name, True, (170, 238, 187))
            dname_label_rect = dname_label.get_rect()
            dname_label_rect.center = (width - 100, 100 + (i * 25))
            screen.blit(dname_label, dname_label_rect)

        # display generation
        label = heading_font.render("Поколение: " + str(generation), True, (0, 72, 186))
        label_rect = label.get_rect()
        label_rect.center = (width / 2, 150)
        screen.blit(label, label_rect)

        # display game speed
        score_label = score_font.render("Скорость: " + str(game_speed / 8) + "x", True, (50, 50, 50))
        score_label_rect = score_label.get_rect()
        score_label_rect.center = (150, 50)
        screen.blit(score_label, score_label_rect)

        # flip & tick
        pygame.display.flip()
        clock.tick(60)  # fixed 60 fps


if __name__ == "__main__":
    # setup config
    config_path = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    # init NEAT
    p = neat.Population(config)

    # run NEAT
    p.run(run_game, 1000)
    #x=Cactus(5,5)
