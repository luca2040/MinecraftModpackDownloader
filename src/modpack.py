from typing import Dict
import os
import zipfile
import json

MANIFEST_FILE = "manifest.json"


def is_modpack_valid(modpack_path: str) -> bool:
    """Checks if a modpack is valid

    Args:
        modpack_path (str): The modpack's ZIP file path

    Returns:
        bool: True if the pack is valid, false otherwise
    """
    try:
        with zipfile.ZipFile(modpack_path, "r") as z:
            return MANIFEST_FILE in z.namelist()
    except:
        return False


def get_minecraft_version(modpack_content: Dict) -> str:
    """Gets the minecraft version for the given manifest dict

    Args:
        modpack_content (Dict): The manifest json file loaded as a Python dict

    Returns:
        str: The minecraft version as "version - loader id"
    """
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


class Modpack:
    """Class to store modpack-relative information, used to simplify passing those variables into functions."""

    def __init__(self, modpack_path: str, extraction_path: str):
        """Set the paths for the modpack.

        Args:
            modpack_path (str): Path to the modpack's ZIP file
            extraction_path (str): Output path
        """
        self.modpack_path = modpack_path
        self.output_path = extraction_path

        # Those will be set later
        self.overrides: str | None = None
        self.minecraft_version: str = ""
        self.modpack_name: str = ""
        self.modpack_version: str = ""
        self.modpack_author: str = ""
        self.files: Dict | None = None

        self.mods_folder: str = os.path.join(self.output_path, "mods")
        self.resourcepack_folder: str = os.path.join(self.output_path, "resourcepacks")
        self.shaderpack_folder: str = os.path.join(self.output_path, "shaderpacks")

    def load_modpack(self) -> bool:
        """Try loading the modpack.

        Returns:
            bool: True if the pack has been loaded successfully, False otherwise.
        """
        try:
            with zipfile.ZipFile(self.modpack_path, "r") as z:
                with z.open(MANIFEST_FILE) as f:
                    json_bytes = f.read()
                    json_str = json_bytes.decode("utf-8")
                    manifest = json.loads(json_str)
        except:
            return False

        self.overrides: str | None = manifest.get("overrides", None)
        self.minecraft_version: str = get_minecraft_version(manifest)
        self.modpack_name: str = manifest.get("name", "")
        self.modpack_version: str = manifest.get("version", "")
        self.modpack_author: str = manifest.get("author", "")
        self.files: Dict | None = manifest.get("files", None)

        os.makedirs(self.mods_folder, exist_ok=True)
        os.makedirs(self.resourcepack_folder, exist_ok=True)
        os.makedirs(self.shaderpack_folder, exist_ok=True)

        return True
