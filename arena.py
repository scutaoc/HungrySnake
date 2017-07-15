# coding=utf-8
import cocos
from cocos.director import director
from pyglet.window.key import symbol_string
from cocos.audio.pygame.mixer import Sound
import definition
from snake import Snake
from dot import Dot
# 声音控件
class Audio(Sound):
    def __init__(self, audio_file):
        super(Audio, self).__init__(audio_file)
# 竞技场
class Arena(cocos.layer.ColorLayer):

    is_event_handler = True

    def __init__(self):
        super(Arena, self).__init__(250, 255, 255, 255, definition.WIDTH, definition.HEIGHT)
        #起始位置
        self.center = (director.get_window_size()[0] / 2, director.get_window_size()[1] / 2)
        #batches
        self.batch = cocos.batch.BatchNode()
        self.add(self.batch)
        #加入用户蛇身
        self.snake = Snake()
        self.add(self.snake, 10000)
        self.snake.init_body()
        self.accel = Audio('assets/audio/accel.wav')
        self.accel.set_volume(0.6)
        #加入七个bot
        self.enemies = []
        for i in range(7):
            self.add_enemy()
        #按下键集合
        self.keys_pressed = set()

        for i in range(50):
            self.batch.add(Dot())
        #注册事件
        self.schedule(self.update)
    # 添加Snake
    def add_enemy(self):
        enemy = Snake(True)
        self.add(enemy, 10000)
        enemy.init_body()
        self.enemies.append(enemy)
    # 地图更新事件
    def update(self, dt):
        if(self.snake):
            self.x = self.center[0] - self.snake.x
            self.y = self.center[1] - self.snake.y
        else:
            self.x = self.center[0]
            self.y = self.center[1]
    # 键盘按下
    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        self.snake.update_angle(self.keys_pressed)
        #按下空格蛇加速
        if symbol_string(key) == "SPACE":
            self.accel.play(-1)
            self.accel.isPlaying = True
            self.snake.speed = 300
    # 键盘释放
    def on_key_release (self, key, modifiers):
        if symbol_string(key) != "RETURN":
            self.keys_pressed.remove(key)
        self.snake.update_angle(self.keys_pressed)
        if symbol_string(key) == "SPACE":
            if self.accel.isPlaying:
                self.accel.stop()
            self.snake.speed = 180
