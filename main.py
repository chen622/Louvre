from copy import deepcopy
from queue import Queue

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
AMOUNT_OF_ANT = 200

start_time = 0

exit_amount = 0
exit_floor = []
connect_floor = []
exits = []  # The position of exit. e.g. [0:[(1,2)],1:[],2:[],3:[],4:[]]
stairs = []  # The position of stair. e.g. [0:[(1,2)],1:[],2:[],3:[],4:[]]
available = []  # The position of block which can stand. e.g. [(1,2,3),(1,3,4)]
location_pool = []  # Copy of available to help iterate. e.g. [(1,2,3),(1,3,4)]
louvre_map = numpy.empty([FLOORS, ROWS, COLUMNS], dtype=Item)  # e.g. [0:[0:[],1:[]],1:[0:[],1:[]]]
humans = numpy.empty(AMOUNT_OF_ANT, dtype=Human)  # e.g. [human1,human2]


# Use to simulate automaton.
def automaton():
    global start_time, exit_amount
    start_time = datetime.datetime.now()
    locate_humans()
    print('Locate finish use %d microseconds' % (datetime.datetime.now() - start_time).microseconds)
    start_time = datetime.datetime.now()
    time = 0
    while not is_safe():
        print("iterate %d, exits %d/%d" % (time, exit_amount, AMOUNT_OF_ANT))
        time += 1
        for human in humans:  # traversal all the visitor
            if human.is_safe:
                continue
            f, x, y = human.path[-1]
            print('position: %d, %d, %d H=%f' % (f + 1, x + 1, y + 1, louvre_map[f][x][y].heuristic))
            if isinstance(louvre_map[f][x][y], Floor):  # visitor is on a Floor block
                neighbors = check_neighbor(f, x, y)
                if len(neighbors) == 0:
                    continue
                x_max, y_max = neighbors[0][0], neighbors[0][1]
                for (x_neighbor, y_neighbor) in neighbors[1:]:
                    if louvre_map[f][x_max][y_max].get_probability() < louvre_map[f][x_neighbor][
                        y_neighbor].get_probability():
                        x_max, y_max = x_neighbor, y_neighbor
                print('max: %d, %d' % (x_max + 1, y_max + 1))
                louvre_map[f][x_max][y_max].owner = human
                human.path.append((f, x_max, y_max))
                louvre_map[f][x][y].owner = None
                human.touch((f, x_max, y_max))
            elif isinstance(louvre_map[f][x][y], Stair):  # visitor is on a Stair block
                if louvre_map[f][x][y].toward == louvre_map[f][x][y].h_toward:  # visitor should move to another floor
                    if louvre_map[f][x][y].touch():  # visitor should wait or not
                        if louvre_map[f][x][y].toward == 0 and louvre_map[f - 1][x][y].owner is None:  # move to up
                            louvre_map[f - 1][x][y].owner = human
                            louvre_map[f][x][y].owner = None
                            louvre_map[f][x][y].current = louvre_map[f][x][y].WAIT_TIME
                            human.touch((f - 1, x, y))
                        elif louvre_map[f][x][y].toward == 1 and louvre_map[f + 1][x][y].owner is None:  # move to down
                            louvre_map[f + 1][x][y].owner = human
                            louvre_map[f][x][y].owner = None
                            louvre_map[f][x][y].current = louvre_map[f][x][y].WAIT_TIME
                            human.touch((f + 1, x, y))
                else:  # visitor should move to another block in same floor
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
            elif isinstance(louvre_map[f][x][y], Exit):  # visitor arrive exit
                print('\033[0;37;42m out\033[0m')
                exit_human = human
                exit_human.is_safe = True
                louvre_map[f][x][y].owner = None
                exit_amount += 1
    print('Evacuation finish use %d seconds' % (datetime.datetime.now() - start_time).seconds)
    start_time = datetime.datetime.now()


# 迪杰斯特拉算法
def initialGraph():
    graph = numpy.full([FLOORS, ROWS * COLUMNS, ROWS * COLUMNS], 9999, dtype=float)
    for f in range(0, FLOORS - 1):
        for r in range(0, ROWS):
            for c in range(0, COLUMNS):
                if not isinstance(louvre_map[f][r][c], Blank):
                    for neighbor in check_neighbor(f, r, c):
                        if r == neighbor[0] or c == neighbor[1]:
                            graph[f][transfer_to_and(r, c)][transfer_to_and(neighbor[0], neighbor[1])] = 1
                        else:
                            graph[f][transfer_to_and(r, c)][transfer_to_and(neighbor[0], neighbor[1])] = 2
            graph[f][r][r] = 0
    return graph


