import os
from pathlib import Path

import run
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def read_folder(drive, title, id):
    folder = {}

    folder["title"] = title
    folder["files"] = {}
    folder["folders"] = []

    drive_list = drive.ListFile({"q": f"'{id}' in parents and trashed=false"}).GetList()

    for f in drive_list:
        if f["mimeType"] == "application/vnd.google-apps.folder":
            folder["folders"].append(read_folder(drive, f["title"], f["id"]))
        else:
            folder["files"][f["title"]] = {
                "id": f["id"],
                "title": f["title"],
                "title1": f["alternateLink"],
            }

    return folder


def print_folders(directory, tab=0):
    tabs = " " * tab

    for _, file in directory["files"].items():
        message = f"{tabs}File: {file['title']}, id: {file['id']}"
        print(f"{message}")

    for folder in directory["folders"]:
        message = f"{tabs}Folder: {folder['title']}"
        print(f"{message}")
        print_folders(folder, tab=tab + 5)


def main():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()

    drive = GoogleDrive(gauth)

    # COMPSYS726 - Assignment 1 Folder
    primary_folder_id = "1xM3Dhtm3YCoLnMFTMxyZnhJVvHsYbFgn"

    directory = read_folder(drive, "COMPSYS726 - Assignments", primary_folder_id)

    print_folders(directory)

    for folders in directory["folders"]:
        title = folders["title"]
        print(f"Title: {title}")

        files = folders["files"]
        requirements_id = files["requirements.txt"]["id"]
        mario_expert_id = files["mairo_expert.py"]["id"]

        requirement_path = f"{Path(__file__).parent.parent}"

        file = drive.CreateFile({"id": requirements_id})
        file.GetContentFile(f"{requirement_path}/requirements.py")

        file = drive.CreateFile({"id": mario_expert_id})
        file.GetContentFile("mario_expert.py")

        os.system(
            f"pip3 install -r {requirement_path}/requirements.py --ignore-installed"
        )
        os.system(f"python3 run.py --upi {title} --headless")


if __name__ == "__main__":
    main()
