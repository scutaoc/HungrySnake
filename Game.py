# coding=utf-8
import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.menu import Menu, CENTER, ImageMenuItem, BOTTOM, EntryMenuItem
from pyglet.app import exit
from cocos.actions import *
from cocos.audio.pygame.mixer import Sound
from cocos.audio.pygame import mixer
import re
import os

import definition
from hungrySnake import HungrySnake

#声音控件
class Audio(Sound):
    def __init__(self, audio_file):
        super(Audio, self).__init__(audio_file)
#游戏结束界面
class GameOver(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self, score):
        super(GameOver, self).__init__()
        #导入背景图片
        bkg = Sprite("assets/img/bkg.png",position=(director.get_window_size()[0] / 2, director.get_window_size()[1] / 2))
        self.add(bkg, 0, name='bkg')

        #导入menu图层
        menu = GameEndMenu() # "再来一次"、"返回"、输入玩家昵称
        self.add(menu,0, name='menu')

        #获取中间位置
        positionW = director.get_window_size()[0]/2
        positionH = director.get_window_size()[1]/2
        self.score = score
        # self.score = str(10)

        #设置分数值标签
        self.scoreLabel = cocos.text.Label(self.score,
                                      font_name='SimHei',
                                      font_size=30,
                                      color=definition.MAROON)
        self.scoreLabel.position = positionW+50, positionH-10
        self.scoreLabel.visible = False
        self.add(self.scoreLabel)
        #设置分数标签
        self.text_score = cocos.text.Label('Score: ',
                                font_name='SimHei',
                                font_size=24,
                                color=definition.MAROON)
        self.text_score.position = positionW-100, positionH-10
        self.text_score.visible = False
        self.add(self.text_score)

        #设置最高分数Label
        bestScore = self.getBestScore()
        if int(bestScore) < int(score):
            bestScore = score
        self.bestScoreLabel = cocos.text.Label(bestScore,
                                      font_name='SimHei',
                                      font_size=30,
                                      color=definition.MAROON)
        self.bestScoreLabel.position = positionW+50, positionH-50
        self.bestScoreLabel.visible = False
        self.add(self.bestScoreLabel)

        #Best标签
        self.text_best_score = cocos.text.Label('Best: ',
                                font_name='SimHei',
                                font_size=24,
                                color=definition.MAROON)
        self.text_best_score.position = positionW-100, positionH-50
        self.text_best_score.visible = False
        self.add(self.text_best_score)
        self.showLabel() # 先全部准备好，再一起显示出来

    #更新数据库
    def rank(self, name='Guest'):
        name = name.strip()
        with open('data.txt','a+') as f: 
            # a+模式下，文件打开后起始指针为文件末尾，此时readline()将读不到数据，需要先调整文件指针的位置
            f.seek(0, os.SEEK_SET)
            lines = f.readlines()
            num = 0
            if name == 'Guest': # 如果是匿名，则递增编号
                for line in lines:
                    if line[:5] == 'Guest':
                        num += 1 # 编号递增
                name = 'Guest' + str(num) # 拼接成一个完整的用户昵称
                f.write(str(name) + ':' + str(self.score)+'\n')
            else: # 否则直接写入
                f.write(str(name) + ':' + str(self.score) + '\n')
            
    def startAgain(self): #重新开始
        self.parent.startGame() #调用父类函数
    def back(self): #返回主菜单
        self.parent.back()

    def getBestScore(self): #获取数据库最高分
        f = open('data.txt', 'a+')
        max = 0
        lines = f.readlines()
        for line in lines:
            mat = re.search('([0-9A-Za-z]+)$', line) #正则寻找最高分
            if mat:
                if int(mat.group(1)) > max:
                    max = int(mat.group(1))
        f.close()
        return str(max)

    def showLabel(self): #显示分数标签
        self.scoreLabel.visible = True
        self.bestScoreLabel.visible = True
        self.text_score.visible = True
        self.text_best_score.visible = True
    #事件处理
    def on_mouse_press(self, x, y, buttons, modifiers):
        self.showLabel()
    def on_mouse_motion(self, x, y, buttons, modifiers):
        self.showLabel()
    def on_key_press(self, key, modifiers):
        self.showLabel()
