from copy import deepcopy

import xlrd
import numpy

from model.Exit import Exit
from model.Blank import Blank
from model.Floor import Floor
from model.Human import Human
from model.Item import Item
from model.Stair import Stair
import datetime
import random

FLOORS = 5
ROWS = 58 * 1
COLUMNS = 136 * 1
AMOUNT_OF_ANT = 2

start_time = 0

exit_floor = []
connect_floor = []
exits = []  # The position of exit
stairs = []  # The position of stair
available = []  # The position of block which can stand
location_pool = []  # Copy of available to help iterate
louvre_map = numpy.empty([FLOORS, ROWS, COLUMNS], dtype=Item)
humans = numpy.empty(AMOUNT_OF_ANT, dtype=Human)


def automaton():
    global start_time
    start_time = datetime.datetime.now()
    locate_humans()
    print('Locate finish use %d microseconds' % (datetime.datetime.now() - start_time).microseconds)
    start_time = datetime.datetime.now()
    time = 0
    while not is_safe():
        print("iterate %d" % time)
        time += 1
        for human in humans:
            if human.is_safe:
                continue
            f, x, y = human.path[-1]
            print('position: %d, %d, %d' % (f, x, y))
            if isinstance(louvre_map[f][x][y], Floor):
                neighbors = check_neighbor(f, x, y)
                if len(neighbors) == 0:
                    continue
                x_max, y_max = neighbors[0][0], neighbors[0][1]
                for (x_neighbor, y_neighbor) in neighbors[1:]:
                    if louvre_map[f][x_max][y_max].get_probability() < louvre_map[f][x_neighbor][
                        y_neighbor].get_probability():
                        x_max, y_max = x_neighbor, y_neighbor
                print('max: %d, %d' % (x_max, y_max))
                louvre_map[f][x_max][y_max].owner = human
                louvre_map[f][x][y].owner = None
                human.touch((f, x_max, y_max))
            elif isinstance(louvre_map[f][x][y], Stair):
                if louvre_map[f][x][y].toward == louvre_map[f][x][y].h_toward:
                    if louvre_map[f][x][y].touch():
                        if louvre_map[f][x][y].toward == 0 and louvre_map[f - 1][x][y].owner is None:
                            louvre_map[f - 1][x][y].owner = human
                            louvre_map[f][x][y].owner = None
                            louvre_map[f][x][y].current = louvre_map[f][x][y].WAIT_TIME
                            human.touch((f - 1, x, y))
                        elif louvre_map[f][x][y].toward == 1 and louvre_map[f + 1][x][y].owner is None:
                            louvre_map[f + 1][x][y].owner = human
                            louvre_map[f][x][y].owner = None
                            louvre_map[f][x][y].current = louvre_map[f][x][y].WAIT_TIME
                            human.touch((f + 1, x, y))
                else:
                    neighbors = check_neighbor(f, x, y)
                    if len(neighbors) == 0:
                        continue
                    x_max, y_max = neighbors[0][0], neighbors[0][1]
                    for (x_neighbor, y_neighbor) in neighbors[1:]:
                        if louvre_map[f][x_max][y_max].get_probability() < louvre_map[f][x_neighbor][
                            y_neighbor].get_probability():
                            x_max, y_max = x_neighbor, y_neighbor
                    # print('max: %d, %d' % (x_max, y_max))
                    louvre_map[f][x_max][y_max].owner = human
                    louvre_map[f][x][y].owner = None
                    human.touch((f, x_max, y_max))
            elif isinstance(louvre_map[f][x][y], Exit):
                print('\033[0;37;42m out\033[0m')
                exit_human = human
                exit_human.is_safe = True
                louvre_map[f][x][y].owner = None
    print('Evacuation finish use %d seconds' % (datetime.datetime.now() - start_time).seconds)
    start_time = datetime.datetime.now()


def is_safe():
    for human in humans:
        if not human.is_safe: return False
    return True


def check_neighbor(f, x, y):
    neighbors = []
    for (x2, y2) in [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1), (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1),
                     (x - 1, y - 1), ]:
        if x2 < ROWS and y2 < COLUMNS and not isinstance(louvre_map[f][x2][y2], Blank) and louvre_map[f][x2][
            y2].owner is None:
            if len(louvre_map[f][x][y].owner.path) >= 2 and (f, x2, y2) == louvre_map[f][x][y].owner.path[-2]:
                continue
            else:
                neighbors.append((x2, y2))
    return neighbors


def locate_humans():
    global location_pool
    location_pool = available.copy()
    for i in range(AMOUNT_OF_ANT):
        human = Human()
        humans[i] = human
        f, x, y = get_available_position(i)
        human.path.append((f, x, y))
        louvre_map[f][x][y].owner = human
        if i % 1000 == 0: print('Locating %d of %d' % (i, AMOUNT_OF_ANT))


def get_available_position(seed):
    random.seed(seed + datetime.datetime.now().second)
    temp = random.randint(0, len(location_pool) - 1)
    position = location_pool[temp]
    del location_pool[temp]
    return position


def read_data():
    excel = xlrd.open_workbook(r'./data2.xlsx')
    for f in range(FLOORS):
        sheet = excel.sheet_by_index(f)
        for i in range(ROWS):
            for j in range(COLUMNS):
                value = int(sheet.cell(int(i / 1), int(j / 1)).value)
                if value == 1:  # Floor
                    louvre_map[f][i][j] = Floor()
                    available.append((f, i, j))
                elif value == 3:  # Up to down stair
                    louvre_map[f][i][j] = Stair(0)
                    stairs[f].append((i, j))
                    available.append((f, i, j))
                elif value == 4:  # Exit
                    louvre_map[f][i][j] = Exit()
                    exits[f].append((i, j))
                    exit_floor.append(f)
                    available.append((f, i, j))
                elif value == 2:  # Down to up stair
                    louvre_map[f][i][j] = Stair(1)
                    stairs[f].append((i, j))
                    available.append((f, i, j))
                else:
                    louvre_map[f][i][j] = Blank()


def count_heuristic():
    count_exit_floor_stair()
    count_all_floor_stair()
    count_all_floor_floor()


def count_exit_floor_stair():
    for f in exit_floor:
        for (x_stair, y_stair) in stairs[f]:
            for (x_exit, y_exit) in exits[f]:
                louvre_map[f][x_stair][y_stair].set_heuristic(
                    ((x_stair - x_exit) ** 2 + (y_stair - y_exit) ** 2) ** 0.5)
            # exits[f].append((x_stair, y_stair))
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


def count_all_floor_floor():
    for f in range(FLOORS):
        for x in range(ROWS):
            for y in range(COLUMNS):
                if isinstance(louvre_map[f][x][y], Floor):
                    for (x_exit, y_exit) in exits[f]:
                        louvre_map[f][x][y].set_heuristic(
                            ((x - x_exit) ** 2 + (y - y_exit) ** 2) ** 0.5 + louvre_map[f][x_exit][
                                y_exit].heuristic)
                else:
                    continue


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
    all_start_time = datetime.datetime.now()
    start_time = datetime.datetime.now()
    for i in range(FLOORS):
        exits.append([])
        stairs.append([])
    read_data()
    print('Load data finish use %d seconds' % (datetime.datetime.now() - start_time).seconds)
    start_time = datetime.datetime.now()
    count_heuristic()
    print('Calculate finish use %d seconds' % (datetime.datetime.now() - start_time).seconds)
    automaton()
    print('All finish use %d seconds' % (datetime.datetime.now() - all_start_time).seconds)
