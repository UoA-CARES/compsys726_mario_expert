"""
This the primary class for the Mario Expert agent. It contains the logic for the Mario Expert agent to play the game and choose actions.

Your goal is to implement the functions and methods required to enable choose_action to select the best action for the agent to take.

Original Mario Manual: https://www.thegameisafootarcade.com/wp-content/uploads/2017/04/Super-Mario-Land-Game-Manual.pdf
"""

import json
import logging
import random
import math

import cv2
from mario_environment import MarioEnvironment
from pyboy.utils import WindowEvent
from enum import Enum

class Action(Enum):
    DOWN = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    JUMP = 4
    PRESS_B = 5
    JUMP_OBS = 6
    JUMP_EMPTY = 7
    JUMP_POWER_UP = 8
    JUMP_SKIP_ENEMY = 9
    JUMP_RIGHT = 10
    ENEMY_LEFT = 11

class Element(Enum):
    GUMBA = 15
    GROUND = 10
    BLOCK = 12
    POWERUP = 13
    PIPE = 14
    PICKUP = 6
    MARIO = 1
    EMPTY = 0
    TOAD = 16
    FLY = 18

row, col = 0, 0
prev_action = Action.RIGHT
next_action = Action.RIGHT

class MarioController(MarioEnvironment):
    """
    The MarioController class represents a controller for the Mario game environment.

    You can build upon this class all you want to implement your Mario Expert agent.

    Args:
        act_freq (int): The frequency at which actions are performed. Defaults to 10.
        emulation_speed (int): The speed of the game emulation. Defaults to 0.
        headless (bool): Whether to run the game in headless mode. Defaults to False.
    """

    def __init__(
        self,
        act_freq: int = 10,
        emulation_speed: int = 0,
        headless: bool = False,
    ) -> None:
        super().__init__(
            act_freq=act_freq,
            emulation_speed=emulation_speed,
            headless=headless,
        )

        self.act_freq = act_freq

        # Example of valid actions based purely on the buttons you can press
        valid_actions: list[WindowEvent] = [
            WindowEvent.PRESS_ARROW_DOWN,
            WindowEvent.PRESS_ARROW_LEFT,
            WindowEvent.PRESS_ARROW_RIGHT,
            WindowEvent.PRESS_ARROW_UP,
            WindowEvent.PRESS_BUTTON_A,
            WindowEvent.PRESS_BUTTON_B,
        ]

        release_button: list[WindowEvent] = [
            WindowEvent.RELEASE_ARROW_DOWN,
            WindowEvent.RELEASE_ARROW_LEFT,
            WindowEvent.RELEASE_ARROW_RIGHT,
            WindowEvent.RELEASE_ARROW_UP,
            WindowEvent.RELEASE_BUTTON_A,
            WindowEvent.RELEASE_BUTTON_B,
        ]

        self.valid_actions = valid_actions
        self.release_button = release_button

    def run_action(self, action: int) -> None:
        """
        Runs actions by pushing buttons for a set period of time. Certain actions can be pressed for longer, with different codes corresponding to each case.
        Action.JUMP <= Action.JUMP_OBS (jump obstacle)
        """
        # extended hold duration when jumping over obstacles
        if action == Action.JUMP_OBS.value:
            self.pyboy.send_input(self.valid_actions[Action.JUMP.value])
            for _ in range(self.act_freq*10):
                self.pyboy.tick()

            action = Action.JUMP.value
            #self.pyboy.send_input(self.release_button[action])

        elif action == Action.JUMP_POWER_UP.value:
            self.pyboy.send_input(self.valid_actions[Action.JUMP.value])
            for _ in range(self.act_freq):
                self.pyboy.tick()
            
            action = Action.JUMP.value
            #self.pyboy.send_input(self.release_button[action])
        elif action == Action.JUMP_EMPTY.value:
            self.pyboy.send_input(self.valid_actions[Action.JUMP.value])
            self.pyboy.send_input(self.valid_actions[Action.RIGHT.value])
            for _ in range(self.act_freq * 5):
                self.pyboy.tick()
            
            print("releasing right jump empty")
            self.pyboy.send_input(self.release_button[Action.RIGHT.value])            
            action = Action.JUMP.value

        elif action == Action.ENEMY_LEFT.value:
            self.pyboy.send_input(self.valid_actions[Action.LEFT.value])
            time = int(self.act_freq)
            for _ in range(time):
                self.pyboy.tick()
            
            print("releasing enemy left ")
            action = Action.LEFT.value
            
        elif action == Action.JUMP_SKIP_ENEMY.value:
            self.pyboy.send_input(self.valid_actions[Action.JUMP.value])
            self.pyboy.send_input(self.valid_actions[Action.RIGHT.value])
            for _ in range(self.act_freq * 2):
                self.pyboy.tick()
            self.pyboy.send_input(self.release_button[Action.RIGHT.value])
            action = Action.JUMP.value
        
        elif action == Action.JUMP_RIGHT.value:
            # normal jump right with normal button press timings
            self.pyboy.send_input(self.valid_actions[Action.JUMP.value])
            self.pyboy.send_input(self.valid_actions[Action.RIGHT.value])
            for _ in range(self.act_freq):
                self.pyboy.tick()
            self.pyboy.send_input(self.release_button[Action.RIGHT.value])
            action = Action.JUMP.value

        else:
            # normal hold duration on all other inputs
            self.pyboy.send_input(self.valid_actions[action])
            for _ in range(self.act_freq):
                self.pyboy.tick()

        self.pyboy.send_input(self.release_button[action])

