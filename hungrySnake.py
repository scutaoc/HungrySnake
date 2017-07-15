# coding=utf-8
import cocos

import definition
from arena import Arena
from cocos.audio.pygame.mixer import Sound

#声音控件
class Audio(Sound):
    def __init__(self, audio_file):
        super(Audio, self).__init__(audio_file)

#游戏图层
class HungrySnake(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(HungrySnake, self).__init__()
        #新建竞技场图层
        self.arena = Arena()
        self.add(self.arena)
        #分数列表
        self.score = cocos.text.Label('30',font_name='Times New Roman',font_size=24,color=definition.GOLD)
        self.score.position = 20, 440
        self.add(self.score, 99999)
        #播放BGM
        self.bgm = Audio('assets/audio/bgm.ogg')
        self.bgm.play(-1)

    #更新分数
    def update_score(self):
        self.score.element.text = str(self.arena.snake.score)

    #游戏结束
    def end_game(self):
        #bgm暂停
        self.bgm.stop()

        del self.bgm
        #播放失败音效
        Audio("assets/audio/gameover.wav").play()

        self.arena.unschedule(self.arena.update)
        self.arena.accel.stop()
        self.parent.gameEnd(str(self.arena.snake.score))