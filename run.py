import configparser
import os
import shutil
import subprocess
import filecmp
import re

const_dir_CURRENT = os.path.abspath("")
const_dir_TEMP = os.path.join(const_dir_CURRENT, "TEMP")
const_dir_BEFORE = os.path.join(const_dir_TEMP, "BEFORE")
const_dir_AFTER = os.path.join(const_dir_TEMP, "AFTER")
const_dir_COMPARED = os.path.join(const_dir_TEMP, "_COMPARE_RESULT")
const_dir_PATCH = os.path.join(const_dir_TEMP, "PATCH")
get_dir_COMPARED_BASE = lambda instance: os.path.join(os.path.join(const_dir_COMPARED, "BASE"), instance)
get_dir_PATCH = lambda instance: os.path.join(const_dir_PATCH, instance)
get_dir_PATCH_DATA = lambda instance: os.path.join(get_dir_PATCH(instance), "DATA")
get_filename_UPGRADE10_eif = lambda instance: os.path.join(get_dir_PATCH(instance), "Upgrade(10).eif")
splitfilename = lambda filename: os.path.split(filename)[1]

const_UPGRADE10_HEADER = \
                "[SECTION]\n" \
                "Name = MAKEUPGRADE (10)\n" \
                "Type = DSPStructure\n" \
                "Version = {}\n" \
                "ObjectType = 10\n" \
                "ObjectName = MAKEUPGRADE\n" \
                "TableName = MakeUpgrade\n" \
                "ParentObject =\n" \
                "RootNode =\n" \
                "[DATA]\n" \
                " [REMARKS]\n" \
                "  V. Генератор апгрейдов\n" \
                " [TREE]\n" \
                "  Indexes\n" \
                "    AKey\n" \
                "      Fields\n" \
                "        AutoKey:integer = 0\n" \
                "      Unique:boolean = TRUE\n" \
                "      Primary:boolean = TRUE\n" \
                "    DSP\n" \
                "      Fields\n" \
                "        StructureType:integer = 0\n" \
                "        StructureName:integer = 1\n" \
                "  Fields\n" \
                "    AutoKey\n" \
                "      FieldType:integer = 14\n" \
                "      Length:integer = 0\n" \
                "      Remark:string = 'PK'\n" \
                "    StructureType\n" \
                "      FieldType:integer = 1\n" \
                "      Length:integer = 0\n" \
                "      Remark:string = 'Категория'\n" \
                "    StructureName\n" \
                "      FieldType:integer = 0\n" \
                "      Length:integer = 255\n" \
                "      Remark:string = 'Структура'\n" \
                "    ImportStructure\n" \
                "      FieldType:integer = 16\n" \
                "      Length:integer = 0\n" \
                "      Remark:string = 'Импортировать или удалять структуру'\n" \
                "    BackupData\n" \
                "      FieldType:integer = 16\n" \
                "      Length:integer = 0\n" \
                "      Remark:string = 'Сохранять резервную копию структуры'\n" \
                "    ImportData\n" \
                "      FieldType:integer = 16\n" \
                "      Length:integer = 0\n" \
                "      Remark:string = 'Имп. данные или Локал. ресрсы для форм.'\n" \
                "    ReCreate\n" \
                "      FieldType:integer = 16\n" \
                "      Length:integer = 0\n" \
                "      Remark:string = 'Пересоздавать ли таблицу'\n" \
                "    NtClearRoot\n" \
                "      FieldType:integer = 16\n" \
                "      Length:integer = 0\n" \
                "      Remark:string = 'Очищать ветку структуры (данные таблицы) перед импортом'\n" \
                "    UpdateFound\n" \
                "      FieldType:integer = 16\n" \
                "      Length:integer = 0\n" \
                "      Remark:string = 'Обновлять сопадающие записи'\n" \
                "    IndexFields\n" \
                "      FieldType:integer = 8\n" \
                "      Length:integer = -1\n" \
                "      Remark:string = 'Список индексов полей для сравнения при добавлении записей (UpdateFound)'\n" \
                "    SubstFields\n" \
                "      FieldType:integer = 8\n" \
                "      Length:integer = -1\n" \
                "      Remark:string = 'Правила заполнения полей. (переименование, добавление поля в ПК...)'\n" \
                "    UseTransit\n" \
                "      FieldType:integer = 0\n" \
                "      Length:integer = 100\n" \
                "      Remark:string = 'Промежуточная структура'\n" \
                "    ParentFor\n" \
                "      FieldType:integer = 0\n" \
                "      Length:integer = 100\n" \
                "      Remark:string = 'Установить предком для структуры'\n" \
                "    OperationResult\n" \
                "      FieldType:integer = 0\n" \
                "      Length:integer = 255\n" \
                "      Remark:string = 'Результат операции'\n" \
                "    Description\n" \
                "      FieldType:integer = 0\n" \
                "      Length:integer = 255\n" \
                "      Remark:string = 'Описание операции'\n" \
                "[END]\n" \
                "[SECTION]\n" \
                "Name =  - Table data\n" \
                "Type = TableData\n" \
                "Version = {}\n" \
                "TableName = MAKEUPGRADE\n" \
                "[DATA]\n" \
                " [FIELDS]\n" \
                "  AutoKey\n" \
                "  StructureType\n" \
                "  StructureName\n" \
                "  ImportStructure\n" \
                "  BackupData\n" \
                "  ImportData\n" \
                "  ReCreate\n" \
                "  NtClearRoot\n" \
                "  UpdateFound\n" \
                "  IndexFields\n" \
                "  SubstFields\n" \
                "  UseTransit\n" \
                "  ParentFor\n" \
                "  OperationResult\n" \
                "  Description\n" \
                "[RECORDS]\n".format("100", "100")

