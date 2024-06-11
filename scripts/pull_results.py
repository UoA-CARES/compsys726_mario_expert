import os
import subprocess
from pathlib import Path

import virtualenv
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def read_folder(drive, title, file_id):
    folder = {}

    folder["title"] = title
    folder["files"] = {}
    folder["folders"] = []

    drive_list = drive.ListFile(
        {"q": f"'{file_id}' in parents and trashed=false"}
    ).GetList()

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


def run_venv(upi, requirement_path):
    path = f"{os.path.expanduser('~')}/venv"
    venv_dir = os.path.join(path, f"{upi}")
    virtualenv.cli_run([venv_dir])

    python_bin = f"{path}/{upi}/bin/python3"

    command = f". {venv_dir}/bin/activate && pip install -r {requirement_path}/requirements.txt"
    os.system(command)

    return subprocess.Popen([python_bin, "run.py", "--upi", upi, "--headless"])


def main():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()

    drive = GoogleDrive(gauth)

    # COMPSYS726 - Assignment 1 Folder
    primary_folder_id = "1xM3Dhtm3YCoLnMFTMxyZnhJVvHsYbFgn"

    directory = read_folder(drive, "COMPSYS726 - Assignments", primary_folder_id)

    print_folders(directory)

    sub_processes = {}
    for folders in directory["folders"]:
        upi = folders["title"]
        print(f"Title: {upi}")

        files = folders["files"]
        requirements_id = files["requirements.txt"]["id"]
        mario_expert_id = files["mario_expert.py"]["id"]

        requirement_path = f"{Path(__file__).parent.parent}"

        file = drive.CreateFile({"id": requirements_id})
        file.GetContentFile(f"{requirement_path}/requirements.txt")

        file = drive.CreateFile({"id": mario_expert_id})
        file.GetContentFile("mario_expert.py")

        p = run_venv(upi, requirement_path)
        sub_processes[upi] = p

    for upi, p in sub_processes.items():
        exit_code = p.wait()
        print(f"Exit code: {exit_code} {upi}")


if __name__ == "__main__":
    main()