def Dijkstra_algorithm(graph, v):
    f = v[0]
    r = v[1]
    c = v[2]
    distance = numpy.empty(ROWS * COLUMNS, dtype=float)
    for i in range(0, ROWS * COLUMNS):
        distance[i] = graph[f][transfer_to_and(r, c)][i]

    book = set()  # has visited
    book.add((r, c))
    notBook = []  # has not visited
    # while len(book) < available_floor[f]:
    while True:
        for neighbor in check_neighbor(f, r, c):
            if neighbor not in book and neighbor not in notBook:
                notBook.append(neighbor)
                if distance[transfer_to_and(neighbor[0], neighbor[1])] > distance[transfer_to_and(r, c)] + \
                        graph[f][transfer_to_and(r, c)][transfer_to_and(neighbor[0], neighbor[1])]:
                    distance[transfer_to_and(neighbor[0], neighbor[1])] = distance[transfer_to_and(r, c)] + \
                                                                          graph[f][transfer_to_and(r, c)][
                                                                              transfer_to_and(neighbor[0], neighbor[1])]

        if len(notBook) == 0:
            break
        else:
            item = notBook[0]
            r = item[0]
            c = item[1]
            book.add(item)
            notBook.remove(item)

    return distance


def transfer_to_and(row, column):
    return row * COLUMNS + column


# Determine is all visitor safe.
def is_safe():
    for human in humans:
        if not human.is_safe: return False
    return True


# Get the neighbor which can reach
def check_neighbor(f, x, y):
    neighbors = []
    for (x2, y2) in [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1), (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1),
                     (x - 1, y - 1), ]:
        if x2 >= 0 and x2 < ROWS and y2 >= 0 and y2 < COLUMNS and not isinstance(louvre_map[f][x2][y2], Blank) and \
                louvre_map[f][x2][y2].owner is None:
            neighbors.append((x2, y2))
    return neighbors


# Generate some human into map
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


# Generate position to stand
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
    graph = initialGraph()
    count_exit_floor_stair(graph)
    count_all_floor_stair(graph)
    count_all_floor_floor(graph)


# Calculate the heuristic of stair in floor which has exit
def count_exit_floor_stair(graph):
    for f in exit_floor:
        for (x_stair, y_stair) in stairs[f]:
            distance = Dijkstra_algorithm(graph, (f, x_stair, y_stair))
            change = False
            for (x_exit, y_exit) in exits[f]:
                if louvre_map[f][x_stair][y_stair].set_heuristic(
                    distance[transfer_to_and(x_exit, y_exit)] + louvre_map[f][x_exit][y_exit].heuristic):
                    change = True
            if louvre_map[f][x_stair][y_stair].toward == 0 and louvre_map[f - 1][x_stair][y_stair].heuristic > \
                    louvre_map[f][x_stair][y_stair].heuristic + 15:
                louvre_map[f - 1][x_stair][y_stair].is_down_to_up(louvre_map[f][x_stair][y_stair].heuristic + 15)
                louvre_map[f][x_stair][y_stair].is_down_to_up(louvre_map[f][x_stair][y_stair].heuristic)
                if f - 1 not in connect_floor: connect_floor.append(f - 1)
                exits[f - 1].append((x_stair, y_stair))
            elif louvre_map[f][x_stair][y_stair].toward == 1 and louvre_map[f + 1][x_stair][y_stair].heuristic > \
                    louvre_map[f][x_stair][y_stair].heuristic + 15:
                louvre_map[f + 1][x_stair][y_stair].is_up_to_down(louvre_map[f][x_stair][y_stair].heuristic + 15)
                louvre_map[f][x_stair][y_stair].is_up_to_down(louvre_map[f][x_stair][y_stair].heuristic)
                if f + 1 not in connect_floor: connect_floor.append(f + 1)
                exits[f + 1].append((x_stair, y_stair))
            else:
                if change:
                    if louvre_map[f][x_stair][y_stair].toward == 0:
                        louvre_map[f-1][x_stair][y_stair].h_toward = -1
                    elif louvre_map[f][x_stair][y_stair].toward == 0:
                        louvre_map[f+1][x_stair][y_stair].h_toward = -1
                    louvre_map[f][x_stair][y_stair].h_toward = -1