const_UPGRADE10_FOOTER = "[END]\n"
const_instance_BANK = "BANK"
const_instance_CLIENT = "CLIENT"
# -------------------------------------------------------------------------------------------------


def getpassword(message):
    import getpass
    # running under PyCharm or not
    if "PYCHARM_HOSTED" in os.environ:
        return getpass.fallback_getpass(message)
    else:
        return getpass.getpass(message)
# -------------------------------------------------------------------------------------------------


class GlobalSettings:
    stcmd = ""
    StarteamServer = ""
    StarteamPort = ""
    StarteamLogin = ""
    StarteamProject = ""
    StarteamView = ""
    StarteamPassword = ""
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


def download_starteam_by_label(settings):
    total_result = -1
    try:
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
                                    settings.StarteamPassword,
                                    settings.StarteamServer,
                                    settings.StarteamPort,
                                    settings.StarteamProject,
                                    settings.StarteamView)
                launch_string += " -rp " + quote(outdir)
                launch_string += " -vl " + quote(label)

                # print(launch_string)
                result = subprocess.call(launch_string)
                if result == 0:
                    print("\t\tFINISHED downloading for label \"{}\"".format(label))
                    total_result = 0
                else:
                    print("\t\tERROR when downloading label \"{}\"".format(label))

    except BaseException as e:
        print("Error when downloading from Starteam ({})".format(e))
    return total_result
# -------------------------------------------------------------------------------------------------


def download_starteam_by_file(settings, path, filename, where_to_save):
    total_result = -1
    try:
        print("\tDOWNLOADING file \"{}\". Please wait...".format(path+filename))
        launch_string = quote(settings.stcmd)
        launch_string += " co -nologo -stop -q -x -o -is -p \"{}:{}@{}:{}/{}/{}/{}\"".format(
                                    settings.StarteamLogin,
                                    settings.StarteamPassword,
                                    settings.StarteamServer,
                                    settings.StarteamPort,
                                    settings.StarteamProject,
                                    settings.StarteamView,
                                    path)
        launch_string += " -rp " + quote(where_to_save)
        launch_string += " " + filename

        #print(launch_string)
        result = subprocess.call(launch_string)
        if result == 0:
            print("\t\tFINISHED downloading file \"{}\"".format(filename))
            total_result = 0
        else:
            print("\t\tERROR when downloading file \"{}\"".format(filename))

    except BaseException as e:
        print("Error when downloading from Starteam ({})".format(e))
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
# -------------------------------------------------------------------------------------------------


def compare_directories_BEFORE_and_AFTER():
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


