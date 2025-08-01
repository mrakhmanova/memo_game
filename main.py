# МЕМО
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QIcon, QMovie, QFont
from PyQt5.QtCore import QTimer, QSize
from random import sample, shuffle
from os import listdir

TILE_SIZE = 100
THEMES = ['flowers', 'animals']  # tile topics
TIME = 1000


class MainWindow(QMainWindow):
    """The start window"""

    def __init__(self):
        """Load memo.ui with the start window

        User can choose theme, number of tiles and one or two players level
        self.pushButton_play is for playing game
        self.pushButton_quit is for exit"""
        super().__init__()
        uic.loadUi('memo.ui', self)
        self.setWindowIcon(QIcon('images/icon.png'))
        self.game = None
        self.pushButton_play.clicked.connect(self.play)
        self.pushButton_quit.clicked.connect(self.close)

    def play(self):
        """Run the game

        Take the information about chosen theme and number of tiles from comboBoxes
        Create and show game's window"""

        if self.radioButton1.isChecked():
            self.game = GameWindow1(self.comboBox_size.currentIndex() + 4,
                                    self.comboBox_theme.currentIndex())
        else:
            self.game = GameWindow2(self.comboBox_size.currentIndex() + 4,
                                    self.comboBox_theme.currentIndex())
        self.game.show()

    def close(self):
        super().close()
        if self.game:
            self.game.close()