# Calculate the heuristic of stair in floor which doesn't have exit
def count_all_floor_stair(graph):
    for f in connect_floor:
        for (x_stair, y_stair) in stairs[f]:
            distance = Dijkstra_algorithm(graph, (f, x_stair, y_stair))
            change = False
            for (x_exit, y_exit) in exits[f]:
                if louvre_map[f][x_stair][y_stair].set_heuristic(
                    distance[transfer_to_and(x_exit, y_exit)] + louvre_map[f][x_exit][y_exit].heuristic):
                    change = True
                # louvre_map[f][x_stair][y_stair].set_heuristic(
                #     (((x_stair - x_exit) ** 2 + (y_stair - y_exit) ** 2) ** 0.5) + louvre_map[f][x_exit][
                #         y_exit].heuristic)
            if louvre_map[f][x_stair][y_stair].toward == 0 and louvre_map[f - 1][x_stair][y_stair].heuristic > \
                    louvre_map[f][x_stair][y_stair].heuristic + 15:
                louvre_map[f - 1][x_stair][y_stair].is_down_to_up(louvre_map[f][x_stair][y_stair].heuristic + 15)
                louvre_map[f][x_stair][y_stair].is_down_to_up(louvre_map[f][x_stair][y_stair].heuristic)
                if f - 1 not in connect_floor: connect_floor.append(f - 1)
                exits[f - 1].append((x_stair, y_stair))
            elif louvre_map[f][x_stair][y_stair].toward == 1 and louvre_map[f + 1][x_stair][y_stair].heuristic > \
                    louvre_map[f][x_stair][y_stair].heuristic + 15:
                louvre_map[f + 1][x_stair][y_stair].is_up_to_down(louvre_map[f][x_stair][y_stair].heuristic + 15)
                louvre_map[f][x_stair][y_stair].is_up_to_down(louvre_map[f][x_stair][y_stair].heuristic)
                if f + 1 not in connect_floor: connect_floor.append(f + 1)
                exits[f + 1].append((x_stair, y_stair))
            else:
                if change:
                    if louvre_map[f][x_stair][y_stair].toward == 0:
                        louvre_map[f-1][x_stair][y_stair].h_toward = -1
                    elif louvre_map[f][x_stair][y_stair].toward == 0:
                        louvre_map[f+1][x_stair][y_stair].h_toward = -1
                    louvre_map[f][x_stair][y_stair].h_toward = -1

# Calculate the heuristic of all block
def count_all_floor_floor(graph):
    for f in range(FLOORS):
        for x in range(ROWS):
            for y in range(COLUMNS):
                if isinstance(louvre_map[f][x][y], Floor):
                    # check first top-down second left-right
                    distance = []
                    for (x_exit, y_exit) in exits[f]:
                        should_dijkstra = False
                        if x != x_exit:
                            for x2 in range(x, x_exit, int((x_exit - x) / abs(x_exit - x))):
                                if isinstance(louvre_map[f][x2][y], Blank):
                                    should_dijkstra = True
                                    break
                            if should_dijkstra: continue
                        if y != y_exit:
                            for y2 in range(y, y_exit, int((y_exit - y) / abs(y_exit - y))):
                                if isinstance(louvre_map[f][x2][y2], Blank):
                                    should_dijkstra = True
                                    break
                            if should_dijkstra: continue
                        distance.append(abs(x - x_exit) + abs(y - y_exit) + louvre_map[f][x_exit][y_exit].heuristic)
                    if len(distance) != 0:
                        louvre_map[f][x][y].set_heuristic(min(distance))
                        continue
                    # check first left-right second top-down
                    distance = []
                    for (x_exit, y_exit) in exits[f]:
                        should_dijkstra = False
                        if y != y_exit:
                            for y2 in range(y, y_exit, int((y_exit - y) / abs(y_exit - y))):
                                if isinstance(louvre_map[f][x][y2], Blank):
                                    should_dijkstra = True
                                    break
                            if should_dijkstra: continue
                        if x != x_exit:
                            for x2 in range(x, x_exit, int((x_exit - x) / abs(x_exit - x))):
                                if isinstance(louvre_map[f][x2][y2], Blank):
                                    should_dijkstra = True
                                    break
                            if should_dijkstra: continue
                        distance.append(abs(x - x_exit) + abs(y - y_exit) + louvre_map[f][x_exit][y_exit].heuristic)
                    if len(distance) != 0:
                        louvre_map[f][x][y].set_heuristic(min(distance))
                        continue
                    distance = Dijkstra_algorithm(graph, (f, x, y))
                    for (x_exit, y_exit) in exits[f]:
                        louvre_map[f][x][y].set_heuristic(
                            distance[transfer_to_and(x_exit, y_exit)] + louvre_map[f][x_exit][y_exit].heuristic)
                        # (((x - x_exit) ** 2 + (y - y_exit) ** 2) ** 0.5) + louvre_map[f][x_exit][
                        #     y_exit].heuristic)
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
    print('Load data finish use %d microseconds' % (datetime.datetime.now() - start_time).microseconds)
    start_time = datetime.datetime.now()
    count_heuristic()
    print('Calculate finish use %d seconds' % (datetime.datetime.now() - start_time).seconds)
    automaton()
    print('All finish use %d seconds' % (datetime.datetime.now() - all_start_time).seconds)
