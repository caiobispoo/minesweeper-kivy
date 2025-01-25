from kivymd.app import MDApp
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.config import Config
from random import shuffle
# import os

# os.environ['KIVY_MULTITOUCH'] = '0'
Config.set('input', 'mouse', 'mouse,disable_multitouch')


class Tile(Button):

    def __init__(self, grid, **kwargs):
        super(Tile, self).__init__(**kwargs)
        # design settings
        self.text = ''
        self.font_size = 20
        self.font_name = 'fonts/mine-sweeper.ttf'
        self.tile_colors = {
            1: 'dodgerblue',
            2: 'green',
            3: 'red',
            4: 'mediumpurple',
            5: 'darkred',
            6: 'cyan',
            7: 'mediumvioletred',
            8: 'darkgray',
        }
        # Tile properties
        self.row = None
        self.col = None
        self.bold = True
        self.flagged = False
        self.disabled = False
        self.blocked = False
        self.is_mine = False
        self.close_mines = 0
        # GameGrid
        self.grid = grid
        # Desing settings
        # self.disabled_color = (1, 1, 1, 1)
        # self.background_disabled_normal = ''
        # self.background_disabled_down = ''
        # self.background_color = 'black'
        # self.background_normal = ''


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
        if not self.flagged and not self.disabled and not self.blocked:
            self.text = '`'
            self.flagged = True
        elif self.flagged:
            self.text = ''
            self.flagged = False

        self.grid.check_win()


    def reveal_tile(self):
        if not self.flagged and not self.blocked:
            if self.is_mine:
                self.text = '*'
                self.disabled_color = 'red'
                # self.background_color = 'red'
                self.disabled = True
                self.grid.end_game(lost=True)
            else:
                if self.close_mines > 0:
                    number = self.close_mines
                    self.text = f'{number}'
                    self.disabled_color = self.tile_colors.get(number, 'white')
                else:
                    self.text = ''
                    self.grid.reveal_blank_tiles(self)
            if not self.disabled:
                self.disabled = True

            self.grid.check_win()


class MineSweeperGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MineSweeperGrid, self).__init__(**kwargs)
        self.cols = 9
        self.rows = 9
        self.num_mines = 10
        self.tile_size = 40
        self.matrix = []
        self.create_grid()
        #self.start_timer()


    def change_difficulty(self, difficulty):
        '''Altera a dificuldade do jogo'''
        
        self.matrix = []
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

        Window.size = (self.cols * self.tile_size, self.rows * self.tile_size)

        # Reinicia o grid com a nova dificuldade
        
        self.create_grid()


    def create_grid(self):
        '''Cria o grid e também a matrix que representa o grid'''
        self.matrix = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                tile = Tile(self)
                self.matrix[row][col] = tile
                tile.row = row
                tile.col = col
                self.add_widget(tile)
        self.place_mines() # Escolhe Tiles aleatórios para terem minas
        self.calculate_mines_around() # Altera o close_mines das minas


    def place_mines(self):
        '''Escolhe aleatoriamente quais os botões que terão minas'''
        avaible_positions = [(row, col) for row in range(self.rows) for col in range(self.cols)]
        shuffle(avaible_positions)

        for row, col in avaible_positions[:self.num_mines]:
            tile = self.matrix[row][col]
            tile.is_mine = True


    def calculate_mines_around(self):
        '''Altera o valor de close_mines do Tile'''
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.matrix[row][col].is_mine:
                    self.matrix[row][col].close_mines = self.count_mines_around(row, col)


    def count_mines_around(self, row, col):
        '''Calcula o total de minas ao redor de algum Tile'''
        count = 0
        for i in range(max(0, row - 1), min(row + 2, self.rows)):
            for j in range(max(0, col - 1), min(col + 2, self.cols)):
                if self.matrix[i][j].is_mine:
                    count += 1
        return count


    def reveal_blank_tiles(self, tile):
        '''Revela todos os tiles vizinhos que têm close_mines == 0 usando DFS.'''
        row, col = tile.row, tile.col

        # Marca o tile atual como revelado
        tile.disabled = True
        tile.text = ''  # Tiles com close_mines == 0 ficam vazios

        for i in range(max(0, row - 1), min(row + 2, self.rows)):
            for j in range(max(0, col - 1), min(col + 2, self.cols)):
                neighbor = self.matrix[i][j]

                if not neighbor.disabled and not neighbor.is_mine and neighbor.close_mines == 0:
                    self.reveal_blank_tiles(neighbor)  # Chamada recursiva (DFS)
                elif not neighbor.disabled and not neighbor.is_mine and neighbor.close_mines > 0:
                    # Revela tiles com close_mines > 0, sem iniciar a recursão
                    neighbor.disabled = True
                    neighbor.text = f'{neighbor.close_mines}'
                    neighbor.disabled_color = neighbor.tile_colors.get(neighbor.close_mines, 'white')


    def end_game(self, lost=False):
        # Não está funcionando corretamente
        '''Revela todo o grid desabilitando todos os tiles'''
        if lost:
            for row in range(self.rows):
                for col in range(self.cols):
                    tile = self.matrix[row][col]

                    if not tile.is_mine and tile.flagged:
                        tile.background_color = 'red'
                        
                    elif tile.is_mine and not tile.flagged and not tile.disabled:
                        tile.disabled = True
                        tile.text = '*'
                        tile.disabled_color = 'grey'
                        # tile.background_color = 'black'
                        
                    tile.blocked = True
        
        else:
            for row in range(self.rows):
                for col in range(self.cols):
                    tile = self.matrix[row][col]

                    if tile.is_mine:
                        tile.text = '`'
                        tile.blocked = True
            # Funcionalidades da vitória
            print("Você venceu")


# mudar o check win
    def check_win(self):
        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.matrix[row][col]
                # verificar condição de vitória
                if not tile.is_mine and not tile.disabled:
                    return None
        self.end_game(lost=False)


class MineSweeperApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        Window.size = (360, 360)
        return Builder.load_file('MineSweeper.kv')


if __name__ == '__main__':
    MineSweeperApp().run()

