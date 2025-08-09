from print_color import print
import zipfile
import json
import os
import concurrent.futures
import threading

from cursemaven import mod_name_from_id, download_mod

MANIFEST_FILE = "manifest.json"
RETRIES = 5


def is_modpack_valid(modpack_path: str) -> bool:
    try:
        with zipfile.ZipFile(modpack_path, "r") as z:
            if MANIFEST_FILE in z.namelist():
                return True
    except:
        return False

    return False


def get_minecraft_version(modpack_content) -> str:
    minecraft = modpack_content.get("minecraft", None)
    if not minecraft:
        return ""

    version = minecraft.get("version", "")
    modloaders = minecraft.get("modLoaders", [])

    id = ""

    for loader in modloaders:
        is_primary = loader.get("primary", False)
        current_id = loader.get("id", "")
        if is_primary:
            id = current_id

    return f"{version} - {id}"


def check_and_download_resource(
    idx, file, resourcepack_folder, mods_folder
) -> bool:  # False means retry
    project_id = file.get("projectID", None)
    file_id = file.get("fileID", None)

    if project_id is None and file_id is None:
        return True

    mod_name = mod_name_from_id(project_id, file_id)
    if not mod_name:
        print(
            f"Cannot find {project_id}:{file_id}",
            tag="Warning",
            tag_color="y",
            color="m",
        )
        return True

    is_texturepack = mod_name.endswith(".zip")  # Not the best check, but it works
    target_folder = resourcepack_folder if is_texturepack else mods_folder
    download_filepath = os.path.join(target_folder, mod_name)

    downloaded = download_mod(mod_name, download_filepath, project_id, file_id)

    if downloaded:
        print(
            mod_name,
            tag=f"Downloaded {idx + 1}",
            tag_color="g",
            color="w",
        )
        return True
    else:
        print(
            mod_name,
            tag=f"Download error {idx + 1}",
            tag_color="y",
            color="w",
        )
        return False


def download_wrapper(args):
    idx, file, resourcepack_folder, mods_folder = args

    for _ in range(RETRIES):
        skip = check_and_download_resource(idx, file, resourcepack_folder, mods_folder)
        if skip:
            break


def multithreaded_download(files, resourcepack_folder, mods_folder):
    files_args = [
        (idx, file, resourcepack_folder, mods_folder) for idx, file in enumerate(files)
    ]
    total_files = len(files)

    print_lock = threading.Lock()

    def print_progress(print_idx):
        with print_lock:
            current_percent = 100.0 * (print_idx + 1) / total_files
            print(f"{current_percent:.2f}%", tag="Progress", color="w", tag_color="w")

    max_workers = None  # os.cpu_count() * 5 by default
    idx = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_wrapper, arg) for arg in files_args]
        for _ in concurrent.futures.as_completed(futures):
            print_progress(idx)
            idx = idx + 1


def extract_modpack(modpack_path: str, extraction_path: str) -> None:
    try:
        with zipfile.ZipFile(modpack_path, "r") as z:
            with z.open(MANIFEST_FILE) as f:
                json_bytes = f.read()
                json_str = json_bytes.decode("utf-8")
                manifest = json.loads(json_str)
    except:
        print("Error parsing manifest file", tag="Error", tag_color="r", color="r")
        exit()

    overrides = manifest.get("overrides", None)
    minecraft_version = get_minecraft_version(manifest)
    modpack_name = manifest.get("name", "")
    modpack_version = manifest.get("version", "")
    modpack_author = manifest.get("author", "")
    files = manifest.get("files", None)

    mods_folder = os.path.join(extraction_path, "mods")
    resourcepack_folder = os.path.join(extraction_path, "resourcepacks")
    os.makedirs(mods_folder, exist_ok=True)
    os.makedirs(resourcepack_folder, exist_ok=True)

    multithreaded_download(
        files, resourcepack_folder=resourcepack_folder, mods_folder=mods_folder
    )

    print()
    print("Download finished", color="g", format="bold")
