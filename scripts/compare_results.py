import argparse
import glob
import json
import logging
from functools import cmp_to_key

logging.basicConfig(level=logging.INFO)


def compare_performance(results_one, results_two):
    if results_one["world"] > results_two["world"]:
        return -1
    elif results_one["world"] < results_two["world"]:
        return 1

    if results_one["stage"] > results_two["stage"]:
        return -1
    elif results_one["stage"] < results_two["stage"]:
        return 1

    if results_one["score"] > results_two["score"]:
        return -1
    elif results_one["score"] < results_two["score"]:
        return 1

    return 0


def get_args():
    parse_args = argparse.ArgumentParser()

    parse_args.add_argument("-r", "--results_path", type=str, required=True)

    return parse_args.parse_args()


def main():
    args = get_args()

    results_path = args.results_path

    result_directories = glob.glob(f"{results_path}/*")
    logging.info(f"Found {len(result_directories)} results directories")
    logging.info(f"Results directories: {result_directories}")

    logging.info(f"Comparing results in {results_path}")

    results = []
    for result_directory in result_directories:
        upi = result_directory.split("/")[-1]
        logging.info(f"Reading results for UPI: {upi}")

        with open(f"{result_directory}/results.json", "r", encoding="utf-8") as file:
            result = json.load(file)
            result["upi"] = upi

            results.append(result)

    results = sorted(results, key=cmp_to_key(compare_performance))

    for i, result in enumerate(results):
        logging.info(
            f"Rank {i + 1}: {result['upi']} - World: {result['world']} Stage: {result['stage']} Score: {result['score']}"
        )


if __name__ == "__main__":
    main()
