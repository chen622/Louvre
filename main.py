import xlrd
import numpy

from model.Blank import Blank
from model.Floor import Floor
from model.Item import Item
from model.Stair import Stair


def read_data():
    excel = xlrd.open_workbook(r'./data.xlsx')
    map = numpy.empty([2, 3], dtype=Item)
    for sheet in excel.sheets():
        for i in range(2):
            for j in range(3):
                value = int(sheet.cell(i, j).value)
                map[i][j] = Floor() if value == 1 else (Stair() if value == 2 else Blank())
    for row in map:
        for value in row:
            if isinstance(value, Floor):
                print('\033[0;31m1\033[0;31m')
            elif isinstance(value, Stair):
                print('\033[0;32m2\033[0;32m')
            else:
                print(3)


if __name__ == '__main__':
    read_data()
