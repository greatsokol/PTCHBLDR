import configparser
import os
import shutil
import subprocess
import filecmp

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
    StarteamPassword = ""
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
        raise exc_info


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
    inifilename = "settings.ini"
    errorheader = "Error when reading settings from file {} ".format(inifilename)
    sectionSPECIAL = "SPECIAL"
    sectionCOMMON = "COMMON"
    sectionLABELS = "LABELS"
    try:
        parser = configparser.RawConfigParser()
        res = parser.read(inifilename)
        if res.count == 0:  # если файл настроек не найден
            raise FileNotFoundError("NOT FOUND {}".format(inifilename))
        settings.stcmd = parser.get(sectionCOMMON, "stcmd")
        settings.StarteamServer = parser.get(sectionCOMMON, "StarteamServer")
        settings.StarteamPort = parser.get(sectionCOMMON, "StarteamPort")
        settings.StarteamProject = parser.get(sectionSPECIAL, "StarteamProject")
        settings.StarteamView = parser.get(sectionSPECIAL, "StarteamView")
        settings.StarteamLogin = parser.get(sectionSPECIAL, "StarteamLogin")
        settings.StarteamPassword = parser.get(sectionSPECIAL, "StarteamPassword")
        settings.Labels = parser.items(sectionLABELS)

        # проверка Labels -----------------------------------
        all_lables = ''
        for label in settings.Labels:
            all_lables += label[1].strip()

        if not settings.Labels or all_lables == "":  # Если не дали совсем никаких меток для загрузки
            raise ValueError("NO LABELS defined in {}".format(inifilename))

        # проверка stsmd -----------------------------------
        if settings.stcmd != "":  # если пусть к stcmd не задан
            settings.stcmd = os.path.normpath(settings.stcmd)
            settings.stcmd = settings.stcmd+os.sep+"stcmd.exe"
            if not os.path.exists(settings.stcmd):
                raise FileNotFoundError("NOT FOUND "+settings.stcmd)
        else:
            raise FileNotFoundError("NOT DEFINED path to stcmd")

    except BaseException as e:
        print(errorheader+"({})".format(e))
        raise e
    else:
        print("GOT SETTINGS:\n\tStarteamProject = {}\n\tStarteamView = {}\n\tLabels = {}\n\tstcmd = {}".
              format(settings.StarteamProject, settings.StarteamView, settings.Labels, settings.stcmd))
        return settings


# -------------------------------------------------------------------------------------------------


def downloadStarteam(settings):
    errorheader = "Error when downloading from Starteam "
    totalResult = -1
    try:
        # starteamlogin = input("Enter Starteam login:")
        # TODO переделать запрос getpass - не скрывает вводимые символы, честно предупреждает об этом
        # starteampass = getpass.fallback_getpass("Enter Starteam password:")

        for key, label in settings.Labels:
            if label.strip() == "":
                print("NOT DEFINED label \"{}\" (empty)".format(key))
            else:
                print("DOWNLOADING for label \"{}\". Please wait...".format(label))
                if key == "labelbefore":
                    outdir = const_dir_BEFORE
                else:
                    outdir = const_dir_AFTER

                launchstring = quote(settings.stcmd)
                launchstring += " co -nologo -stop -q -x -o -is -p \"{}:{}@{}:{}/{}/{}\"".format(
                                    settings.StarteamLogin,
                                    settings.StarteamPassword,
                                    settings.StarteamServer,
                                    settings.StarteamPort,
                                    settings.StarteamProject,
                                    settings.StarteamView)
                launchstring += " -rp " + quote(outdir)
                launchstring += " -vl " + quote(label)

                # print(launchstring)
                result = subprocess.call(launchstring)
                if result == 0:
                    print("\tFINISHED download for label \"{}\"".format(label))
                    totalResult = 0
                else:
                    print("\tERROR when download label \"{}\"".format(label))

    except BaseException as e:
        print(errorheader + "({})".format(e))
    return totalResult


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


def main():
    globalSettings = read_config()
    clean(const_dir_TEMP)
    if downloadStarteam(globalSettings) == 0:
        comparedirs()
    print("DONE!!!")


# ---- поехали ------------------------------------------------------------------------------------


main()
