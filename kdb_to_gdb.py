import os
import shutil
import logging

logging.basicConfig(
    filename='%s.log' % "kdb_to_gdb", 
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(message)s', 
    datefmt='%d-%b-%y %H:%M:%S'
)
logging.info("Logging file started")

# GLOBALS

NAMES = [
    "all",
    "shorts",
    "socks",
    "numbers",
    "font",
]

KIT_SETS_NAMES = [
    "ga",
    "gb",
    "pa",
    "pb",
]

AUSTRIA_ID = 4576
TOTAL_TEXTURES = 20
TEXTURES_IN_SET = 5
GLOVES_PREFIX = "-gloves"
PAL_PREFIX = "-pal"

def get_team_id(folder_number:int):
    return (folder_number - AUSTRIA_ID) // TOTAL_TEXTURES

def get_kit_set(file_number:int, folder_number:int):
    texture_number = file_number - folder_number
    first_texture = 0
    for i, kit_set_name in enumerate(KIT_SETS_NAMES, 1):
        last_texture = TEXTURES_IN_SET * i
        if first_texture <= texture_number < last_texture:
            return kit_set_name
        first_texture = last_texture
    raise Exception("Couldn't determinate the kit set for file number %d from folder number %d" % (file_number, folder_number))

def get_name(file_number:int, folder_number:int, kit_set:str):
    texture_number = file_number - folder_number
    kit_set_index = KIT_SETS_NAMES.index(kit_set)
    name_index = texture_number - kit_set_index * TEXTURES_IN_SET
    return NAMES[name_index]

def attrib_to_config(attrib_file_path, uni_folder):
    attrib_file = open(attrib_file_path, "r")
    lines = attrib_file.readlines()
    attrib_file.close()
    config_file_path = ""
    for line in lines:
        if line.startswith("#"): continue
        if any(kit_set_name in line for kit_set_name in KIT_SETS_NAMES):
            kit_set = line.strip().strip("[").strip("]")
            config_path = os.path.join(uni_folder, kit_set)
            os.makedirs(config_path, exist_ok=True)
            config_file_path = os.path.join(config_path, "config.txt")
            config_file = open(config_file_path, "w")
            config_file.write("numbers = \".\\numbers.png\"\n")
            config_file.close()
        if not config_file_path: continue
        if "collar" in line:
            config_file = open(config_file_path, "a")
            config_file.write(line)
            config_file.close()
        if "model" in line:
            config_file = open(config_file_path, "a")
            config_file.write(line)
            config_file.close()

def main():
    unis_dir = "."
    try:
        new_unis_dir =  "./uni/"
        os.makedirs(new_unis_dir, exist_ok=True)
        map_file = open("%smap.txt" % (new_unis_dir), "w")
        map_file.close()
    except Exception as e:
        logging.error("Error when trying to create %s" % (new_unis_dir))
        return

    unis = os.listdir(unis_dir)
    map_file = open("%smap.txt" % (new_unis_dir), "a")
    for uni in unis:
        try:
            folder_number = int(uni)
            team_id = get_team_id(folder_number)
            logging.info("team_id %d" % (team_id))
            team_folder = os.path.join(new_unis_dir, uni)
            os.makedirs(team_folder, exist_ok=True)
            map_file.write(
                "%d,\"%s\"\n" % (
                    team_id,
                    uni,
                )
            )
            textures_folder = os.path.join(unis_dir, uni)
            textures = os.listdir(textures_folder)
            for texture in textures:
                if ".cfg" in texture:
                    attrib_file_path = os.path.join(textures_folder, texture)
                    attrib_to_config(attrib_file_path, team_folder)
                else:
                    try:
                        gloves = False
                        pal = False
                        pal_prefix = ""

                        name, file_ext = texture.split(".")
                        if GLOVES_PREFIX in name:
                            name, _ = name.split("-")
                            gloves = True
                        elif PAL_PREFIX in name:
                            name, pal_prefix = name.split("-")
                            pal = True

                        texture_number = int(name)
                        kit_set = get_kit_set(texture_number, folder_number)
                        logging.info(kit_set)

                        kit_set_folder = os.path.join(team_folder, kit_set)
                        os.makedirs(kit_set_folder, exist_ok=True)

                        texture_name = get_name(texture_number, folder_number, kit_set)
                        if gloves: texture_name += GLOVES_PREFIX
                        if pal: texture_name += pal_prefix

                        texture_full_path = os.path.join(textures_folder, texture)
                        new_texture_full_path = os.path.join(kit_set_folder, ".".join((texture_name, file_ext)))
                        logging.info(new_texture_full_path)

                        shutil.copyfile(texture_full_path, new_texture_full_path)

                    except Exception as e:
                        logging.error("Error processing texture %s from folder %s Exception: %r" % (texture, uni, e))

        except Exception as e:
            logging.error("Error processing folder named %s Exception: %r" % (uni, e))
    map_file.close()


if __name__ == "__main__":
    main()