def make_upgrade10_eif_string_by_file_name(counter, file_name):
    file_type_match = re.findall("\((?:\d+|data)\)\.eif", file_name, flags=re.IGNORECASE)
    if len(file_type_match):
        structure_type_raw = file_type_match[0]
        structure_type = re.sub(r"\.eif", "", structure_type_raw, flags=re.IGNORECASE).replace("(", "").replace(")", "")
        if structure_type.upper() == "DATA":
            structure_type = "10"
        file_name = file_name.replace(structure_type_raw, "")
        if structure_type == "10" or structure_type == "data":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|FALSE|TRUE|FALSE|''|''|''|''|NULL|'Таблицы'>"  # TODO здесь все сложно
        elif structure_type == "12":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|TRUE|NULL|NULL|NULL|NULL|NULL|'Визуальные формы'>"
        elif structure_type == "14":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|''|NULL|'Конфигурации'>"
        elif structure_type == "16":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|''|NULL|'Автопроцедуры'>"
        elif structure_type == "18":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Профили'>"
        elif structure_type == "19":
            result = "<{}|{}|'{}'|TRUE|FALSE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Роли'>"
        elif structure_type == "20":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Привелегии'>"
        elif structure_type == "30":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|TRUE|NULL|NULL|NULL|NULL|NULL|'Сценарии'>"
        elif structure_type == "65":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|''|NULL|''>"
        elif structure_type == "66":
            result = "<352|66|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'RTS Errors params'>"
        elif structure_type == "71":
            result = "<{}|{}|'{}'|TRUE|FALSE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|''|NULL|'Генераторы'>"
        elif structure_type == "72":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|''|NULL|'Структуры отображений'>"
        elif structure_type == "73":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|''|NULL|'Хранимые процедуры'>"
        elif structure_type == "81":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|''|NULL|'Простые операции'>"
        elif structure_type == "82":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|''|NULL|'Табличные операции'>"
        elif structure_type == "83":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|''|NULL|'Документарные операции'>"
        elif structure_type == "84":
            result = "<{}|{}|'{}'|TRUE|FALSE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|''|NULL|'Статусы'>"
        else:
            raise ValueError("ERROR unknown structure type {} for filename {}".format(structure_type, file_name))

        return "  "+result.format(counter, structure_type, file_name)
    else:
        raise ValueError("ERROR can't detect structure type by filename ({})".format(file_name))
# -------------------------------------------------------------------------------------------------


def search_for_DATA_FILES_without_10_FILES_and_download_them(settings, instance):
    eif_list = list_files_of_given_type(get_dir_COMPARED_BASE(instance), ".eif")
    for eif_file in eif_list:
        file_type_match = re.findall("\(data\)\.eif", eif_file, flags=re.IGNORECASE)
        if len(file_type_match):
            # TODO проверить - может быть файл имеется
            structure_type_raw = file_type_match[0]
            eif10_file = str(eif_file).replace(structure_type_raw,"(10).eif")
            eif10_file = splitfilename(eif10_file)
            print(eif10_file)
            download_starteam_by_file(settings, "BASE/"+instance+"/TABLES/", eif10_file, const_dir_COMPARED)
# -------------------------------------------------------------------------------------------------


def build_upgrade10_eif(instance):
    eif_list = list_files_of_given_type(get_dir_COMPARED_BASE(instance), ".eif")
    if len(eif_list) > 0:
        data_dir = get_dir_PATCH_DATA(instance)
        os.makedirs(data_dir)
        for eif_file in eif_list:
            try:
                shutil.copy2(eif_file, data_dir)
            except EnvironmentError as e:
                print("Unable to copy file. %s" % e)

        eif_list = list_files_of_given_type(data_dir, ".eif")
        if len(eif_list) > 0:
            with open(get_filename_UPGRADE10_eif(instance), mode="w") as f:
                f.writelines(const_UPGRADE10_HEADER)
                counter = 1
                for eif_file in eif_list:
                    eif_file_name = splitfilename(eif_file)
                    f.writelines(make_upgrade10_eif_string_by_file_name(counter, eif_file_name)+"\n")
                    counter += 1
                f.writelines(const_UPGRADE10_FOOTER)
# -------------------------------------------------------------------------------------------------


def main():
    global_settings = read_config()
    clean(const_dir_TEMP)
    #clean(const_dir_PATCH)
    global_settings.StarteamPassword = getpassword('ENTER StarTeam password:')
    print('BEGIN DOWNLOADING')
    if download_starteam_by_label(global_settings) == 0:
        compare_directories_BEFORE_and_AFTER()
        search_for_DATA_FILES_without_10_FILES_and_download_them(global_settings, const_instance_BANK)
        search_for_DATA_FILES_without_10_FILES_and_download_them(global_settings, const_instance_CLIENT)
        build_upgrade10_eif(const_instance_BANK)
        build_upgrade10_eif(const_instance_CLIENT)
    print("DONE!!!")
# ---- поехали ------------------------------------------------------------------------------------


main()
