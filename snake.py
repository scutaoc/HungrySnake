# coding=utf-8
import math
import random
import cocos
from cocos.sprite import Sprite

import definition
from dot import Dot


class Snake(cocos.cocosnode.CocosNode):
    # 构造方法，初始化蛇身
    def __init__(self, is_enemy=False):
        super(Snake, self).__init__()
        self.is_dead = False

        self.angle = random.randrange(360)  # 目前角度
        self.angle_dest = self.angle  # 目标角度
        self.color = random.choice(definition.ALL_COLOR) # 随机选择颜色

        if is_enemy:
            self.position = (random.randrange(300, 1300), random.randrange(200, 600))
            if 600 < self.x < 1000:
                self.x += 400
        else:
            self.position = (random.randrange(700, 900), random.randrange(350, 450))
        self.is_enemy = is_enemy
        #头
        self.head = Sprite('assets/img/circle.png', color=self.color)
        self.scale = 1.5
        #两只眼睛构造
        eye = Sprite('assets/img/circle.png')
        eye.y = 5
        eye.scale = 0.5
        eyeball = Sprite('assets/img/circle.png', color=definition.BLACK)
        eyeball.scale = 0.5
        eye.add(eyeball)
        self.head.add(eye)
        eye = Sprite('assets/img/circle.png')
        eye.y = -5
        eye.scale = 0.5
        eyeball = Sprite('assets/img/circle.png', color=definition.BLACK)
        eyeball.scale = 0.5
        eye.add(eyeball)
        self.head.add(eye)
        self.add(self.head)

        self.speed = 150
        #主蛇速度大于bot
        if not is_enemy:
            self.speed = 180
        self.path = [self.position] * 100
        #每帧更新事件注册
        self.schedule(self.update)
        if self.is_enemy:
            #bot的定时ai判断
            self.schedule_interval(self.ai, random.random() * 0.01)
    #添加蛇身
    def add_body(self):
        b = Sprite('assets/img/circle.png', color=self.color)
        b.scale = 1.5
        self.body.append(b)
        if self.x == 0:
            print(self.position)
        b.position = self.position
        self.parent.batch.add(b, 9999 - len(self.body))
    #初始化分数和蛇身长度
    def init_body(self):
        if self.is_enemy:
            self.score = 30
        else:
            self.score = 0
        self.length = 4
        self.body = []
        for i in range(self.length):
            self.add_body()
    #每帧更新函数
    def update(self, dt):
        self.angle = (self.angle + 360) % 360
        arena = self.parent

        if self.is_enemy:
            self.check_crash(arena.snake)

        for s in arena.enemies:
            if s != self and not s.is_dead:
                self.check_crash(s)
        if self.is_dead:
            return
        # 目标方向
        if abs(self.angle - self.angle_dest) < 2:
            self.angle = self.angle_dest
        else:
            if (0 < self.angle - self.angle_dest < 180) or (
                self.angle - self.angle_dest < -180):
                self.angle -= 500 * dt
            else:
                self.angle += 500 * dt

        self.head.rotation = -self.angle
        self.x += math.cos(self.angle * math.pi / 180) * dt * self.speed
        self.y += math.sin(self.angle * math.pi / 180) * dt * self.speed
        self.path.append(self.position)
        #蛇身路径
        lag = int(round(1100.0 / self.speed))
        for i in range(int(self.length)):
            idx = (i + 1) * lag + 1
            self.body[i].position = self.path[-min(idx,len(self.path))]
            if self.body[i].x == 0:
                print(self.body[i].position)
        m_l = max(self.length * lag * 2, 60)
        if len(self.path) > m_l:
            self.path = self.path[int(-m_l * 2):]
    #角度更新
    def update_angle(self, keys):
        # 原版本为四个方向键控制，现改为左右方向键控制
        # x, y = 0, 0
        # if 65361 in keys:  # 左
        #     x -= 1
        # if 65362 in keys:  # 上
        #     y += 1
        # if 65363 in keys:  # 右
        #     x += 1
        # if 65364 in keys:  # 下
        #     y -= 1
        # #转向
        # directs = ((225, 180, 135), (270, None, 90), (315, 0, 45))
        # direct = directs[x + 1][y + 1]
        # if direct is None:
        #     self.angle_dest = self.angle
        # else:
        #     self.angle_dest = direct

        directs = [0, 45, 90, 135, 180, 225, 270, 315]
        if 65361 in keys or 97 in keys:  # 左
            # self.index = (self.index - 1) % 8
            # self.angle_dest = int(directs[self.index])
            self.angle_dest = int((self.angle_dest + 45) % 360 // 45 * 45)
        elif 65363 in keys or 100 in keys:  # 右
            # self.index = (self.index + 1) % 8
            # self.angle_dest = int(directs[self.index])
            self.angle_dest = int((self.angle_dest - 45) % 360 // 45 * 45)
        else:
            pass

    #添加分数
    def add_score(self, s=1):
        if self.is_dead:
            return
        self.score += s
        if self.is_enemy:
            l = (self.score - 6) / 5
        else:
            l = (self.score - 6) / 12
        if l > self.length:
            self.length = l
            self.add_body()
    #bot ai
    def ai(self, dt):
        # 弱鸡版ai，只有两种行动策略，有兴趣的同学可以自行增强
        self.angle_dest = (self.angle_dest + 360) % 360

        if (self.x < 100 and 90 < self.angle_dest < 270) or (
            self.x > definition.WIDTH - 100 and (
                self.angle_dest < 90 or self.angle_dest > 270)
        ): # 即将触碰到左墙壁或右墙壁时，掉头就跑
            self.angle_dest = 180 - self.angle_dest
        elif (self.y < 100 and self.angle_dest > 180) or (
            self.y > definition.HEIGHT - 100 and self.angle_dest < 180
        ): # 即将触碰到上墙壁或下墙壁时，掉头就跑
            self.angle_dest = -self.angle_dest
        else: # 不然就按着原来的方向前进
            arena = self.parent
            self.collision_detect(arena.snake)
            for s in arena.enemies:
                if s != self:
                    self.collision_detect(s)
    
    # 碰撞检测
    def collision_detect(self, other):
        if self.is_dead or other.is_dead:
            return
        for b in other.body:
            d_y = b.y - self.y
            d_x = b.x - self.x
            if abs(d_x) > 200 or abs(d_y) > 200:
                return
            if d_x == 0:
                if d_y > 0:
                    angle = 90
                else:
                    angle = -90
            else:
                angle = math.atan(d_y / d_x) * 180 / math.pi
                if d_x < 0:
                    angle += 180
            angle = (angle + 360) % 360
            if abs(angle - self.angle_dest) < 5:
                self.angle_dest += random.randrange(90, 270) #逃逸
    # 检查是否损坏
    def check_crash(self, other):
        if self.is_dead or other.is_dead:
            return
        # 撞到墙-损坏
        if (self.x < 0 or self.x > definition.WIDTH) or (
            self.y < 0 or self.y > definition.HEIGHT):
            self.crash()
            return
        # 与其他蛇身碰撞-损坏
        for b in other.body:
            dis = math.sqrt((b.x - self.x) ** 2 + (b.y - self.y) ** 2)
            if dis < 24:
                self.crash()
                return

    def crash(self):
        if not self.is_dead:
            self.is_dead = True

            self.unschedule(self.update)
            self.unschedule(self.ai)
            arena = self.parent



            for b in self.body:
                arena.batch.add(Dot(b.position, b.color))
                arena.batch.add(Dot(b.position, b.color))
                arena.batch.remove(b)
            # 从竞技场移除
            arena.remove(self)
            # 再加入一个bot
            arena.add_enemy()
            # 删除path
            del self.path
            # 如果是bot，清理bot 否则结束游戏
            if self.is_enemy:
                arena.enemies.remove(self)
                del self.body
                del self
            else:
                arena.parent.end_game()
