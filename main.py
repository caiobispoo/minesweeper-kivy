from kivymd.app import MDApp
from kivy.uix.button import Button
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
        self.text = ''
        self.flagged = False
        self.disabled = False
        self.is_mine = False
        self.close_mines = 0
        self.grid = grid
        # self.background_color = [0, 0, 0, 1]


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
        if not self.flagged:
            self.text = 'F'
            self.flagged = True
        else:
            self.text = ''
            self.flagged = False


    def reveal_tile(self):
        if not self.flagged:
            if self.is_mine:
                self.text = 'M'
                self.grid.end_game(lost=True)
            else:
                if self.close_mines > 0:
                    self.text = f'{str(self.close_mines)}'
                else:
                    self.text = ''
                    self.grid.reveal_blank_tiles(self)
            self.disabled = True
            self.grid.check_win()


class MineSweeperGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MineSweeperGrid, self).__init__(**kwargs)
        self.cols = 9
        self.rows = 9
        self.num_mines = 10
        self.matrix = []
        self.create_grid()
        #self.start_timer()


    def create_grid(self):
        '''Cria o grid e também a matrix que representa o grid'''
        self.matrix = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                tile = Tile(self)
                self.matrix[row][col] = tile
                self.add_widget(tile)
        self.place_mines() # Escolhe Tiles aleatórios para terem minas
        self.calculate_mines_around() # Altera o close_mines das minas


    def place_mines(self):
        '''Escolhe aleatoriamente quais os botões que terão minas'''
        avaible_positions = [(row, col) for row in range(self.rows) for col in range(self.cols)]
        shuffle(avaible_positions)

        for row, col in avaible_positions[:self.num_mines]:
            self.matrix[row][col].is_mine = True


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
        '''
        Revela todos os tiles vizinhos que têm close_mines == 0 usando DFS.
        '''
        row, col = self.get_tile_position(tile)

        # Marca o tile atual como revelado
        tile.disabled = True
        tile.text = ''  # Tiles com close_mines == 0 ficam vazios

        # Itera sobre as células vizinhas
        for i in range(max(0, row - 1), min(row + 2, self.rows)):
            for j in range(max(0, col - 1), min(col + 2, self.cols)):
                neighbor = self.matrix[i][j]

                # Revela apenas células que não foram reveladas, não são minas e têm close_mines == 0
                if not neighbor.disabled and not neighbor.is_mine and neighbor.close_mines == 0:
                    self.reveal_blank_tiles(neighbor)  # Chamada recursiva (DFS)
                elif not neighbor.disabled and not neighbor.is_mine and neighbor.close_mines > 0:
                    # Revela tiles com close_mines > 0, mas não propaga a revelação
                    neighbor.disabled = True
                    neighbor.text = f'{neighbor.close_mines}'


    def get_tile_position(self, tile):
        '''Obtem as coordenadas de um tile de posição desconhecida'''
        for row in range(self.rows):
            for col in range(self.cols):
                if self.matrix[row][col] == tile:
                    return row, col
        return None, None


    def end_game(self, lost=False):
        '''Revela todo o grid e desabilita todos os tiles'''
        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.matrix[row][col]
                if not tile.disabled:
                    if lost and tile.is_mine:
                        tile.text = 'M'  # Revela todas as minas em caso de derrota
                    elif not tile.is_mine:
                        tile.reveal_tile()  # Revela os tiles que não são minas
                tile.disabled = True  # Desabilita todos os tiles

        if lost:
            print('Você perdeu!')
        else:
            print('Você ganhou!')


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
        Window.size = (640, 640)

        return MineSweeperGrid()


if __name__ == '__main__':
    MineSweeperApp().run()

