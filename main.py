# python 3.10
# kivy 2.3.1
# kivymd 2.0.1

from kivymd.app import MDApp
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
)
from kivy.lang import Builder
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty, StringProperty
from random import shuffle


Config.set('input', 'mouse', 'mouse,disable_multitouch')


kv = '''
MDBoxLayout:
    md_bg_color: (0.05, 0.05, 0.05, 1)

    orientation: 'vertical'
    padding: '10dp'
    spacing: '10dp'

    MDBoxLayout:
        #md_bg_color: 'green'
        orientation: 'horizontal'
        spacing: '10dp'
        size_hint: None, None
        size: self.minimum_size
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}


        MDButton:
            size_hint: None, None
            style: 'tonal'
            radius: [5]
            theme_bg_color: 'Custom'
            md_bg_color: (0.3, 0.3, 0.3, 1)
            on_release: root.ids.grid.change_difficulty('easy')

            MDButtonText:
                text: 'Fácil'
                bold: True
                theme_text_color: 'Custom'
                text_color: (0.8, 0.8, 0.8, 1)


        MDButton:
            size_hint: None, None
            style: 'tonal'
            radius: [5]
            theme_bg_color: 'Custom'
            md_bg_color: (0.3, 0.3, 0.3, 1)
            on_release: root.ids.grid.change_difficulty('medium')

            MDButtonText:
                text: 'Médio'
                bold: True
                theme_text_color: 'Custom'
                text_color: (0.8, 0.8, 0.8, 1)


        MDButton:
            size_hint: None, None
            style: 'tonal'
            radius: [5]
            theme_bg_color: 'Custom'
            md_bg_color: (0.3, 0.3, 0.3, 1)
            on_release: root.ids.grid.change_difficulty('hard')

            MDButtonText:
                text: 'Difícil'
                bold: True
                theme_text_color: 'Custom'
                text_color: (0.8, 0.8, 0.8, 1)


    MDBoxLayout:
        id: bg_count
        size_hint: None, None
        size: 60, 40
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        padding: '10dp'
        theme_bg_color: 'Custom'
        md_bg_color: (0.4, 0.4, 0.4, 1)

        Label:
            id: mine_count
            text: root.ids.grid.mine_count_str
            font_size: 32
            bold: True
            theme_text_color: 'Custom'
            text_color: 'red'


    MineSweeperGrid:
        id: grid
'''


class Tile(Button):

    def __init__(self, grid, **kwargs):
        super(Tile, self).__init__(**kwargs)
        # design settings
        self.text = ''
        self.font_size = 20
        self.font_name = 'fonts/mine-sweeper.ttf'
        self.font_colors = {
            1: 'dodgerblue',
            2: 'green',
            3: 'red',
            4: 'mediumpurple',
            5: 'darkred',
            6: 'cyan',
            7: 'mediumvioletred',
            8: 'darkgray',
        }
        self.row = None
        self.col = None
        self.bold = True
        self.flagged = False
        self.disabled = False
        self.blocked = False
        self.is_mine = False
        self.nearby_mines = 0
        self.grid = grid


    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button == 'right':
                self.add_flag()
                return True
            elif touch.button == 'left':
                self.reveal_tile()
                return True
        return super(Tile, self).on_touch_down(touch)


    def add_flag(self):
        '''Adiciona flag nos botões que não a tem, e remove caso contrário.'''

        if not self.flagged and not self.disabled and not self.blocked:
            self.text = '`'
            self.grid.mine_count -= 1
            self.grid.mine_count_str = f'{self.grid.mine_count:02}'
            self.flagged = True
        elif self.flagged:
            self.text = ''
            self.grid.mine_count += 1
            self.grid.mine_count_str = f'{self.grid.mine_count:02}'
            self.flagged = False

        self.grid.check_win()


    def reveal_tile(self):
        '''Responsável por revelar os botões e terminar o jogo caso seja uma mina.'''

        if not self.flagged and not self.blocked:
            if self.is_mine:
                self.text = '*'
                self.disabled_color = 'red'
                self.disabled = True
                self.grid.end_game(lost=True)
            else:
                if self.nearby_mines > 0:
                    number = self.nearby_mines
                    self.text = f'{number}'
                    self.disabled_color = self.font_colors.get(number, 'white')
                else:
                    self.text = ''
                    self.grid.reveal_blank_tiles(self)
            if not self.disabled:
                self.disabled = True

            self.grid.check_win()


