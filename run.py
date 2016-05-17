import configparser
import os
import shutil
import subprocess
import filecmp
import getpass

const_NOTPROVIDED_ERROR = "NOT PROVIDED: "
const_dir_CURRENT = os.path.abspath("")
const_dir_TEMP = os.path.join(const_dir_CURRENT, "TEMP")
const_dir_BEFORE = os.path.join(const_dir_TEMP, "BEFORE")
const_dir_AFTER = os.path.join(const_dir_TEMP, "AFTER")
const_dir_COMPARED = os.path.join(const_dir_TEMP, "_COMPARE_RESULT")

# -------------------------------------------------------------------------------------------------


class GlobalSettings:
    stcmd = ""
    StarteamServer = ""
    StarteamPort = ""
    StarteamLogin = ""
    StarteamProject = ""
    StarteamView = ""
    Labels = []


def quote(string2prepare):
    return "\""+string2prepare+"\""

# -------------------------------------------------------------------------------------------------
# Очистка рабочих каталогов


def __onerror_handler__(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise BaseException


def clean(directory):
    try:
        print("CLEANING {}. Please wait.".format(const_dir_TEMP))
        shutil.rmtree(directory, onerror=__onerror_handler__)
        print("\tCLEANING done")
    except FileNotFoundError:
        pass  # если папка TEMP отсутствует, то продолжаем молча
    except BaseException as e:
        print("Error when cleaning directories ({})".format(e))
        raise


# -------------------------------------------------------------------------------------------------


def read_config():
    settings = GlobalSettings()
    ini_filename = "settings.ini"
    error_header = "Error when reading settings from file {} ".format(ini_filename)
    section_special = "SPECIAL"
    section_common = "COMMON"
    section_labels = "LABELS"
    try:
        parser = configparser.RawConfigParser()
        res = parser.read(ini_filename)
        if res.count == 0:  # если файл настроек не найден
            raise FileNotFoundError("NOT FOUND {}".format(ini_filename))
        settings.stcmd = parser.get(section_common, "stcmd")
        settings.StarteamServer = parser.get(section_common, "StarteamServer")
        settings.StarteamPort = parser.get(section_common, "StarteamPort")
        settings.StarteamProject = parser.get(section_special, "StarteamProject")
        settings.StarteamView = parser.get(section_special, "StarteamView")
        settings.StarteamLogin = parser.get(section_special, "StarteamLogin")
        settings.Labels = parser.items(section_labels)

        # проверка Labels -----------------------------------
        all_lables = ''
        for label in settings.Labels:
            all_lables += label[1].strip()

        if not settings.Labels or all_lables == "":  # Если не дали совсем никаких меток для загрузки
            raise ValueError("NO LABELS defined in {}".format(ini_filename))

        # проверка stsmd -----------------------------------
        if settings.stcmd != "":  # если пусть к stcmd не задан
            settings.stcmd = os.path.normpath(settings.stcmd)
            settings.stcmd = settings.stcmd+os.sep+"stcmd.exe"
            if not os.path.exists(settings.stcmd):
                raise FileNotFoundError("NOT FOUND "+settings.stcmd)
        else:
            raise FileNotFoundError("NOT DEFINED path to stcmd")

    except BaseException as e:
        print(error_header+"({})".format(e))
        raise e
    else:
        print("GOT SETTINGS:\n\tStarteamProject = {}\n\tStarteamView = {}\n\tLabels = {}\n\tstcmd = {}".
              format(settings.StarteamProject, settings.StarteamView, settings.Labels, settings.stcmd))
        return settings


# -------------------------------------------------------------------------------------------------


def download_starteam(settings):
    errorheader = "Error when downloading from Starteam "
    total_result = -1
    try:
        password = getpass.getpass('BEGIN DOWNLOADING\n\tEnter StarTeam password: ')  # getpass.fallback_getpass("Enter Starteam password:")
        for key, label in settings.Labels:
            if label.strip() == "":
                print("\tNOT DEFINED label \"{}\" (empty)".format(key))
            else:
                print("\tDOWNLOADING for label \"{}\". Please wait...".format(label))
                if key == "labelbefore":
                    outdir = const_dir_BEFORE
                else:
                    outdir = const_dir_AFTER

                launch_string = quote(settings.stcmd)
                launch_string += " co -nologo -stop -q -x -o -is -p \"{}:{}@{}:{}/{}/{}\"".format(
                                    settings.StarteamLogin,
                                    password,
                                    settings.StarteamServer,
                                    settings.StarteamPort,
                                    settings.StarteamProject,
                                    settings.StarteamView)
                launch_string += " -rp " + quote(outdir)
                launch_string += " -vl " + quote(label)

                # print(launch_string)
                result = subprocess.call(launch_string)
                if result == 0:
                    print("\t\tFINISHED download for label \"{}\"".format(label))
                    total_result = 0
                else:
                    print("\t\tERROR when download label \"{}\"".format(label))

    except BaseException as e:
        print(errorheader + "({})".format(e))
    return total_result


# -------------------------------------------------------------------------------------------------


def __compare_and_copy_dirs_recursively__(before, after, wheretocopy):
    dircmp = filecmp.dircmp(before, after)
    if dircmp.common_dirs:
        for directory in dircmp.common_dirs:
            __compare_and_copy_dirs_recursively__(os.path.join(before, directory),
                                                  os.path.join(after, directory),
                                                  os.path.join(wheretocopy, directory))

    if dircmp.diff_files:
        for file in dircmp.diff_files:
            path = os.path.join(after, file)
            if os.path.isfile(path):
                print("\t\tcopying {}".format(path))
                if not os.path.exists(wheretocopy):
                    os.makedirs(wheretocopy)
                shutil.copy2(path, wheretocopy)
            else:
                print("\t\tsomething wrong {} -> {}".format(path, wheretocopy))

    if dircmp.right_only:
        for file in dircmp.right_only:
            path = os.path.join(after, file)
            if os.path.isfile(path):
                print("\t\tcopying {}".format(path))
                if not os.path.exists(wheretocopy):
                    os.makedirs(wheretocopy)
                shutil.copy2(path, wheretocopy)
            else:
                print("\t\tcopying DIR with contents {}".format(path))
                clean(os.path.join(wheretocopy, file))
                shutil.copytree(path, os.path.join(wheretocopy, file))


def comparedirs():
    if os.path.exists(const_dir_BEFORE):
        print("BEGIN compare directories:\n\tBEFORE: {}\n\tAFTER:  {}".format(const_dir_BEFORE, const_dir_AFTER))
        __compare_and_copy_dirs_recursively__(const_dir_BEFORE, const_dir_AFTER, const_dir_COMPARED)
    else:
        os.rename(const_dir_AFTER, const_dir_COMPARED)
        print("USING folder 'AFTER' as compare result, because 'BEFORE' not exists:"
              "\n\tBEFORE (not exists): {}\n\tAFTER:  {}".format(const_dir_BEFORE, const_dir_AFTER))

    print("\tFINISHED compare directories. LOOK at {}".format(const_dir_COMPARED))


# -------------------------------------------------------------------------------------------------


def list_files_of_given_type(directory, extension):
    result_list = []
    extension = extension.upper()
    for root, dirs, files in os.walk(directory):
        for name in files:
            if os.path.splitext(name)[1].upper() == extension:
                result_list.append(os.path.join(root, name))
        for name in dirs:
            result_list += list_files_of_given_type(name, extension)
    return result_list


# -------------------------------------------------------------------------------------------------


def build_upgrade_eif():
    eif_list = list_files_of_given_type(const_dir_COMPARED, ".eif")
    print(eif_list)
    pass


# -------------------------------------------------------------------------------------------------


def main():
    global_settings = read_config()
    clean(const_dir_TEMP)
    if download_starteam(global_settings) == 0:
        comparedirs()
    build_upgrade_eif()
    print("DONE!!!")


# ---- поехали ------------------------------------------------------------------------------------


main()