class GameWindow(QWidget):
    """Game's window with tiles and images"""

    def __init__(self, num_tiles, num_theme):
        """Initialization

        :param num_tiles: the number of tiles in row (3, 4 or 5) to play 3*4 or 4*5 or 5*6 game
        :param num_theme: the index of the chosen theme from THEMES
        """
        super().__init__()
        self.tiles_in_row = num_tiles
        self.num_tiles = num_tiles * (num_tiles - 1)  # tiles amount
        self.num_theme = num_theme  # index of the theme
        self.tiles_opened = []  # opened cards (0, 1 or 2), (place number, image number)
        self.buttons = []  # buttons list
        self.num_images = []  # numbers of images in order they appeared
        self.images = []  # labels with images list
        self.shift = TILE_SIZE // 2  # the shift to place objects on the window
        self.tiles_done = 0  # opened tiles amount
        self.window_width = num_tiles * TILE_SIZE + TILE_SIZE * 3
        self.window_height = (num_tiles - 1) * TILE_SIZE + TILE_SIZE
        self.timer = QTimer()  # the timer for opened cards
        self.timer.timeout.connect(self.close_cards)
        self.timer_ending = QTimer()  # the timer for pause before victory
        self.timer_ending.timeout.connect(self.win)
        self.setWindowIcon(QIcon('images/icon.png'))

    def pictures_array(self):
        """Form an array of images and buttons, place buttons above images

        :return: None
        """
        self.picture_choice(self.num_tiles)
        for i in range(self.tiles_in_row - 1):
            for j in range(self.tiles_in_row):
                btn = QPushButton(self)
                btn.setObjectName(f'btn{i * self.tiles_in_row + j}')
                btn.resize(TILE_SIZE, TILE_SIZE)
                btn.move(self.shift + TILE_SIZE * j, TILE_SIZE * i + TILE_SIZE // 2)
                btn.setIcon(QIcon(f'images/card_cover/{THEMES[self.num_theme]}'))
                btn.setIconSize(QSize(TILE_SIZE, TILE_SIZE))
                btn.clicked.connect(self.open_card)
                pixmap = QPixmap(f'images/{THEMES[self.num_theme]}/'
                                 f'{self.num_images[i * self.tiles_in_row + j]}')
                img = QLabel(self)
                img.setObjectName(f'img{i * self.tiles_in_row + j}')
                img.move(self.shift + TILE_SIZE * j, TILE_SIZE * i + TILE_SIZE // 2)
                img.resize(TILE_SIZE, TILE_SIZE)
                img.setPixmap(pixmap)
                img.hide()
                self.buttons += [btn]
                self.images += [img]

    def picture_choice(self, number):
        """Choose the number of images from a directory with chosen theme

        :param number: amount of images (tiles)
        :return: None
        """
        tmp_images = sample(listdir(f'images/{THEMES[self.num_theme]}'), number // 2)
        self.num_images = tmp_images * 2
        shuffle(self.num_images)

    def open_card(self):
        """Open images, one or two.

        Timer starts when two images opened"""
        if len(self.tiles_opened) < 2:
            s = self.sender().objectName()
            i = int(s[3:])
            self.tiles_opened += [(i, self.num_images[i])]
            self.buttons[i].hide()
            self.images[i].show()
        if len(self.tiles_opened) == 2:
            self.timer.start(TIME)
            self.buttons_unblock(False)

    def close_cards(self):
        """Close opened cards

        if images are equal, hide them and form cards deck. If not - show buttons again"""
        if self.tiles_opened[0][1] == self.tiles_opened[1][1]:
            self.images[self.tiles_opened[0][0]].hide()
            self.images[self.tiles_opened[1][0]].hide()
            self.card_stack()
            self.tiles_done += 2  # a number of opened cards
            self.score_and_turn(True)
            if self.tiles_done == self.num_tiles:  # when all cards opened
                self.timer_ending.start(int(TIME * 1.5))  # pause before fireworks
        else:
            self.images[self.tiles_opened[0][0]].hide()
            self.images[self.tiles_opened[1][0]].hide()
            self.buttons[self.tiles_opened[0][0]].show()
            self.buttons[self.tiles_opened[1][0]].show()
            self.score_and_turn(False)
        self.tiles_opened.clear()
        self.timer.stop()
        self.buttons_unblock(True)

    def buttons_unblock(self, flag):
        """Blocks all buttons when two images opened

        :param flag: bool, to block or not to block
        :return: None
        """
        for btn in self.buttons:
            btn.setEnabled(flag)

    def win(self):
        """Ending of the game with fireworks and congrats"""
        self.timer_ending.stop()
        for child in self.children():
            child.hide()
        gif = QMovie('images/firework.gif')
        gif.start()
        label = QLabel(self)
        label.setMovie(gif)
        label.adjustSize()
        label.move(self.width() // 2 - label.width() // 2,
                   self.height() // 2 - label.height() // 2)
        label.show()

        victory_label = QLabel(self)
        font = QFont()
        font.setPointSize(16)
        victory_label.setFont(font)
        victory_label.setStyleSheet("color: red")
        victory_label.setText('Победа!!!')
        victory_label.adjustSize()
        victory_label.move(self.width() // 2 - victory_label.width() // 2,
                           self.height() // 2 - victory_label.height() // 2)
        victory_label.show()


class GameWindow1(GameWindow):
    def __init__(self, num_tiles, num_theme):
        super().__init__(num_tiles, num_theme)
        self.setWindowTitle('Игра * 1')
        self.setFixedSize(QSize(self.window_width, self.window_height))
        self.steps_label = QLabel(self)
        self.scores_label = QLabel(self)
        self.steps = 0
        self.scores = 0
        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, self.window_width, self.window_height)
        self.pictures_array()
        self.steps_label.setText('Ходы: 0  ')
        font = QFont()
        font.setPointSize(12)
        self.steps_label.setFont(font)
        self.steps_label.move(TILE_SIZE * self.tiles_in_row + TILE_SIZE, TILE_SIZE // 2)
        self.steps_label.show()
        self.scores_label.setText('Очки: 0  ')
        self.scores_label.setFont(font)
        self.scores_label.move(self.shift + TILE_SIZE * self.tiles_in_row + TILE_SIZE // 2,
                               TILE_SIZE // 2 * 2)
        self.scores_label.show()

    def close_cards(self):
        super().close_cards()
        self.steps += 1
        self.steps_label.setText('Ходы: ' + str(self.steps))
        self.scores_label.setText('Очки: ' + str(self.scores))

    def score_and_turn(self, bl):
        if bl:
            self.scores += 1

    def card_stack(self):
        pxm = QPixmap(f'images/card_cover/{THEMES[self.num_theme]}')
        img = QLabel(self)
        img.move(self.shift + TILE_SIZE * self.tiles_in_row + TILE_SIZE // 2 + 2 * self.tiles_done,
                 TILE_SIZE * 2 + 2 * self.tiles_done)
        img.resize(TILE_SIZE, TILE_SIZE)
        img.setPixmap(pxm)
        img.show()

    def win(self):
        super().win()
        winner_label = QLabel(self)
        font = QFont()
        font.setPointSize(16)
        winner_label.setFont(font)
        winner_label.setStyleSheet("color: red")
        winner_label.setText(f'Ваша успешность: {self.scores} / {self.steps}')
        winner_label.adjustSize()
        winner_label.move(self.width() // 2 - winner_label.width() // 2,
                          self.height() // 2 + winner_label.height() // 2)
        winner_label.show()


class GameWindow2(GameWindow):
    def __init__(self, num_tiles, num_theme):
        super().__init__(num_tiles, num_theme)
        self.setWindowTitle('Игра * 2')
        self.shift += TILE_SIZE * 2
        self.steps1 = 0
        self.steps2 = 0
        self.scores1 = 0
        self.scores2 = 0
        self.turn = 1  # whose turn
        self.window_width = num_tiles * TILE_SIZE + TILE_SIZE * 5
        self.setFixedSize(QSize(self.window_width, self.window_height))
        self.steps_label1 = QLabel(self)  # steps of first player
        self.steps_label2 = QLabel(self)  # steps of second player
        self.scores_label1 = QLabel(self)  # scores of first player
        self.scores_label2 = QLabel(self)  # scores of second player
        self.timer = QTimer()
        self.timer.timeout.connect(self.close_cards)
        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, self.window_width, self.window_height)
        self.pictures_array()
        font = QFont()
        font.setPointSize(12)
        q1 = QLabel(self)
        q1.setText('Игрок 1')
        q1.setFont(font)
        q1.move(TILE_SIZE // 2, TILE_SIZE // 2)
        q2 = QLabel(self)
        q2.setText('Игрок 2')
        q2.setFont(font)
        q2.move(self.shift + TILE_SIZE * self.tiles_in_row + TILE_SIZE // 2, TILE_SIZE // 2)
        self.steps_label1.setText('Ходы: 0  ')
        self.steps_label1.setFont(font)
        self.steps_label1.move(TILE_SIZE // 2, TILE_SIZE)
        self.steps_label1.show()
        self.steps_label2.setText('Ходы: 0  ')
        self.steps_label2.setFont(font)
        self.steps_label2.move(self.shift + TILE_SIZE * self.tiles_in_row + TILE_SIZE // 2,
                               TILE_SIZE)
        self.steps_label2.show()
        self.scores_label1.setText('Очки: 0  ')
        self.scores_label1.setFont(font)
        self.scores_label1.move(TILE_SIZE // 2, TILE_SIZE // 2 * 3)
        self.scores_label1.show()
        self.scores_label2.setText('Очки: 0  ')
        self.scores_label2.setFont(font)
        self.scores_label2.move(self.shift + TILE_SIZE * self.tiles_in_row + TILE_SIZE // 2,
                                TILE_SIZE // 2 * 3)
        self.scores_label2.show()

    def score_and_turn(self, bl):
        if bl:
            if self.turn == 1:
                self.scores1 += 1
            else:
                self.scores2 += 1
        else:
            self.turn = 3 - self.turn

    def close_cards(self):
        if self.turn == 1:
            self.steps1 += 1
        else:
            self.steps2 += 1
        super().close_cards()
        self.steps_label1.setText('Ходы: ' + str(self.steps1))
        self.scores_label1.setText('Очки: ' + str(self.scores1))
        self.steps_label2.setText('Ходы: ' + str(self.steps2))
        self.scores_label2.setText('Очки: ' + str(self.scores2))

    def card_stack(self):
        pxm = QPixmap(f'images/card_cover/{THEMES[self.num_theme]}')
        if self.turn == 2:
            img = QLabel(self)
            img.move(self.shift + TILE_SIZE * self.tiles_in_row + TILE_SIZE // 2 + 2 * self.scores2,
                     TILE_SIZE * 2 + 2 * self.scores2)
            img.resize(TILE_SIZE, TILE_SIZE)
            img.setPixmap(pxm)
            img.show()
        else:
            img = QLabel(self)
            img.move(TILE_SIZE // 2 + 2 * self.scores1, TILE_SIZE * 2 + 2 * self.scores1)
            img.resize(TILE_SIZE, TILE_SIZE)
            img.setPixmap(pxm)
            img.show()

    def win(self):
        super().win()
        winner = 0
        if self.scores2 > self.scores1:
            winner = 2
        elif self.scores1 > self.scores2:
            winner = 1
        winner_label = QLabel(self)
        font = QFont()
        font.setPointSize(16)
        winner_label.setFont(font)
        winner_label.setStyleSheet("color: red")
        if winner:
            winner_label.setText(f'Игрок {winner} победил со счётом '
                                 f'{max(self.scores1, self.scores2)} :'
                                 f' {min(self.scores1, self.scores2)}')
        else:
            winner_label.setText(f'Победила дружба! Счёт {self.scores1} : {self.scores2}')
        winner_label.adjustSize()
        winner_label.move(self.width() // 2 - winner_label.width() // 2,
                          self.height() // 2 + winner_label.height() // 2)
        winner_label.show()


app = QApplication(sys.argv)
ex = MainWindow()
ex.show()
sys.exit(app.exec_())
