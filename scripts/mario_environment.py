"""
The link below has all the ROM memory data for Super Mario Land. 
It is used to extract the game state for the MarioEnvironment class.

https://datacrystal.tcrf.net/wiki/Super_Mario_Land/RAM_map

https://www.thegameisafootarcade.com/wp-content/uploads/2017/04/Super-Mario-Land-Game-Manual.pdf
"""

from abc import ABCMeta
from pathlib import Path

import cv2
import numpy as np
from pyboy import PyBoy
from pyboy.utils import WindowEvent

from pyboy_environment import PyboyEnvironment


class MarioEnvironment(PyboyEnvironment):
    """
    This is a base class for the MarioEnvironment.

    It is recommended that you add your own functions to this class to better suit your needs

    https://datacrystal.tcrf.net/wiki/Super_Mario_Land/RAM_map
    """

    def __init__(
        self,
        act_freq: int = 10,
        emulation_speed: int = 0,
        headless: bool = False,
    ) -> None:

        super().__init__(
            task="mario",
            rom_name="SuperMarioLand.gb",
            init_name="init.state",
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

    def game_state(self) -> dict[str, int]:
        """
        This is an example of how you could extract the game state

        You can add to this list for your purposes but do NOT remove any of these
        """
        return {
            "lives": self.get_lives(),  # DO NOT REMOVE
            "score": self.get_score(),  # DO NOT REMOVE
            "coins": self.get_coins(),  # DO NOT REMOVE
            "stage": self.get_stage(),  # DO NOT REMOVE
            "world": self.get_world(),  # DO NOT REMOVE
            "x_position": self.get_x_position(),  # DO NOT REMOVE
            "time": self.get_time(),  # DO NOT REMOVE
            "dead_timer": self.get_dead_timer(),  # DO NOT REMOVE
            "dead_jump_timer": self.get_dead_jump_timer(),  # DO NOT REMOVE
            "game_over": self.get_game_over(),  # DO NOT REMOVE
            # Add more here if you wish
        }

    ############################################################################################################
    # Useful functions to extract the game state - you can add more if you want but do NOT edit these functions#
    ############################################################################################################
    def game_area(self) -> np.ndarray:
        mario = self.pyboy.game_wrapper
        mario.game_area_mapping(mario.mapping_compressed, 0)
        return mario.game_area()

    def get_time(self):
        hundreds = self._read_m(0x9831)
        tens = self._read_m(0x9832)
        ones = self._read_m(0x9833)
        return int(str(hundreds) + str(tens) + str(ones))

    def get_lives(self):
        return self._read_m(0xDA15)

    def get_score(self):
        mario = self.pyboy.game_wrapper
        return mario.score

    def get_coins(self):
        return self._read_m(0xFFFA)

    def get_stage(self):
        return self._read_m(0x982E)

    def get_world(self):
        return self._read_m(0x982C)

    def get_game_over(self):
        return self._read_m(0xC0A4) == 0x39

    def get_mario_pose(self):
        return self._read_m(0xC203)

    def get_dead_timer(self):
        return self._read_m(0xFFA6)

    def get_dead_jump_timer(self):
        return self._read_m(0xC0AC)

    def get_x_position(self):
        # Copied from: https://github.com/lixado/PyBoy-RL/blob/main/AISettings/MarioAISettings.py
        # Do not understand how this works...
        level_block = self._read_m(0xC0AB)
        mario_x = self._read_m(0xC202)
        scx = self.pyboy.screen.tilemap_position_list[16][0]
        real = (scx - 7) % 16 if (scx - 7) % 16 != 0 else 16
        real_x_position = level_block * 16 + real + mario_x
        return real_x_position
