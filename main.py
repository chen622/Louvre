import xlrd
import numpy

from model.Exit import Exit
from model.Blank import Blank
from model.Floor import Floor
from model.Item import Item
from model.Stair import Stair

FLOORS = 5
# FLOORS = 2
ROWS = 58 * 5
# ROWS = 2
COLUMNS = 136 * 5
# COLUMNS = 3
exit_floor = []
exits = [[]]  # The position of exit
stairs = []
louvre_map = numpy.empty([FLOORS, ROWS, COLUMNS], dtype=Item)
connect_floor = []


def read_data():
    excel = xlrd.open_workbook(r'./data2.xlsx')
    for f in range(FLOORS):
        sheet = excel.sheet_by_index(f)
        for i in range(ROWS):
            for j in range(COLUMNS):
                value = int(sheet.cell(int(i / 5), int(j / 5)).value)
                if value == 1:
                    louvre_map[f][i][j] = Floor()
                elif value == 3:
                    stairs[f].append((i, j))
                    louvre_map[f][i][j] = Stair(0)
                elif value == 4:
                    exit_floor.append(f)
                    exits[f].append((i, j))
                    louvre_map[f][i][j] = Exit()
                elif value == 2:
                    stairs[f].append((i, j))
                    louvre_map[f][i][j] = Stair(1)
                else:
                    louvre_map[f][i][j] = Blank()
    count_heuristic()


def count_heuristic():
    count_exit_floor_stair()
    count_all_floor_stair()


def count_exit_floor_stair():
    for f in exit_floor:
        for (x_stair, y_stair) in stairs[f]:
            for (x_exit, y_exit) in exits[f]:
                louvre_map[f][x_stair][y_stair].set_heuristic(
                    ((x_stair - x_exit) ** 2 + (y_stair - y_exit) ** 2) ** 0.5)
            if louvre_map[f][x_stair][y_stair].toward == 0 and louvre_map[f - 1][x_stair][y_stair].heuristic > \
                    louvre_map[f][x_stair][y_stair].heuristic + 15:
                louvre_map[f - 1][x_stair][y_stair].is_down_to_up(louvre_map[f][x_stair][y_stair].heuristic + 15)
                if f - 1 not in connect_floor: connect_floor.append(f - 1)
                exits[f - 1].append((x_stair, y_stair))
            elif louvre_map[f][x_stair][y_stair].toward == 1 and louvre_map[f + 1][x_stair][y_stair].heuristic > \
                    louvre_map[f][x_stair][y_stair].heuristic + 15:
                louvre_map[f + 1][x_stair][y_stair].is_up_to_down(louvre_map[f][x_stair][y_stair].heuristic + 15)
                if f + 1 not in connect_floor: connect_floor.append(f + 1)
                exits[f + 1].append((x_stair, y_stair))


def count_all_floor_stair():
    for f in connect_floor:
        for (x_stair, y_stair) in stairs[f]:
            for (x_exit, y_exit) in exits[f]:
                louvre_map[f][x_stair][y_stair].set_heuristic(
                    ((x_stair - x_exit) ** 2 + (y_stair - y_exit) ** 2) ** 0.5 + louvre_map[f][x_exit][
                        y_exit].heuristic)
            if louvre_map[f][x_stair][y_stair].toward == 0 and louvre_map[f - 1][x_stair][y_stair].heuristic > \
                    louvre_map[f][x_stair][y_stair].heuristic + 15:
                louvre_map[f - 1][x_stair][y_stair].is_down_to_up(louvre_map[f][x_stair][y_stair].heuristic + 15)
                if f - 1 not in connect_floor: connect_floor.append(f - 1)
                exits[f - 1].append((x_stair, y_stair))
            elif louvre_map[f][x_stair][y_stair].toward == 1 and louvre_map[f + 1][x_stair][y_stair].heuristic > \
                    louvre_map[f][x_stair][y_stair].heuristic + 15:
                louvre_map[f + 1][x_stair][y_stair].is_up_to_down(louvre_map[f][x_stair][y_stair].heuristic + 15)
                if f + 1 not in connect_floor: connect_floor.append(f + 1)
                exits[f + 1].append((x_stair, y_stair))


def printGraph():
    for floor in louvre_map:
        for row in floor:
            for value in row:
                if isinstance(value, Floor):
                    print('\033[0;37;44m  \033[0m', end='')
                elif isinstance(value, Stair):
                    print('\033[0;37;46m %.2f\033[0m' % value.heuristic, end='')
                elif isinstance(value, Exit):
                    print('\033[0;37;42m  \033[0m', end='')
                else:
                    print('\033[0;37;47m  \033[0m', end='')
            print()
        print(end='\n\n\n')


if __name__ == '__main__':
    for i in range(FLOORS):
        exits.append([])
        stairs.append([])
    read_data()
