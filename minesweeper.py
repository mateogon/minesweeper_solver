import pyautogui
import time
from window_control import get_window_id, get_window_dimensions, window_to_foreground,send_click,send_mouse_click,move_mouse,click
from displaywindow import DisplayWindow
import keyboard
from enum import Enum
import cv2
import numpy as np
import random
from extras import time_function
import os
import timeit
from PIL import Image, ImageDraw
from io import BytesIO
def timeit_wrapper(func):
    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        end_time = timeit.default_timer()
        execution_time = end_time - start_time
        print(f"Function: {func.__name__} | Execution time: {execution_time} seconds")
        
        return result
    return wrapper

class TileStates(Enum):
    UNREVEALED = 1
    REVEALED_EMPTY = 2
    REVEALED_NUMBERED = 3  # You can add the number as a separate attribute in the tile
    FLAGGED = 4
    QUESTIONED = 5
    MINE = 6


class TileColors(Enum):
    UNREVEALED = (186, 189, 182)
    RELEAVED_EMPTY = (222, 222, 220)
    EXPLODED = (211, 215, 207)
    MINE = (136, 138, 133)
    NUMBERED = {
        1: (221, 250, 195),
        2: (236, 237, 191),
        3: (237, 218, 180),
        4: (237, 195, 138),
        5: (247, 161, 162),
        6: (254, 167, 133),
        7: (255, 125, 96),
        8: (255, 50, 60),
    }


