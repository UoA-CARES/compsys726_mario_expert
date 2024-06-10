"""
DO NOT EDIT THIS CLASS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
DO NOT EDIT THIS CLASS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
DO NOT EDIT THIS CLASS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
DO NOT EDIT THIS CLASS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
DO NOT EDIT THIS CLASS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
DO NOT EDIT THIS CLASS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""

import numpy as np

from pyboy_environment import PyboyEnvironment


class MarioEnvironment(PyboyEnvironment):
    """
    This is a base class for the MarioEnvironment.

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

    def game_state(self) -> dict[str, any]:
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
        }

    ############################################################################################################
    # Useful functions to extract the game state - add additional ones in MarioController NOT HERE             #
    #                                                                                                          #
    # The link below has all the ROM memory data for Super Mario Land.                                         #
    # It is used to extract the game state for the MarioEnvironment class.                                     #
    #                                                                                                          #
    # https://datacrystal.tcrf.net/wiki/Super_Mario_Land/RAM_map                                               #
    #                                                                                                          #
    # https://www.thegameisafootarcade.com/wp-content/uploads/2017/04/Super-Mario-Land-Game-Manual.pdf         #
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
