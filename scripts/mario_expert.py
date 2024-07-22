"""
This the primary class for the Mario Expert agent. It contains the logic for the Mario Expert agent to play the game and choose actions.

Your goal is to implement the functions and methods required to enable choose_action to select the best action for the agent to take.

Original Mario Manual: https://www.thegameisafootarcade.com/wp-content/uploads/2017/04/Super-Mario-Land-Game-Manual.pdf
"""

import json
import logging
import random

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
    PRESS_A = 5
    PRESS_B = 6

prev_action = Action.RIGHT
already_jumped = False

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

    def find_mario(self, game_area):
        for x in range(len(game_area)):
            for y in range(len(game_area[x])):
                if game_area[x][y] == 1:
                    return (x, y + 1)
        return None  # Return None if 1 is not found

    def check_power_up(self, row, col, game_area):
        # print("checking for power up")
        for row in range(len(game_area)):
            if game_area[row][col] == 13 or game_area[row][col + 1] == 13:
                # print("power up found")
                return True
        # print("power up not found")
        return False

    
    def check_enemy_right(self, row, col, game_area):
        if (game_area[row + 1][col + 1] == 15 or game_area[row + 1][col + 1] == 15):
            print("found enemy")
            return True
        return False
    
    def check_enemy_up(self, row, col, game_area):
        for row in range(len(game_area)):
            if game_area[row][col] == 15:
                return True
        return False
    
    def check_block(self, row, col, game_area):
        if (game_area[row][col + 2] == 14 or game_area[row][col + 2] == 10):
            return True
        return False
    
    def check_jump(self, row, col, game_area):
        # check power up
        if self.check_power_up(row, col, game_area):
            return True
        elif self.check_enemy_right(row, col, game_area):
            return True
        elif self.check_block(row, col, game_area):
            return True
        else:
            return False

    def check_left(self, row, col, game_area):
        if self.check_enemy_up(row, col, game_area):
            return True
        return False
    
    def choose_action(self):
        global prev_action
        global already_jumped
        # global curr_lives
        # global prev_lives
        curr_action = 0

        state = self.environment.game_state()
        game_area = self.environment.game_area()
        print(game_area.shape)
        print(game_area)
        row,col = self.find_mario(game_area) # get game area

        # check which action to perform, defaults to right
        jump = self.check_jump(row, col, game_area)
        left = self.check_left(row, col, game_area)
        
        if prev_action == Action.JUMP:
            curr_action = Action.JUMP        

        elif jump:
            curr_action = Action.JUMP

        elif left:
            curr_action = Action.LEFT

        else:
            curr_action = Action.RIGHT

        if curr_action == Action.JUMP and already_jumped == True:
            already_jumped = False

        prev_action = curr_action # record current action

        print("Action: ", curr_action)

        return curr_action.value  # Return the value of the current action
    
    def step(self):
        """
        Modify this function as required to implement the Mario Expert agent's logic.

        This is just a very basic example
        """

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


    
