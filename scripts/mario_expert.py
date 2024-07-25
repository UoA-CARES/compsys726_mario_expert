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

class Element(Enum):
    GUMBA = 15
    GROUND = 10
    BLOCK = 12
    POWERUP = 13
    PIPE = 14
    PICKUP = 6
    MARIO = 1

row, col = 0, 0
prev_action = Action.RIGHT

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
        This is a very basic example of how this function could be implemented

        As part of this assignment your job is to modify this function to better suit your needs

        You can change the action type to whatever you want or need just remember the base control of the game is pushing buttons
        """

        # Simply toggles the buttons being on or off for a duration of act_freq
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
        return row, col  # Return None if 1 is not found
    
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
                        print(f"Distance to gumba: {distance}")
                        if distance <= 4.0:
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
                if (game_area[a, b] == Element.BLOCK.value or 
                    game_area[a][b] == Element.PIPE.value or
                    (game_area[a][b] == Element.GROUND.value and b > col and a < row)):
                    if b > col:  # If block is to the right of Mario
                        distance = self.get_distance(row, col, a, b)
                        if game_area[a, b] == Element.BLOCK.value:
                            print(f"Distance to block: {distance}")
                        elif game_area[a,b] == Element.GROUND.value:
                            if game_area[a+1,b] == Element.GROUND.value and game_area[a-1,b] == Element.GROUND.value:
                                print(f"Distance to Hill: {distance}")
                                if distance <= 1.0:
                                    return True
                        else:
                            print(f"distance to pipe: {distance}")

                        if distance <= 2.0:
                            return True  # jump over obstacle
        return False

    def check_power_up(self, row, col, game_area):
        x, y = game_area.shape  # x is the number of rows, y is the number of columns
        for b in range(y):  # Iterate over columns
            for a in range(x):  # Iterate over rows
                # Check for blocks
                if game_area[a, b] == Element.POWERUP.value and self.check_on_ground(row, col, game_area) == True:
                    if row >= a and b >= col:  # If power up is to the right and above Mario
                        distance = self.get_distance(row, col, a, b)
                        print(f"Distance to power up: {distance}")
                        if distance <= 3.0:
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
     
    def check_jump(self, row, col, game_area):
        # don't jump again if you're not on the ground
        if self.check_dist_to_ground(row, col, game_area):
            return False 
        # jump over gumba
        elif self.get_gumba_dist(row, col, game_area):
            return True
        # jump to collect power up
        elif self.check_power_up(row, col, game_area):
            return True
        # jump onto a platform
        elif self.check_platform_jump(row, col, game_area):
            return True
        # jump over obstacle
        elif self.check_obstacle(row, col, game_area):
            return True
        else:
            return False

    def check_left(self, row, col, game_area):
        return False
    
    def choose_action(self):
        global prev_action
        global row, col

        curr_action = 0

        state = self.environment.game_state()
        game_area = self.environment.game_area()
        print(game_area)

        row,col = self.find_mario(game_area, row, col) # get game area
        enemy_row, enemy_col = self.find_gumba(game_area)
        
        print(f"Mario loc: {row},{col}")
        print(f"Enemy loc: {enemy_row},{enemy_col}")
        
        # jump over gumba
        if self.get_gumba_dist(row, col, game_area):
            if prev_action == Action.JUMP:
                curr_action = Action.LEFT
            # if gumba is above Mario 
            elif enemy_row < row: 
                curr_action = Action.LEFT
            else:
                curr_action = Action.JUMP
        # jump to collect power up
        elif self.check_power_up(row, col, game_area):
            if prev_action == Action.JUMP:
                curr_action = Action.UP
            else:
                curr_action = Action.JUMP
        # jump onto a platform
        #elif self.check_platform_jump(row, col, game_area):
            #curr_action = Action.JUMP
        # jump over obstacle
        elif self.check_obstacle(row, col, game_area):
            if prev_action == Action.JUMP:
                curr_action = Action.LEFT
            else:
                curr_action = Action.JUMP
        # default to moving right
        else:
            curr_action = Action.RIGHT
        

        prev_action = curr_action # record current action

        print("Action: ", curr_action)

        return curr_action.value  # Return the value of the current action
    
    def step(self):
        """
        Modify this function as required to implement the Mario Expert agent's logic.

        This is just a very basic example
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


    