class MineSweeperGrid(GridLayout):
    mine_count = NumericProperty(0)
    mine_count_str = StringProperty('00')

    def __init__(self, **kwargs):
        super(MineSweeperGrid, self).__init__(**kwargs)
        self.cols = 9
        self.rows = 9
        self.num_mines = 10
        self.mine_count = self.num_mines
        self.mine_count_str = f'{self.mine_count:02}'
        self.tile_size = 40
        self.matrix = []
        self.create_grid()

    def show_zero_tile(self):
        '''Função de auxílio para correção de um bug específico.'''

        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.matrix[row][col]
                if tile.nearby_mines == 0 and not tile.is_mine:
                    tile.text = '0'


    def change_difficulty(self, difficulty):
        '''Altera a dificuldade do jogo e o tamanho da janela.'''
        
        self.clear_widgets()

        if difficulty == 'easy':
            self.cols = 9
            self.rows = 9
            self.num_mines = 10
        elif difficulty == 'medium':
            self.cols = 16
            self.rows = 16
            self.num_mines = 40
        elif difficulty == 'hard':
            self.cols = 32
            self.rows = 16
            self.num_mines = 99

        self.mine_count = self.num_mines
        self.mine_count_str = f'{self.mine_count:02}'
        Window.size = (self.cols * self.tile_size, self.rows * self.tile_size + 90)

        self.create_grid()


    def create_grid(self):
        '''Cria o grid e sua matriz.'''

        self.matrix = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                tile = Tile(self)
                self.matrix[row][col] = tile
                tile.row = row
                tile.col = col
                self.add_widget(tile)
        
        self.place_mines()
        self.set_nearby_mines()
        # self.show_zero_tile()


    def place_mines(self):
        '''Escolhe aleatoriamente quais os botões que terão minas.'''

        avaible_positions = [(row, col) for row in range(self.rows) for col in range(self.cols)]
        shuffle(avaible_positions)

        for row, col in avaible_positions[:self.num_mines]:
            tile = self.matrix[row][col]
            tile.is_mine = True


    def set_nearby_mines(self):
        '''Altera o valor de nearby_mines do Tile.'''

        for row in range(self.rows):
            for col in range(self.cols):
                if not self.matrix[row][col].is_mine:
                    self.matrix[row][col].nearby_mines = self.count_nearby_mines(row, col)


    def count_nearby_mines(self, row, col):
        '''Calcula o total de minas ao redor de algum Tile'''

        count = 0
        for i in range(max(0, row - 1), min(row + 2, self.rows)):
            for j in range(max(0, col - 1), min(col + 2, self.cols)):
                if self.matrix[i][j].is_mine:
                    count += 1
        return count


    def reveal_blank_tiles(self, tile):
        '''Revela todos os tiles vizinhos que têm nearby_mines == 0 usando DFS.'''

        row, col = tile.row, tile.col

        if tile.flagged:
            self.mine_count += 1
            self.mine_count_str = f'{self.mine_count:02}'
            tile.flagged = False  

        tile.disabled = True
        tile.text = ''

        for i in range(max(0, row - 1), min(row + 2, self.rows)):
            for j in range(max(0, col - 1), min(col + 2, self.cols)):
                neighbor = self.matrix[i][j]

                if not neighbor.disabled and not neighbor.is_mine and neighbor.nearby_mines == 0:
                    self.reveal_blank_tiles(neighbor)

                elif not neighbor.disabled and not neighbor.is_mine and neighbor.nearby_mines > 0:
                    neighbor.disabled = True
                    neighbor.text = f'{neighbor.nearby_mines}'
                    neighbor.disabled_color = neighbor.font_colors.get(neighbor.nearby_mines, 'white')

                    if neighbor.flagged and not neighbor.is_mine:
                        self.mine_count += 1
                        self.mine_count_str = f'{self.mine_count:02}'
                        neighbor.flagged = False 


    def check_win(self):
        '''Verifica que o jogador está em condição de vitória.'''

        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.matrix[row][col]
                if not tile.is_mine and not tile.disabled:
                    return None
        self.end_game(lost=False)


    def end_game(self, lost=False):
        '''Termina o game e impede que o jogador interaja com o grid.'''

        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.matrix[row][col]
                if lost:
                    if not tile.is_mine and tile.flagged:
                        tile.background_color = 'red'
                    elif tile.is_mine and not tile.flagged and not tile.disabled:
                        tile.disabled = True
                        tile.text = '*'
                        tile.disabled_color = 'grey'
                    tile.blocked = True
                else:
                    if tile.is_mine and not tile.flagged:
                        tile.text = '`'
                        self.mine_count -= 1
                        self.mine_count_str = f'{self.mine_count:02}'
                    tile.blocked = True

        if lost:
            MDDialog(
                MDDialogHeadlineText(
                    text = 'VOCÊ PERDEU!',
                    bold = True
                ),
                MDDialogSupportingText(
                    text = 'Selecione uma dificuldade para iniciar uma nova partida.',
                ),
                style = 'outlined',
            ).open()

        else:
            MDDialog(
                MDDialogHeadlineText(
                    text = 'VOCÊ VENCEU!',
                    bold = True
                ),
                MDDialogSupportingText(
                    text = 'Parabéns, para iniciar uma nova partida selecione uma dificuldade.',
                ),
                style = 'outlined',
            ).open()


class MineSweeperApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        Window.size = (360, 360 + 90)
        return Builder.load_string(kv)


if __name__ == '__main__':
    MineSweeperApp().run()

