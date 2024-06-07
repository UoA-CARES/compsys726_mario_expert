"""

"""

import random
import json
import logging
import time
from pathlib import Path

import cv2
from mario_environment import MarioEnvironment


class MarioExpert:
    def __init__(self, results_path: str, headless=False):
        self.results_path = results_path

        self.environment = MarioEnvironment(headless=headless)

        self.video = None

    def start_video(self, video_name, width, height, fps=30):
        self.video = cv2.VideoWriter(
            video_name, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )

    def stop_video(self) -> None:
        self.video.release()

    def choose_action(self, stats, game_image, game_area):
        return random.randint(0, len(self.environment.valid_actions) - 1)

    def play(self):
        self.environment.reset()

        frame = self.environment.grab_frame()
        height, width, _ = frame.shape

        self.start_video(f"{self.results_path}/mario_expert.mp4", width, height)

        while not self.environment.get_game_over():

            state = self.environment.game_state()

            frame = self.environment.grab_frame()
            self.video.write(frame)

            game_area = self.environment.game_area()

            action = self.choose_action(state, frame, game_area)
            self.environment.run_action(action)

        final_stats = self.environment.game_state()
        logging.info(f"Final Stats: {final_stats}")

        with open(f"{self.results_path}/results.json", "w", encoding="utf-8") as file:
            json.dump(final_stats, file)

        self.stop_video()
