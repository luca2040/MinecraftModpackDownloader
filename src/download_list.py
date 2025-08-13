from typing import List, Tuple
from modpack import Modpack
from mod import ModElement, mod_type_html_map
from jinja2 import Template
from print_color import print
from utils import ask_yes_no
from suppress_std import SuppressStd
import webbrowser
from pathlib import Path
from urllib.parse import quote


html_download_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Download remaining mods</title>
</head>
<body>
    <p>
        <b>These mods couldn't be downloaded automatically. Please download them manually and put them in their respective folders{% if mods_path and resource_path and shaders_path %}:</b>
            <br>
            <table border="1" cellpadding="5">
                <tr>
                    <th>Folder</th>
                    <th>Local path</th>
                </tr>
                <tr>
                    <td>Mods folder</td>
                    <td><span style="color: #1976D2; font-family: monospace; font-size: 1.25em;">{{ mods_path }}</span></td>
                </tr>
                <tr>
                    <td>Resource packs folder</td>
                    <td><span style="color: #FF8F00; font-family: monospace; font-size: 1.25em;">{{ resource_path }}</span></td>
                </tr>
                <tr>
                    <td>Shaders folder</td>
                    <td><span style="color: #7B1FA2; font-family: monospace; font-size: 1.25em;">{{ shaders_path }}</span></td>
                </tr>
            </table>
        {% else %}.</b>{% endif %}
    </p>
    
    <p>
        <b>Downloads:</b>
    </p>

    <table border="1" cellpadding="5">
        <tr>
            <th>Resource type</th>
            <th>Download link</th>
        </tr>
        {% for (type_tuple, url_tuple) in elements %}
            {% set type_text, color = type_tuple %}
            {% set view_name, url = url_tuple %}
            <tr>
                <td><b style="color: {{ color }};">{{ type_text }}</b></td>
                <td><a href="{{ url }}">{{ view_name }}</a></td>
            </tr>
        {% endfor %}
    </table>
</body>
</html>
"""


def ask_download_list(modpack: Modpack, error_list: List[int]) -> None:
    print()
    if not ask_yes_no(
        "Do you want to open a list of the missing mods with the links to download them manually? (y/n)",
        color="m",
    ):
        return

    # List that will be rendered as HTML
    # List[ ( (type, color), (name, url) ) ]
    render_list: List[Tuple[Tuple[str, str], Tuple[str, str]]] = []

    for index in error_list:
        modpack.generate_download_url(index)

        mod_element: ModElement = modpack[index]
        if mod_element.download_url is not None:
            render_list.append(
                (
                    mod_type_html_map[mod_element.file_type],  # (type, color)
                    (  # (name, url)
                        mod_element.view_name
                        or f"{mod_element.project_id}:{mod_element.file_id}",
                        mod_element.download_url,
                    ),
                )
            )

    template = Template(html_download_template)
    rendered_html = template.render(
        elements=render_list,
        mods_path=modpack.mods_folder,
        resource_path=modpack.resourcepack_folder,
        shaders_path=modpack.shaderpack_folder,
    )

    with open(modpack.download_html_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)
    with SuppressStd():
        html_abs_path = Path(modpack.download_html_path).resolve()
        file_url = "file://" + quote(str(html_abs_path.as_posix()))
        webbrowser.open(file_url)
