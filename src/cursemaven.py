import requests
import re

CURSEMAVEN_URL = "https://cursemaven.com"
GROUP_PATH = "curse/maven"


def mod_name_from_id(project_id: int, file_id: int) -> str | None:
    """Get the mod name from its ID using the CurseMaven repo.
    If a string is returned, then the project exists on CurseMaven, otherwise it doesnt exist
    and needs to be downloaded manually

    Args:
        project_id (int)
        file_id (int)

    Returns:
        str | None: The project's name
    """
    maven_url = f"{CURSEMAVEN_URL}/test/{project_id}/{file_id}"

    resp = requests.get(maven_url)
    cdn_url = None
    for line in resp.text.splitlines():
        if line.startswith("Found: "):
            cdn_url = line[len("Found: ") :]
            break

    if not cdn_url:
        return None

    response = requests.head(cdn_url, allow_redirects=True)
    cd = response.headers.get("content-disposition")
    if cd:
        fname = re.findall('filename="?([^"]+)"?', cd)
        if fname:
            return fname[0]
    return cdn_url.split("/")[-1]


def download_mod(name: str, save_path: str, project_id: int, file_id: int) -> bool:
    """Downloads a mod to the given path from its IDs using the CurseMaven repo

    Args:
        name (str): The mod name, can be whatever is accepted by CurseMaven and usually isnt important.
        save_path (str): The path to the file that will be created.
        project_id (int)
        file_id (int)

    Returns:
        bool: True if the mod has successfully been downloaded, False otherwise
    """
    artifact_id = f"{name}-{project_id}"
    version = str(file_id)

    url = f"{CURSEMAVEN_URL}/{GROUP_PATH}/{artifact_id}/{version}/{artifact_id}-{version}.jar"

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return True
    except:
        return False
