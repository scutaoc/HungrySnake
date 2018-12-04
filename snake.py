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
        eye.y = 5 # 一个眼球中心离头部中心的y轴偏移
        eye.scale = 0.5
        eyeball = Sprite('assets/img/circle.png', color=definition.BLACK)
        eyeball.scale = 0.5
        eye.add(eyeball) # 把眼珠子“贴”在眼球上
        self.head.add(eye) # 把眼球“贴”在头上
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
        self.parent.batch.add(b, 9999 - len(self.body)) #这一句没看懂
    #初始化分数和蛇身长度
    def init_body(self):
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
        # 目标方向，角度渐变，而不是瞬间变化45度，视觉效果较好
        if abs(self.angle - self.angle_dest) < 2:
            self.angle = self.angle_dest
        else:
            if (0 < self.angle - self.angle_dest < 180) or (
                self.angle - self.angle_dest < -180):
                self.angle -= 500 * dt
            else:
                self.angle += 500 * dt

        self.head.rotation = -self.angle
        # 这个x值是Snake类(继承于cocos.cocosnode.CocosNode)的横坐标值，既不是head的也不是eye的，是这个类自己的(self)，因为它也算是一个结点        
        # 然后因为head是位于CocosNode的正中间add上去的，所以self.position其实也就正好是head.position
        self.x += math.cos(self.angle * math.pi / 180) * dt * self.speed 
        self.y += math.sin(self.angle * math.pi / 180) * dt * self.speed
        self.path.append(self.position) # position属性其实就是(x, y)，一个二元素元组
        # 根据蛇头走过的路径，更新蛇各段身体的位置
        lag = int(round(1100.0 / self.speed)) # 因为path更新得比较快，所以要跳着取path来更新，不然蛇的身体会缩得很短
        # （各个body之间相距很短），lag就是控制隔多少取一个。lag越大，蛇身体各段之间的距离就越远，1100是微调后得到的一个较优的值
        for i in range(int(self.length)):
            idx = (i + 1) * lag + 1 # 如果是i而不是i+1，第一段身体就会跟头叠在一起
            # 记住蛇身的后段一定是沿着前段走过的路径走的
            self.body[i].position = self.path[-min(idx,len(self.path))] # 当idx较小时（身体靠前的几段），path取到的是较新的部分,
            # -min函数保证了在idx越界的时候，能让它取到path[0]而不会报错
            if self.body[i].x == 0: # 似乎从没见到它print过，是用来测试的？
                print(self.body[i].position)
        m_l = max(self.length * lag * 2, 60)
        if len(self.path) > m_l: # 保存的路径过多时，丢掉很旧的路径
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

        # directs = [0, 45, 90, 135, 180, 225, 270, 315]
        if 65361 in keys or 97 in keys:  # 左
            self.angle_dest = int((self.angle_dest + 45) % 360 // 45 * 45)
        elif 65363 in keys or 100 in keys:  # 右
            self.angle_dest = int((self.angle_dest - 45) % 360 // 45 * 45)
        else:
            pass

    #添加分数
    def add_score(self, s=1):
        if self.is_dead:
            return
        self.score += s
        if self.is_enemy:
            l = (self.score + 1) // 12
        else:
            l = (self.score + 1) // 12
        if l > self.length - 4:
            self.length += 1
            self.add_body()

    #bot ai
    def ai(self, dt):
        self.angle_dest = (self.angle_dest + 360) % 360 # 调整角度到[0, 360)之内，方便后面进行判断

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
            # 敌人判断与自己的蛇头与其他蛇头的距离
            d_y = b.y - self.y
            d_x = b.x - self.x
            if abs(d_x) > 200 or abs(d_y) > 200:
                return # 离得挺远，没事
            # 如果离得比较近
            if d_x == 0:
                if d_y > 0: # 自己在上对方在下，掉头往上跑
                    angle = 90
                else: # 自己在下对方在上，掉头往上跑
                    angle = -90
            else:
                angle = math.atan(d_y / d_x) * 180 / math.pi
                angle = (angle + 180) % 360 # 直接掉头
            if abs(angle - self.angle_dest) < 5: # 如果调整后的方向还是跟原方向相差无几
                self.angle_dest += random.randrange(90, 270) # 随便找个方向逃逸
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
                if not self.is_enemy:
                    self.life -= 1
                    if self.life < 0:
                        self.crash()
                    else:
                        print(self.life, 'lives left')
                        self.position = (random.randrange(700, 900), random.randrange(350, 450))
                    pass
                else:
                    self.crash()
                return

    def crash(self):
        if not self.is_dead:
            self.is_dead = True
            self.unschedule(self.update)
            self.unschedule(self.ai)
            arena = self.parent
            for b in self.body: # 产生两倍于蛇长度的食物
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