#游戏结束界面菜单按钮
class GameEndMenu(Menu):
    def __init__(self):
        super(GameEndMenu, self).__init__()
        self.menu_valign = BOTTOM
        self.menu_halign = CENTER   #菜单位置
        #设置菜单属性，菜单选择音效、激活音效，菜单项颜色
        self.select_sound = Audio("assets/audio/button.wav")
        self.select_sound.set_volume(0.6)
        self.activate_sound = self.select_sound
        self.font_item_selected['font_size'] = 35
        self.font_item_selected['color'] = (0, 0, 0, 200)
        self.font_item['color'] = (0, 0, 0, 150)
        self.length = 6
        #菜单项创建
        menu_items = [
            (EntryMenuItem('Name:', self.handleInput, 'Guest', max_length=10)),
            (ImageMenuItem("assets/img/button/again.png", self.startAgain)),
            (ImageMenuItem("assets/img/button/back.png", self.back)),
        ]
        self.create_menu(menu_items)
    #输入菜单handler
    def handleInput(self, value):
        self.name = value
    #再来一次事件handler
    def startAgain(self):
        try:
            self.name
        except AttributeError:
            self.name = 'Guest'
        self.parent.rank(self.name)
        self.parent.startAgain()
    #返回主菜单handler
    def back(self):
        Audio('assets/audio/back.wav').play()
        try:
            self.name
        except AttributeError:
            self.name = 'Guest'
        self.parent.rank(self.name)
        self.parent.back()
#游戏开始界面菜单
class GameStartMenu(Menu):

    def __init__(self):
        super(GameStartMenu, self).__init__()
        # 设置菜单属性，菜单选择音效、激活音效，菜单项颜色
        self.menu_valign = BOTTOM
        self.menu_halign = CENTER
        self.buttonAu = Audio("assets/audio/button.wav")
        self.startAu = Audio("assets/audio/start.wav")
        self.select_sound = Audio("assets/audio/button.wav")
        self.select_sound.set_volume(0.6)
        self.font_item['font_size'] += 8
        self.font_item_selected['font_size'] += 10
        # 菜单项创建
        menu_items = [
            (ImageMenuItem("assets/img/button/start.png", self.start)),
            (ImageMenuItem("assets/img/button/help.png", self.help)),
            (ImageMenuItem("assets/img/button/bangdan.png", self.showRank)),
            (ImageMenuItem("assets/img/button/exit.png", self.onQuit))
        ]
        self.create_menu(menu_items)
    #菜单按钮的handler
    def start(self):
        self.startAu.play(loops=0)
        self.parent.startGame()
    def help(self):
        self.buttonAu.play(loops=0)
        self.parent.showHelp()
    def showRank(self):
        self.buttonAu.play(loops=0)
        self.parent.showRank()
    def onQuit(self):
        self.buttonAu.play(loops=0)
        exit()

#帮助界面
class HelpLayer(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self):
        #背景
        super(HelpLayer, self).__init__()
        # 获取窗口的中心位置
        positionW, positionH = director.get_window_size()[0] / 2, director.get_window_size()[1] / 2
        bkg = Sprite("assets/img/bkg.png",position = (positionW, positionH))
        self.add(bkg, 0)
        #帮助
        help = Sprite("assets/img/help.png", position = (positionW + 15, positionH - 80))
        self.add(help,1)
    #返回事件handler+音效
    def on_key_press(self, key, modifiers):
        Audio('assets/audio/back.wav').play()
        self.parent.back()
#排行榜界面
class RankLayer(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self,dicts):
        super(RankLayer, self).__init__()
        #获取位置
        positionW = director.get_window_size()[0]/2
        positionH = director.get_window_size()[1]/2
        #背景
        bkg = Sprite("assets/img/bkg.png",position=(positionW, positionH))
        self.add(bkg, 0)
        #榜单背景
        rankList = Sprite("assets/img/rank.png",position=(positionW+15,
                                                     positionH-80))
        self.add(rankList, 1)
        #生成榜单前五项Label
        for j in range(5):
            if j < len(dicts):
                self.scoreLabel = cocos.text.Label(str(dicts[j][1]),
                                                   font_name='SimHei',
                                                   font_size=26,
                                                   color=definition.BLACK + (255,))
                self.scoreLabel.position = positionW+50, positionH - (-10 + 42 * j)
                self.add(self.scoreLabel)

                self.text = cocos.text.Label(dicts[j][0],
                                             font_name='SimHei',
                                             font_size=22,
                                             color=definition.BLACK + (200,))
                self.text.position = positionW - 150, positionH - (-10 + 42 * j)
                self.add(self.text)
            #数据库不足5人，生成填充项Label
            else:
                self.text = cocos.text.Label('<Unknown> Waiting for you!',
                                             font_name='SimHei',
                                             font_size=18,
                                             color=definition.BLACK + (200,))
                self.text.position = positionW - 150, positionH - (-10 + 42 * j)
                self.add(self.text)
    #返回事件handler+返回音效
    def on_key_press(self, key, modifiers):
        Audio('assets/audio/back.wav').play()
        self.parent.back()
