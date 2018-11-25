# coding=utf-8
import random
from cocos.actions import MoveTo, CallFuncS
from cocos.sprite import Sprite

import definition


def eat(spr):
    # spr是一个Dot对象
    spr.unschedule(spr.update) # 被吃掉的食物不再更新状态
    arena = spr.parent.parent
    if not spr.is_big:
        arena.batch.add(Dot()) # 如果是开局散落的食物（不是蛇死后产生的），那么在另外一个位置重新生成一颗食物（也就是说竞技场上的小粒食物数量始终保持不变）
        spr.killer.add_score() # 加1分
    else:
        spr.killer.add_score(2) # 蛇死后产生的食物每个加2分
    arena.batch.remove(spr)
    if not spr.killer.is_enemy: # 如果是玩家吃了这个食物，则刷新积分
        arena.parent.update_score()
    del spr

#小圆点
class Dot(Sprite):
    def __init__(self, pos=None, color=None):
        if color is None:
            #颜色选择
            color = random.choice(definition.ALL_COLOR)

        super(Dot, self).__init__('assets/img/circle.png', color=color)
        self.eaten = False
        #生成地图点
        if pos is None: # 开局时生成的食物
            self.position = (random.randint(40, definition.WIDTH - 40),
                             random.randint(40, definition.HEIGHT - 40))
            self.is_big = False
            self.scale = 0.8
        else: # 由于某条蛇撞死而产生的食物，pos即为死去的蛇头部的位置。食物将散落与蛇头附近
            self.position = (pos[0] + random.random() * 32 - 16,
                             pos[1] + random.random() * 32 - 16)
            self.is_big = True # 蛇产生的食物比开局散落的要大（更有价值）

        # self.schedule_interval(self.update, random.random() * 0.2 + 0.1) # 关掉这一句之后，蛇吃不了任何食物，蛇能重生，蛇身不会掉落
        self.schedule_interval(self.update, random.random() * 0.2 + 0.1)

    def update(self, dt):
        # 检测该食物是否会被蛇吃掉
        arena = self.parent.parent
        snake = arena.snake
        self.check_eaten(snake)
        for s in arena.enemies:
            self.check_eaten(s)

    def check_eaten(self, snake):
        if (not self.eaten and not snake.is_dead) and (
            abs(snake.x - self.x) < 32 and abs(snake.y - self.y) < 32
        ): # 当食物未被吃掉，而
            self.eaten = True
            self.killer = snake
            self.do(MoveTo(snake.position, 0.1) + CallFuncS(eat)) # MoveTo函数实现了当蛇靠近食物时，食物会自动被“吸引”到蛇头的效果
