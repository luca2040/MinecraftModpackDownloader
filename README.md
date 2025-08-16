# Minecraft Modpack Downloader
Simple program to manually download Minecraft CurseForge modpacks into a folder containing all the modpack's mods, resourcepacks and custom configurations.

## Description
Modpacks do not contain the actual mod files into their zip file, but instead they contain a file that indicates all the mods' IDs to download them.
<br/>This program takes all the mod's IDs and downloads them from the [cursemaven](https://cursemaven.com) repository.

>[!NOTE]
>Sometimes, some mods listed in the pack might not be found in [cursemaven](https://cursemaven.com),
>in this case if the modpack contains the `modlist.html` file this program will try using it to get the **direct** download link per each missing mod and then will open a page in your browser where you can download them.<br/>
><details><summary>Download page example</summary><img src="https://github.com/user-attachments/assets/9972c823-10e1-44ee-83e4-93ac25ee9a3b"></img></details>

## Download
See the [releases](https://github.com/luca2040/MinecraftModpackDownloader/releases) page.

## Usage
- Run the program.
- You will be prompted to select the modpack ZIP file.
- After selecting the file, the program will print the needed Minecraft and loader version, for example `[Loader version] 1.21.5 - fabric-0.16.14`.
- Next, choose the extraction path - this is the folder where the modpack files will be downloaded and extracted. It can be any directory on your system or you can directly select the folder of a Minecraft instance with the required version.

The program will then:
- Download all the mods and resource packs.
- If some mods couldn't be downloaded automatically, it will ask if you want to open a page with the download links to get them manually (for more information about this see the note in the [Description](#description) section).
- Extract the modpack override files (usually configs or additional resources) into the chosen folder.
- Create a `MODPACK_DOWNLOAD_README.txt` file inside the extraction folder with information about the modpack.

Example `MODPACK_DOWNLOAD_README.txt`:
```txt
Example modpack - 1.0.0 by Example author

Minecraft 1.18.2 - forge-40.2.34
Total resources (mods and resourcepacks): 465
```

After extraction, you can:
- Set up your Minecraft instance the way you prefer with the loader version specified in the readme and printed in the console - no specific launcher needed.
- Manually copy the modpack files from the extraction folder to your Minecraft instance folder as desired **if when downloading you selected an external folder**.

>[!NOTE]
>This program takes the most important information from the modpack's `manifest.json` and it actually ignores the `manifestType` and `manifestVersion` fields, so there may be rare cases of issues related to this.
><br/>However i still haven't seen any issues even after trying some of the most used modpacks, so i think this is fine.