class MarioExpert:
    """
    The MarioExpert class represents an expert agent for playing the Mario game.

    Edit this class to implement the logic for the Mario Expert agent to play the game.

    Do NOT edit the input parameters for the __init__ method.

    Args:
        results_path (str): The path to save the results and video of the gameplay.
        headless (bool, optional): Whether to run the game in headless mode. Defaults to False.
    """

    def __init__(self, results_path: str, headless=False):
        self.results_path = results_path

        self.environment = MarioController(headless=headless)

        self.video = None

    def get_distance(self, row0, col0, row1, col1):
        return math.sqrt(((col1-col0) * (col1-col0)) + ((row1-row0) * (row1-row0))) # pythagoras

    """
    Checks surroundings of Mario, to see if he's in the air. Returns true if all surrounding values are the same
    """
    def check_surrounding(self, row, col, game_area, value):
        print(f"checking surrounding for {value}")
        return (game_area[row - 1][col - 2] == value and
                game_area[row - 1][col - 1] == value and
                game_area[row - 1][col] == value and
                game_area[row - 1][col + 1] == value and
                game_area[row][col - 2] == value and
                game_area[row][col + 1] == value and
                game_area[row + 1][col - 2] == value and
                game_area[row + 1][col + 1] == value and
                game_area[row + 2][col - 2] == value and
                game_area[row + 2][col - 1 == value] and
                game_area[row + 2][col] == value and
                game_area[row + 2][col + 1] == value)

    """
    Gets mario's position, returns the top right corner of Mario
    11 <- this one
    11
    """
    def find_mario(self, game_area, row, col):
        x, y = game_area.shape
        for a in range(x):
            for b in range(y):
                if game_area[a][b] == 1:
                    return (a, b + 1)
        return 0, 0  # if mario is not found
    
    def find_gumba(self, game_area):
        x,y = game_area.shape
        for a in range(x):
            for b in range(y):
                if game_area[a][b] == Element.GUMBA.value:
                    return (a, b)
        return 0,0
    
    def get_gumba_dist(self, row, col, game_area):
        x, y = game_area.shape  # x is the number of rows, y is the number of columns
        for b in range(y):  # Iterate over columns
            for a in range(x):  # Iterate over rows
                # Check for blocks
                if game_area[a, b] == Element.GUMBA.value:
                    # Compute distance
                    if b >= col:  # If gumba is to the right of Mario
                        distance = self.get_distance(row, col, a, b)
                        return distance
        return 10000
    
    def get_toad_dist(self, row, col, game_area):
        x, y = game_area.shape  # x is the number of rows, y is the number of columns
        for b in range(y):  # Iterate over columns
            for a in range(x):  # Iterate over rows
                # Check for blocks
                if game_area[a, b] == Element.TOAD.value:
                    # Compute distance
                    if b >= col:  # If gumba is to the right of Mario
                        distance = self.get_distance(row, col, a, b)
                        print(f"Distance to toad: {distance}")
                        if distance <= 4:
                            return True
        return False
    
    def get_fly_dist(self, row, col, game_area):
        x, y = game_area.shape  # x is the number of rows, y is the number of columns
        for b in range(y):  # Iterate over columns
            for a in range(x):  # Iterate over rows
                # Check for blocks
                if game_area[a, b] == Element.FLY.value:
                    # Compute distance
                    if b >= col:  # If gumba is to the right of Mario
                        distance = self.get_distance(row, col, a, b)
                        print(f"Distance to fly: {distance}")
                        if distance <= 3:
                            return True
        return False

    def check_platform_jump(self, row, col, game_area):
        x, y = game_area.shape  # x is the number of rows, y is the number of columns
        for b in range(y):  # Iterate over columns
            for a in range(x):  # Iterate over rows
                # Check for blocks
                if game_area[a, b] == Element.BLOCK.value:
                    # Compute distance
                    if a < row and b > col:  # If block is above and to the right of Mario
                        distance = self.get_distance(row, col, a, b)
                        print(f"distance to platform: {distance}")
                        if distance <= 7.0:
                            return True  # Found platform to jump on
        return False

    """
    Check for obstacle to jump over
    """
    def check_obstacle(self, row, col, game_area):
        x, y = game_area.shape  # x is the number of rows, y is the number of columns
        for b in range(y):  # Iterate over columns
            for a in range(x):  # Iterate over rows
                # Check for blocks or pipes
                if (game_area[a][b] == Element.BLOCK.value or 
                    game_area[a][b] == Element.PIPE.value or
                    (game_area[a][b] == Element.GROUND.value and b > col and a < row)):
                    if b > col:  # If block is to the right of Mario
                        distance = self.get_distance(row, col, a, b)
                        if game_area[a, b] == Element.BLOCK.value:
                            if game_area[a+1,b] == Element.BLOCK.value and game_area[a-1,b] == Element.BLOCK.value:
                                print(f"Distance to block: {distance}")
                        elif game_area[a,b] == Element.GROUND.value:
                            if game_area[a+1,b] == Element.GROUND.value and game_area[a-1,b] == Element.GROUND.value:
                                print(f"Distance to Hill: {distance}")
                                if distance <= 1.0:
                                    return True
                        elif game_area[a,b] == Element.PIPE.value:
                            print(f"distance to pipe: {distance}")

                        if distance <= 2.0:
                            return True  # jump over obstacle
        return False

    def check_empty_jump(self, row, col, game_area):
        x, y = game_area.shape  # x is the number of rows, y is the number of columns
        for b in range(y):  # Iterate over columns
            for a in range(x):  # Iterate over rows
                # Check for empty to the right below mario
                if (game_area[a][b] == Element.EMPTY.value and (a == row+2) and (b > col)):  
                        # check if ground is wide enough
                        if ((game_area[a][b-1] == Element.GROUND.value and
                            game_area[a][b-2] == Element.GROUND.value and
                            game_area[a][b-3] == Element.GROUND.value) or 
                            (game_area[a][b-1] == Element.BLOCK.value and
                            game_area[a][b-2] == Element.BLOCK.value and
                            game_area[a][b-3] == Element.BLOCK.value) and
                            (game_area[a-1][b-1]) in [0, 1]):
                            # If ground is to the right and below of Mario and block next to it is ground
                            print(f"Empty loc: {a},{b}")
                            distance = self.get_distance(row, col, a, b)
                            print(f"Distance to empty: {distance}")
                            if distance <= 2.5:
                                return True  # jump over empty
        return False

    def check_power_up(self, row, col, game_area):
        x, y = game_area.shape  # x is the number of rows, y is the number of columns
        for b in range(y):  # Iterate over columns
            for a in range(x):  # Iterate over rows
                # Check for blocks
                if game_area[a, b] == Element.POWERUP.value and self.check_on_ground(row, col, game_area) == True:
                    if row >= a and b >= col:  # If power up is to the right and above Mario
                        distance = self.get_distance(row, col, a, b)
                        print(f"Distance to power up: {distance}") # reduce distance?????
                        if distance <= 3.0 and game_area[row+2,col] == Element.GROUND.value:
                            return True
                        return False # missed power up
                    
    def check_on_ground(self, row, col, game_area):
        x, y = game_area.shape
        for b in range(y):  # Iterate over columns
            for a in range(x):  # Iterate over rows
                # Check for blocks
                if game_area[a, b] == Element.GROUND.value:
                    if col == b:  # If ground is under Mario
                        # check adjacent squares for ground
                        if game_area[a,b+1] == Element.GROUND.value and game_area[a][b-1] == Element.GROUND.value:
                            return True
        return False
    
    
    def choose_action(self):
        global prev_action, next_action
        global row, col

        curr_action = 0
        state = self.environment.game_state()
        game_area = self.environment.game_area()
        print(game_area)

        row,col = self.find_mario(game_area, row, col) # get game area
        enemy_row, enemy_col = self.find_gumba(game_area)

        print(f"prev_action: {prev_action}")
        print(f"Mario loc: {row},{col}")
        print(f"Enemy loc: {enemy_row},{enemy_col}")
        distance = self.get_gumba_dist(row, col, game_area)
        print(f"enemy distance: {distance}")
        
        if self.check_empty_jump(row, col, game_area):
            if prev_action == Action.JUMP_EMPTY:
                print("jump over empty")
                curr_action = Action.RIGHT
            else:
                curr_action = Action.JUMP_EMPTY
        
        elif game_area[row+2][col] == Element.PIPE.value:
                if(prev_action in [Action.JUMP, Action.JUMP_EMPTY, Action.JUMP_OBS, Action.JUMP_POWER_UP]):
                    curr_action = Action.UP
                    print("up pipe")
                else:
                    print("jump off pipe")
                    curr_action = Action.JUMP_EMPTY

        elif (row + 2 < enemy_row and
                  enemy_row != 0 and 
                  prev_action == Action.RIGHT and
                  (game_area[row+2][col] != Element.EMPTY.value and
                   distance < 7)): 
                print("jump skip over enemy")
                curr_action = Action.JUMP_EMPTY

        elif self.get_gumba_dist(row, col, game_area) <= 4.5:
            distance = self.get_gumba_dist(row, col, game_area) 
            print(f"gumba dist < 4.5: {distance}")
            # normal case
            if prev_action == Action.RIGHT:
                curr_action = Action.JUMP # jump over gumba
            # edge cases
            # mario too close to gumba, just skip gumba
            elif prev_action == Action.ENEMY_LEFT and distance < 2 and distance > 1.5:
                curr_action = Action.JUMP_SKIP_ENEMY
            # if prev action was jump, can't jump again
            elif prev_action == Action.ENEMY_LEFT and distance >= 1.5:
                # can jump over enemy now, needs to jump to the right
                # print("jump right")
                curr_action = Action.JUMP

            # mario just jumped or in air
            elif prev_action == Action.JUMP:
                if distance < 4:
                    # safe to move left
                    print("gumba left")
                    curr_action = Action.ENEMY_LEFT
                else:
                    curr_action = Action.JUMP_RIGHT
            
            else:
                curr_action = Action.JUMP

        elif self.get_toad_dist(row, col, game_area):
            print("toad left")
            if prev_action == Action.JUMP:
                curr_action = Action.LEFT
            # if gumba is above Mario 
            #elif enemy_row < row and enemy_row != 0: 
                #curr_action = Action.LEFT
            else:
                curr_action = Action.JUMP

        elif self.get_fly_dist(row, col, game_area):
            if prev_action == Action.JUMP:
                print("fly left")
                curr_action = Action.LEFT
            # if gumba is above Mario 
            #elif enemy_row < row and enemy_row != 0: 
                #curr_action = Action.LEFT
            else:
                curr_action = Action.JUMP

        # jump to collect power up
        elif self.check_power_up(row, col, game_area):
            if(prev_action == Action.JUMP_POWER_UP):
                print("Power up right")
                curr_action = Action.RIGHT
            elif prev_action == Action.JUMP:
                curr_action = Action.UP # stop so that mario can check for power ups
            else:
                curr_action = Action.JUMP_POWER_UP

         # jump over obstacle
        elif self.check_obstacle(row, col, game_area):
            if prev_action == Action.JUMP_OBS:
                print("jump over obstacle")
                curr_action = Action.RIGHT
            else:
                curr_action = Action.JUMP_OBS
        
        # elif self.check_platform_jump(row, col, game_area):
        #     if prev_action == Action.JUMP_OBS:
        #         print("jump onto platform")
        #         curr_action = Action.JUMP_OBS
        #     else:
        #         curr_action = Action.JUMP
        

        # if walked off a ledge without jumping
        #elif self.check_surrounding(row, col, game_area, Element.EMPTY.value) and prev_action == Action.RIGHT:
        #    curr_action = Action.LEFT

        elif row == 0:
            curr_action = Action.UP  # when mario is off screen/ dead, move up
        else:
            curr_action = Action.RIGHT
        

        prev_action = curr_action # record current action

        print("Action: ", curr_action)

        return curr_action.value  # Return the value of the current action
    
    def step(self):
        """
        Runs each step of the game
        """
        input("Press enter to continue") # for testing
        # Choose an action - button press or other...
        action = self.choose_action()
        # Run the action on the environment
        self.environment.run_action(action)

    def play(self):
        """
        Do NOT edit this method.
        """
        self.environment.reset()

        frame = self.environment.grab_frame()
        height, width, _ = frame.shape

        self.start_video(f"{self.results_path}/mario_expert.mp4", width, height)

        while not self.environment.get_game_over():
            frame = self.environment.grab_frame()
            self.video.write(frame)

            self.step()

        final_stats = self.environment.game_state()
        logging.info(f"Final Stats: {final_stats}")

        with open(f"{self.results_path}/results.json", "w", encoding="utf-8") as file:
            json.dump(final_stats, file)

        self.stop_video()

    def start_video(self, video_name, width, height, fps=30):
        """
        Do NOT edit this method.
        """
        self.video = cv2.VideoWriter(
            video_name, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )

    def stop_video(self) -> None:
        """
        Do NOT edit this method.
        """
        self.video.release()


    