#游戏主控
class Game(cocos.layer.Layer):
    def __init__(self):
        super(Game, self).__init__()
        #开始背景
        bkg = Sprite("assets/img/bkg.png",position=(director.get_window_size()[0] / 2, director.get_window_size()[1] / 2))
        self.add(bkg, 0, name='bkg')
        #开始菜单
        menu = GameStartMenu()
        self.add(menu,0, name='menu')

    #开始游戏
    def startGame(self):
        #创建游戏竞技场实例
        game = HungrySnake()
        self.gameLayer = game
        #为了渲染效率删除无用Layer
        try: #错误处理
            self.remove('gameover')
        except:
            self.remove('menu')
            self.remove('bkg')
        #加入游戏界面
        self.add(game,0,'game')

    #游戏结束
    def gameEnd(self,score):
        # 游戏结束动画
        # dead = Sprite('assets/img/dead.png')
        # dead.position = director.get_window_size()[0] / 2 , director.get_window_size()[1] / 2
        # self.sprite = dead
        # 淡出效果1s
        # self.fade_out()
        #删除游戏图层
        self.remove('game')
        #创建结束图层
        self.gameOver = GameOver(score)
        self.add(self.gameOver,0,'gameover')

    #淡出动画效果
    def fade_out(self):
        fade_action = FadeOut(1)
        self.sprite.opacity = 0
        self.add(self.sprite, z=1)
        self.sprite.do(fade_action)

    #返回主页函数
    def back(self):
        #清理无用界面
        try:
            self.remove('gameover')
        except:
            try:
                self.remove('help')
            except:
                self.remove('rank')
        #背景
        bkg = Sprite("assets/img/bkg.png",
                     position=(director.get_window_size()[0] / 2, director.get_window_size()[1] / 2))
        self.add(bkg, 0, name='bkg')
        #菜单
        menu = GameStartMenu()
        self.add(menu, 0, name='menu')

    #显示帮助界面
    def showHelp(self):
        self.remove('menu')
        self.remove('bkg')
        self.help = HelpLayer()
        self.add(self.help,10000,'help')

    # 显示榜单界面
    def showRank(self):
        self.remove('menu')
        self.remove('bkg')
        #数据字典 'name' : value
        
        # 排行榜有两种排序方式，一种是按照每个玩家的最高分来排，一个玩家最多出现一次，一种是不看玩家只按分数来排，可能出现前五都是同一个玩家的现象。我们任意选择其中的一种即可
        
        with open('data.txt', 'r') as f:
            lines = f.readlines()
            # 按照每个玩家的最高分来排
            # data = {}
            # for line in lines: # line为一行数据，形如"Nobody0:8"
            #     name, score = line.split(':')[0], line.split(':')[1]
            #     try:
            #         if int(score) > data[name]: # 如果data中已经有该玩家的数据了，则更新他的分数最大值
            #             data[name] = int(score)
            #     except KeyError: # 若此时data中尚未存有该玩家的数据，则新建之
            #         data[name] = int(score)
            # # data.items()的内容形如：dict_items([('Guest1', 49), ('Guest2', 3)])
            # dicts = sorted(data.items(), key=lambda d: d[1], reverse=True) # 按照分数值降序排序字典，返回一个元素为tuple的列表

            # 不看玩家只按分数来排
            data = []
            for line in lines: # line为一行数据，形如"Nobody0:8"
                name, score = line.split(':')[0], line.split(':')[1]
                data.append((name, int(score)))
            # data的内容形如：[('Guest1', 49), ('Guest2', 3)]
            dicts = sorted(data, key=lambda d: d[1], reverse=True) # 按照分数值降序排序字典，返回一个元素为tuple的列表

        self.rank = RankLayer(dicts)
        #添加榜单
        self.add(self.rank, 0, 'rank')
#初始化
mixer.init()
director.init(caption=u"贪吃蛇大作战", resizable=False)
director.run(cocos.scene.Scene(Game()))