from abc import ABCMeta
from pathlib import Path

import cv2
import numpy as np
from pyboy import PyBoy


class PyboyEnvironment(metaclass=ABCMeta):
    """
    This is a base class for the PyboyEnvironment.

    Do NOT Modify this Class
    """

    def __init__(
        self,
        task: str,
        rom_name: str,
        init_name: str,
        emulation_speed: int = 0,
        headless: bool = False,
    ) -> None:
        self.task = task

        path = f"{Path(__file__).parent.parent}/roms"

        self.rom_path = f"{path}/{self.task}/{rom_name}"
        self.init_path = f"{path}/{self.task}/{init_name}"

        head = "null" if headless else "SDL2"
        self.pyboy = PyBoy(
            self.rom_path,
            window=head,
        )

        self.screen = self.pyboy.screen

        self.pyboy.set_emulation_speed(emulation_speed)

        self.reset()

    def grab_frame(self, height: int = 240, width: int = 300) -> np.ndarray:
        frame = np.array(self.screen.ndarray)
        frame = cv2.resize(frame, (width, height))
        # Convert to BGR for use with OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame

    def reset(self) -> np.ndarray:
        with open(self.init_path, "rb") as f:
            self.pyboy.load_state(f)

    def game_area(self) -> np.ndarray:
        raise NotImplementedError("Implement in subclass")

    def _read_m(self, addr: int) -> int:
        return self.pyboy.memory[addr]

    def _read_bit(self, addr: int, bit: int) -> bool:
        # add padding so zero will read '0b100000000' instead of '0b0'
        return bin(256 + self._read_m(addr))[-bit - 1] == "1"

    # built-in since python 3.10
    def _bit_count(self, bits: int) -> int:
        return bin(bits).count("1")

    def _read_triple(self, start_add: int) -> int:
        return (
            256 * 256 * self._read_m(start_add)
            + 256 * self._read_m(start_add + 1)
            + self._read_m(start_add + 2)
        )

    def _read_bcd(self, num: int) -> int:
        return 10 * ((num >> 4) & 0x0F) + (num & 0x0F)