class MineSolver:
    def __init__(self):
        # find the window by its title
        self.window_name = "Mines"
        self.window_id = int(get_window_id(self.window_name), 16)
        self.window = get_window_dimensions(self.window_id)
        self.dw = DisplayWindow(self.window_id)
        # get the dimensions of the window
        self.left, self.top, self.width, self.height = self.window

        # Initialize categories of tiles
        self.unrevealed_tiles = set()
        self.numbered_tiles = set()
        self.empty_tiles = set()
        self.flagged_tiles = set()
        
        self.matrix = False
        self.sqr_width = 50
        self.sqr_height = 50
        self.x_start = 0
        self.x_end = 0
        self.y_start = 0
        self.y_end = 0
        self.row = 0
        self.column = 0
        self.exploded = False
        self.won = False
        self.found_safe_or_flaggable_tiles = False
        self.window_to_foreground()
        time.sleep(0.3)

    def window_to_foreground(self):
        window_to_foreground(self.window_name)

    def init_matrix(self):
        self.matrix = [[]]
        display_screenshot = False
        needle_offset = 2
        # Take a screenshot
        image, width, height = self.dw.take_screenshot()

        for needle_pos in pyautogui.locateAllOnScreen(
            os.getcwd()+"/img/square_corner.png",
            region=self.window,
            confidence=0.95,
        ):
            pos_left = needle_pos.left + needle_offset
            pos_top = needle_pos.top + needle_offset
            pos_width = self.sqr_width
            pos_height = self.sqr_height
            pos = (pos_left, pos_top, pos_width, pos_height)
            # Draw a 1-pixel circle in the center of the box area
            center_x = pos_left + (pos_width // 2)
            center_y = pos_top + (pos_height // 2)
            radius = 1
            cv2.circle(image, (center_x, center_y), radius, (0, 0, 255), -1)

            # print(pos)
            if self.x_start == 0:
                self.x_start = pos[0]
                self.y_start = pos[1]

            else:
                if pos[0] == self.x_start:  # new row
                    self.row += 1
                    self.column = 0
                    self.matrix.append([])
                else:
                    self.column += 1
            tile = {
                "state": TileStates.UNREVEALED,
                "pos": (pos[0], pos[1], self.sqr_width, self.sqr_height),
                "number": -1,
                "column": self.column,
                "row": self.row,
            }
            self.matrix[self.row].append(tile)
            self.unrevealed_tiles.add((self.row, self.column))
            self.x_end = pos[0]
            self.y_end = pos[1]
            
        #cv2.imshow("Screenshot with Circles", image)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
            
    def reset_matrix(self):
        self.unrevealed_tiles = set()
        self.numbered_tiles = set()
        self.empty_tiles = set()
        self.flagged_tiles = set()
        self.exploded = False
        self.won = False
        for row in range(len(self.matrix)):
            for column in range(len(self.matrix[row])):
                self.matrix[row][column]["state"] = TileStates.UNREVEALED
                self.matrix[row][column]["number"] = -1
                self.unrevealed_tiles.add((self.row, self.column))
                
    def click_tile(self, column, row):
        x,y = pyautogui.center(self.matrix[row][column]["pos"])
        click(self.dw.d,x,y,1)
        #
        #pyautogui.click(center)

    def right_click_tile(self, column, row):
        x,y = pyautogui.center(self.matrix[row][column]["pos"])
        click(self.dw.d,x,y,3)
        #pyautogui.rightClick(center)
        
    #@timeit_wrapper
    def update_matrix(self):
        self.found_safe_or_flaggable_tiles = False
        #screenshot = pyautogui.screenshot()
        for set_tile in self.unrevealed_tiles.copy():
            tile = self.matrix[set_tile[0]][set_tile[1]]
            row = tile["row"]
            column = tile["column"]
            pos = tile["pos"]
            # offset to avoid the black number at the center
            offset_x = pos[2] // (1.2)
            offset_y = pos[3] // 2
            color = self.dw.get_pixel_rgb((pos[0] + offset_x, pos[1] + offset_y))
            if (row,column) in self.flagged_tiles:
                tile["state"] = TileStates.FLAGGED
                self.unrevealed_tiles.remove(set_tile)
            elif color == TileColors.EXPLODED.value:
                tile["state"] = TileStates.MINE
                    
            elif color == TileColors.MINE.value:
                tile["state"] = TileStates.MINE
                self.exploded = True
            elif color in TileColors.NUMBERED.value.values():
                tile["state"] = TileStates.REVEALED_NUMBERED
                tile["number"] = list(TileColors.NUMBERED.value.keys())[
                    list(TileColors.NUMBERED.value.values()).index(color)
                ]
                self.unrevealed_tiles.remove(set_tile)
                self.numbered_tiles.add(set_tile)
            elif color == TileColors.RELEAVED_EMPTY.value:
                tile["state"] = TileStates.REVEALED_EMPTY
                self.unrevealed_tiles.remove(set_tile)
                self.empty_tiles.add(set_tile)
            else:
                pass
                #print("Unknown color: ", color)
                #print("tile row,col: ", row, column)

    def print_matrix(self):
        tile_state_symbols = {
            TileStates.UNREVEALED: "?",
            TileStates.REVEALED_EMPTY: " ",
            TileStates.REVEALED_NUMBERED: "N",  # We will replace this with the actual number later
            TileStates.FLAGGED: "F",
            TileStates.QUESTIONED: "Q",
            TileStates.MINE: "M",
        }

        for row in self.matrix:
            for tile in row:
                symbol = tile_state_symbols[tile["state"]]
                # If this is a numbered tile, replace the "N" symbol with the actual number
                if tile["state"] == TileStates.REVEALED_NUMBERED:
                    symbol = str(tile["number"])
                print(symbol, end=" ")
            print()  # Newline at the end of each row
    #@timeit_wrapper
    def reveal_safe_tiles(self):
        for set_tile in self.numbered_tiles:
            tile = self.matrix[set_tile[0]][set_tile[1]]
            row = tile["row"]
            column = tile["column"]
            neighbors = self.get_neighbors(row, column)
            flagged_neighbors = [
                (t, t_row, t_column)
                for t, t_row, t_column in neighbors
                if t["state"] == TileStates.FLAGGED
            ]
            unrevealed_neighbors = [
                (t, t_row, t_column)
                for t, t_row, t_column in neighbors
                if t["state"] == TileStates.UNREVEALED
            ]

            if len(flagged_neighbors) == tile["number"]:
                if len(unrevealed_neighbors) > 0:
                    self.found_safe_or_flaggable_tiles = True
                # All other unrevealed tiles are safe
                for t, t_row, t_column in unrevealed_neighbors:
                    self.click_tile(t_column, t_row)
                    
    #@timeit_wrapper
    def get_neighbors(self, row, column):
        neighbors = []
        for i in range(max(0, row - 1), min(len(self.matrix), row + 2)):
            for j in range(max(0, column - 1), min(len(self.matrix[0]), column + 2)):
                if i != row or j != column:
                    neighbors.append((self.matrix[i][j], i, j))
        return neighbors
    #@timeit_wrapper
    def flag_mines(self):
        for set_tile in self.numbered_tiles:
            tile = self.matrix[set_tile[0]][set_tile[1]]
            row = tile["row"]
            column = tile["column"]
            neighbors = self.get_neighbors(row, column)
            flagged_neighbors = [
                (t, t_row, t_column)
                for t, t_row, t_column in neighbors
                if t["state"] == TileStates.FLAGGED
            ]
            unrevealed_neighbors = [
                (t, t_row, t_column)
                for t, t_row, t_column in neighbors
                if t["state"] == TileStates.UNREVEALED
            ]

            if tile["number"] - len(flagged_neighbors) == len(unrevealed_neighbors):
                if len(unrevealed_neighbors) > 0:
                    self.found_safe_or_flaggable_tiles = True
                # All unrevealed tiles are mines
                for t, t_row, t_column in unrevealed_neighbors:
                    self.matrix[t_row][t_column]["state"] = TileStates.FLAGGED
                    self.right_click_tile(t_column, t_row)
                    self.unrevealed_tiles.remove((t_row, t_column))
                    self.flagged_tiles.add((t_row, t_column))
    def score_tile(self, row, column):
        neighbors = self.get_neighbors(row, column)
        flagged_neighbors = [
            (t, t_row, t_column)
            for t, t_row, t_column in neighbors
            if t["state"] == TileStates.FLAGGED
        ]
        return len(flagged_neighbors)

    def click_random_tile(self):
        unrevealed_tiles = [
            (t, t_row, t_column)
            for t_row, row in enumerate(self.matrix)
            for t_column, t in enumerate(row)
            if t["state"] == TileStates.UNREVEALED
        ]
        if unrevealed_tiles:
            if not self.numbered_tiles and not self.empty_tiles:  # if both sets are empty
                # calculate the center of the grid
                center_x = len(self.matrix[0]) // 2
                center_y = len(self.matrix) // 2

                # find all tiles within a certain radius of the center
                center_tiles = [
                    (t, t_row, t_column)
                    for t, t_row, t_column in unrevealed_tiles
                    if abs(t_row - center_y) <= 2 and abs(t_column - center_x) <= 2
                ]

                # if there are any tiles near the center, choose one of them at random
                if center_tiles:
                    t, t_row, t_column = random.choice(center_tiles)
                else:  # otherwise, just choose a random unrevealed tile
                    t, t_row, t_column = random.choice(unrevealed_tiles)
            else:
                scored_tiles = [(t, t_row, t_column, self.score_tile(t_row, t_column)) for t, t_row, t_column in unrevealed_tiles]
                scored_tiles.sort(key=lambda x: x[3])
                t, t_row, t_column, _ = scored_tiles[0]  # select the tile with the lowest score
            self.click_tile(t_column, t_row)
        else:
            print("YOU WIN!")
            self.won = True

    def print_colors(self):
        #screenshot = pyautogui.screenshot()
        for row in range(len(self.matrix)):
            for column in range(len(self.matrix[row])):
                tile = self.matrix[row][column]
                pos = tile["pos"]
                # offset to avoid the black number at the center
                offset_x = pos[2] // (1.2)

                offset_y = pos[3] // 2

                #color = screenshot.getpixel((pos[0] + offset_x, pos[1] + offset_y))
                color = self.dw.get_pixel_rgb((pos[0] + offset_x, pos[1] + offset_y))
                #print("Unknown color: ", color)
                #print("tile row,col: ", row, column)

# main loop
solver = MineSolver()
loop = True
'''for x in range(0,solver.width):
    for y in range(0,solver.height):
        color = solver.dw.get_pixel_rgb((x, y))
        print("color: ", color, "x,y: ", x, y)'''
loops = 0
max_loops = 100000
while loop:
    if keyboard.is_pressed("{"):
        if not solver.matrix:
            solver.init_matrix()
        elif solver.exploded or solver.won:
            solver.reset_matrix()
        while True:
            if loops > max_loops:
                print("max loops reached")
                loop = False
                break
            print("looping")
            solver.update_matrix()
            #solver.print_matrix()
            solver.flag_mines()
            time.sleep(0.05)
            solver.reveal_safe_tiles()
            time.sleep(0.05)
            print("found safe or flaggable tiles: ", solver.found_safe_or_flaggable_tiles)
            if not solver.found_safe_or_flaggable_tiles:
                print("clicking random tile")
                solver.click_random_tile()
                solver.update_matrix()
                
            if solver.exploded:
                print("Game over")
                break
            if solver.won:
                print("YOU WIN!")
                break
            if keyboard.is_pressed("}"):
                loop = False
                break
            loops+=1
