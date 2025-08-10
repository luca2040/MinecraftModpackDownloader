from print_color import print
import os
import sys
import time
import concurrent.futures
import threading

from modpack import Modpack
from cursemaven import mod_name_from_id, download_mod
from utils import extract_zip_subfolder


NUM_RETRIES = 5
RETRY_DELAY = 2


def check_and_download_resource(
    project_id, file_id, mod_name, resourcepack_folder, mods_folder
) -> bool:  # True means that there is no need to retry
    is_texturepack = mod_name.endswith(".zip")  # Not the best check, but it works
    target_folder = resourcepack_folder if is_texturepack else mods_folder
    download_filepath = os.path.join(target_folder, mod_name)

    downloaded = download_mod(mod_name, download_filepath, project_id, file_id)
    return downloaded


def download_wrapper(args) -> str | None:
    idx, file, resourcepack_folder, mods_folder = args

    project_id = file.get("projectID", None)
    file_id = file.get("fileID", None)

    if project_id is None or file_id is None:
        return

    mod_name = mod_name_from_id(project_id, file_id)
    if not mod_name:
        return f"{project_id}:{file_id}"

    for _ in range(NUM_RETRIES):
        success = check_and_download_resource(
            project_id=project_id,
            file_id=file_id,
            mod_name=mod_name,
            resourcepack_folder=resourcepack_folder,
            mods_folder=mods_folder,
        )
        if success:
            return
        time.sleep(RETRY_DELAY)

    return mod_name


def multithreaded_download(files, resourcepack_folder, mods_folder):
    files_args = [
        (idx, file, resourcepack_folder, mods_folder) for idx, file in enumerate(files)
    ]
    total_files = len(files)
    print_lock = threading.Lock()

    def print_progress(print_idx) -> None:
        p = print_idx / total_files
        i = int(p * 40)
        sys.stdout.write("\r")
        sys.stdout.write("[%-40s] %.2f%%" % ("=" * i, p * 100))
        sys.stdout.flush()

    error_list = []

    max_workers = (os.cpu_count() or 10) * 5
    idx = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_wrapper, arg) for arg in files_args]
        for future in concurrent.futures.as_completed(futures):
            with print_lock:
                eventual_error = future.result()
                if eventual_error:
                    error_list.append(eventual_error)
                idx = idx + 1
                print_progress(idx)

    return error_list


def extract_modpack(modpack_path: str, extraction_path: str) -> None:
    modpack = Modpack(modpack_path, extraction_path)

    if not modpack.load_modpack():
        print("Error parsing manifest file", tag="Error", tag_color="r", color="r")
        return

    print("Downloading mods", color="c", format="bold")
    errors = multithreaded_download(
        modpack.files,
        resourcepack_folder=modpack.resourcepack_folder,
        mods_folder=modpack.mods_folder,
    )

    print()
    print("Download finished", color="g", format="bold")
    if errors:
        print("Errors downloading:", color="r")
        for error in errors:
            print("\t" + error)

    if modpack.overrides is not None:
        print()
        print("Extracting overrides", color="c", format="bold")
        extract_zip_subfolder(
            zip_path=modpack_path, subfolder=modpack.overrides, dest_dir=extraction_path
        )
        print("Overrides extracted", color="g", format="bold")

    modpack_description = f"{modpack.modpack_name} - {modpack.modpack_version}"
    if modpack.modpack_author:
        modpack_description += f" by {modpack.modpack_author}"

    readme_path = os.path.join(extraction_path, "README_MODPACK.txt")
    readme_contents = (
        f"{modpack_description}\n\n"
        f"Minecraft {modpack.minecraft_version}\n"
        f"Total resources (mods, resourcepacks and shaders) downloaded: {len(modpack.files)}"
    )

    with open(readme_path, "w") as readme_file:
        readme_file.write(readme_contents)

    print()
    print("Modpack successfully downloaded", color="g", format="bold")
