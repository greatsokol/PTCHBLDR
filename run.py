import configparser
import os
import shutil
import subprocess
import filecmp
import re
import glob

const_dir_CURRENT = os.path.abspath("")
const_dir_TEMP = os.path.join(const_dir_CURRENT, "TEMP")
const_dir_BEFORE = os.path.join(const_dir_TEMP, "BEFORE")
const_dir_AFTER = os.path.join(const_dir_TEMP, "AFTER")
const_dir_COMPARED = os.path.join(const_dir_TEMP, "_COMPARE_RESULT")
const_dir_PATCH = os.path.join(const_dir_TEMP, "PATCH")
get_dir_COMPARED_BASE = lambda instance: os.path.join(os.path.join(const_dir_COMPARED, "BASE"), instance)
get_dir_PATCH = lambda instance: os.path.join(const_dir_PATCH, instance)
get_dir_PATCH_DATA = lambda instance: os.path.join(get_dir_PATCH(instance), "DATA")
get_dir_PATCH_CBSTART = lambda instance, version='': os.path.join(get_dir_PATCH(instance), "CBSTART{}".format(version))
get_dir_PATCH_LIBFILES = lambda instance, version='': os.path.join(get_dir_PATCH(instance), "LIBFILES{}".format(version))
get_dir_PATCH_LIBFILES_BNK = lambda instance, version='': os.path.join(get_dir_PATCH(instance), "LIBFILES{}.BNK".format(version))
get_dir_PATCH_LIBFILES_EXE = lambda instance, version='': os.path.join(get_dir_PATCH_LIBFILES(instance, version), "EXE")
get_dir_PATCH_LIBFILES_SUBSYS = lambda instance, version='': os.path.join(get_dir_PATCH_LIBFILES(instance, version), "SUBSYS")
get_dir_PATCH_LIBFILES_INSTCLNT = lambda instance, version='': os.path.join(get_dir_PATCH_LIBFILES_SUBSYS(instance, version), "INSTCLNT")
get_dir_PATCH_LIBFILES_INETTEMP = lambda instance, version='': os.path.join(get_dir_PATCH_LIBFILES_INSTCLNT(instance, version), "INETTEMP")
get_dir_PATCH_LIBFILES_SYSTEM = lambda instance, version='': os.path.join(get_dir_PATCH_LIBFILES(instance, version), "SYSTEM")
get_filename_UPGRADE10_eif = lambda instance: os.path.join(get_dir_PATCH(instance), "Upgrade(10).eif")
splitfilename = lambda filename: os.path.split(filename)[1]
print1 = lambda message: print("\t"+message)
print2 = lambda message: print("\t\t"+message)

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
const_instance_IC = "IC"
const_instance_CLIENT = "CLIENT"

const_excluded_build_for_BANK = ['BRHelper.exe',
                                 'BsDataPump.exe',
                                 'BSISet.exe',
                                 'BSLEdit.exe',
                                 'BSSICLogParser.exe',
                                 'BSSOAPServer.exe',
                                 'bssPluginHost.exe',
                                 'BSSPluginManager.exe',
                                 'BssPluginSetup.exe',
                                 'BssPluginSetupNoHost.exe',
                                 'BssPluginWebKitSetup.exe',
                                 'bssuinst.exe',
                                 'BuildUp.exe',
                                 'CalcCRC.exe',
                                 'CBStart.exe',
                                 'CliEx.exe',
                                 'ConvertAttaches.exe',
                                 'Copier.exe',
                                 'ECtrlsD.bpl',
                                 'Eif2Base.exe',
                                 'EXECBLL.exe',
                                 'Install.exe',
                                 'LResCmp.exe',
                                 'LResEIF.exe',
                                 'LResExpt.bpl',
                                 'ODBCMon.exe',
                                 'PBLS.exe',
                                 'PrintServer.exe',
                                 'RBTreeD.bpl',
                                 'RToolsDT.bpl',
                                 'Setup.exe',
                                 'SynEditD.bpl',
                                 'UpdateIc.exe',
                                 'VirtualTreesD.bpl',
                                 'eif2base64_srv.exe',
                                 'eif2base64_cli.dll',
                                 'LocProt.dll',
                                 'PerfControl.dll',
                                 'upgr20.dll']
const_excluded_build_for_CLIENT = const_excluded_build_for_BANK + ['BSAuthServer.exe',
                                                                   'BSAuthService.exe',
                                                                   'bscc.exe',
                                                                   'BSEM.exe',
                                                                   'BSMonitorServer.exe',
                                                                   'BSMonitorService.exe',
                                                                   'btrdict.exe',
                                                                   'CBServ.exe',
                                                                   'ComBuff.exe',
                                                                   'Compiler.exe',
                                                                   'Dictman.exe',
                                                                   'Protcore.exe',
                                                                   'RTS.exe',
                                                                   'RTSAdmin.exe',
                                                                   'RTSInfo.exe',
                                                                   'RTSMBC.exe',
                                                                   'RTSServ.exe',
                                                                   'TCPAgent.exe',
                                                                   'TRedir.exe',
                                                                   'upgr20i.exe',
                                                                   'bsi.dll',
                                                                   'CalcCRC.dll',
                                                                   'cr_altok2x.dll',
                                                                   'cr_ccm3x2x.dll',
                                                                   'cr_epass2x.dll',
                                                                   'cr_pass2x.dll',
                                                                   'cr_sms2x.dll',
                                                                   'dboBlobTbl.dll',
                                                                   'dboFileAttach.dll',
                                                                   'eif2base64_cli.dll',
                                                                   'ILShield.dll',
                                                                   'ILTMail.dll',
                                                                   'llAzkLnk.dll',
                                                                   'llExCtrl.dll',
                                                                   'llRpJet2.dll',
                                                                   'LocProt.dll',
                                                                   'npBSSPlugin.dll',
                                                                   'PerfControl.dll',
                                                                   'upgr20.dll']


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
    BuildBank = ""
    BuildIC = ""
    BuildClient = ""
# -------------------------------------------------------------------------------------------------


def getpassword(message):
    import getpass
    # running under PyCharm or not
    if "PYCHARM_HOSTED" in os.environ:
        return getpass.fallback_getpass(message)
    else:
        return getpass.getpass(message)
# -------------------------------------------------------------------------------------------------


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
# -------------------------------------------------------------------------------------------------


def copyfiles(src_dir, dest_dir, wildcard='*.*', excluded_files=[]):
    for filename_with_path in glob.glob(os.path.join(src_dir, wildcard)):
        filename = splitfilename(filename_with_path)
        if filename not in excluded_files:
            makedirs(dest_dir)
            shutil.copy2(filename_with_path, dest_dir)

# -------------------------------------------------------------------------------------------------


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
        print1("CLEANING done")
    except FileNotFoundError:
        pass  # если папка TEMP отсутствует, то продолжаем молча
    except BaseException as e:
        print1("Error when cleaning directories ({})".format(e))
        raise
# -------------------------------------------------------------------------------------------------


def read_config():
    settings = GlobalSettings()
    ini_filename = "settings.ini"
    error_header = "Error when reading settings from file {} ".format(ini_filename)
    section_special = "SPECIAL"
    section_common = "COMMON"
    section_labels = "LABELS"
    section_build = "BUILD"
    try:
        parser = configparser.RawConfigParser()
        res = parser.read(ini_filename)
        if res.count == 0:  # если файл настроек не найден
            raise FileNotFoundError("NOT FOUND {}".format(ini_filename))
        settings.stcmd = parser.get(section_common, "stcmd").strip()
        settings.StarteamServer = parser.get(section_common, "StarteamServer").strip()
        settings.StarteamPort = parser.get(section_common, "StarteamPort").strip()
        settings.StarteamProject = parser.get(section_special, "StarteamProject").strip()
        settings.StarteamView = parser.get(section_special, "StarteamView").strip()
        settings.StarteamLogin = parser.get(section_special, "StarteamLogin").strip()
        settings.Labels = parser.items(section_labels)
        settings.BuildBank = parser.get(section_build, "Bank").strip()
        settings.BuildClient = parser.get(section_build, "Client").strip()
        settings.BuildIC = parser.get(section_build, "IC").strip()

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
            if label == "":
                print1("NOT DEFINED label \"{}\" (empty)".format(key))
            else:
                print1("DOWNLOADING for label \"{}\". Please wait...".format(label))
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
                    print2("FINISHED downloading for label \"{}\"".format(label))
                    total_result = 0
                else:
                    print2("ERROR when downloading label \"{}\"".format(label))

    except BaseException as e:
        print2("Error when downloading from Starteam ({})".format(e))
    return total_result
# -------------------------------------------------------------------------------------------------


def download_starteam_by_file(settings, path, filename, where_to_save):
    total_result = -1
    try:
        print1("DOWNLOADING file \"{}\". Please wait...".format(path+filename))
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

        # print(launch_string)
        result = subprocess.call(launch_string)
        if result == 0:
            print2("FINISHED downloading file \"{}\"".format(filename))
            total_result = 0
        else:
            print2("ERROR when downloading file \"{}\"".format(filename))

    except BaseException as e:
        print2("Error when downloading from Starteam ({})".format(e))
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
                print2("copying {}".format(path))
                if not os.path.exists(wheretocopy):
                    os.makedirs(wheretocopy)
                shutil.copy2(path, wheretocopy)
            else:
                print2("something wrong {} -> {}".format(path, wheretocopy))

    if dircmp.right_only:
        for file in dircmp.right_only:
            path = os.path.join(after, file)
            if os.path.isfile(path):
                print2("copying {}".format(path))
                if not os.path.exists(wheretocopy):
                    os.makedirs(wheretocopy)
                shutil.copy2(path, wheretocopy)
            else:
                print2("copying DIR with contents {}".format(path))
                clean(os.path.join(wheretocopy, file))
                shutil.copytree(path, os.path.join(wheretocopy, file))
# -------------------------------------------------------------------------------------------------


def compare_directories_BEFORE_and_AFTER():
    if os.path.exists(const_dir_BEFORE):
        print("BEGIN compare directories:")
        print1("BEFORE: {}".format(const_dir_BEFORE))
        print1("AFTER:  {}".format(const_dir_AFTER))
        __compare_and_copy_dirs_recursively__(const_dir_BEFORE, const_dir_AFTER, const_dir_COMPARED)
    else:
        os.rename(const_dir_AFTER, const_dir_COMPARED)
        print1("USING folder 'AFTER' as compare result, because 'BEFORE' not exists:")
        print2("BEFORE (not exists): {}".format(const_dir_BEFORE))
        print2("AFTER              : {}".format(const_dir_AFTER))

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
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|FALSE|TRUE|FALSE|NULL|NULL|NULL|NULL|NULL|'Таблицы'>"  # TODO здесь все сложно
        elif structure_type == "12":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|TRUE|NULL|NULL|NULL|NULL|NULL|'Визуальные формы'>"
        elif structure_type == "14":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Конфигурации'>"
        elif structure_type == "16":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Автопроцедуры'>"
        elif structure_type == "18":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Профили'>"
        elif structure_type == "19":
            result = "<{}|{}|'{}'|TRUE|FALSE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Роли'>"
        elif structure_type == "20":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Привелегии'>"
        elif structure_type == "21":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Пользователи'>"
        elif structure_type == "30":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|TRUE|NULL|NULL|NULL|NULL|NULL|'Сценарии'>"
        elif structure_type == "65":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'RTS что-то'>"
        elif structure_type == "66":
            result = "<352|66|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'RTS Errors params'>"
        elif structure_type == "71":
            result = "<{}|{}|'{}'|TRUE|FALSE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Генераторы'>"
        elif structure_type == "72":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Структуры отображений'>"
        elif structure_type == "73":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Хранимые процедуры'>"
        elif structure_type == "81":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Простые операции'>"
        elif structure_type == "82":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Табличные операции'>"
        elif structure_type == "83":
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Документарные операции'>"
        elif structure_type == "84":
            result = "<{}|{}|'{}'|TRUE|FALSE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Статусы'>"
        else:
            print2("ERROR unknown structure type {} for filename {}".format(structure_type, file_name))

        return "  "+result.format(counter, structure_type, file_name)
    else:
        print2("ERROR can't detect structure type by filename ({})".format(file_name))
# -------------------------------------------------------------------------------------------------


def search_for_DATA_FILES_without_10_FILES_and_download_them(settings, instance):
    eif_list = list_files_of_given_type(get_dir_COMPARED_BASE(instance), ".eif")
    for eif_file in eif_list:
        # проверим соответствует ли название файла формату "*(data).eif"
        file_type_match = re.findall("\(data\)\.eif", eif_file, flags=re.IGNORECASE)
        if len(file_type_match):
            eif10_file = str(eif_file).replace(file_type_match[0],"(10).eif")
            # отрежем путь (splitfilename)
            eif10_file = splitfilename(eif10_file)
            # и проверим есть ли файл eif10_file в списке файлов eif_list
            exists = [file1 for file1 in eif_list if re.search(re.escape(eif10_file), file1)]
            if not exists:
                # если файла eif10_file в списке загруженных файлов нет, то выгрузим его из стартима
                download_starteam_by_file(settings, "BASE/"+instance+"/TABLES/", eif10_file, const_dir_COMPARED)
# -------------------------------------------------------------------------------------------------


def generate_upgrade10_eif(instance):
    eif_list = list_files_of_given_type(get_dir_COMPARED_BASE(instance), ".eif")
    if len(eif_list) > 0:
        data_dir = get_dir_PATCH_DATA(instance)
        os.makedirs(data_dir)
        for eif_file in eif_list:
            try:
                shutil.copy2(eif_file, data_dir)
            except EnvironmentError as e:
                print1("Unable to copy file. %s" % e)

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


def __download_build__(build_path, dest_path, version, file_type, excluded_files = []):
    build_path = os.path.join(build_path, 'Win{}\\Release'.format(version))
    copyfiles(build_path, dest_path, file_type, excluded_files)
# -------------------------------------------------------------------------------------------------


def download_build(settings, instance):
    if instance == '':
        print("NOT DOWNLOADING build: no instance specified")
        return

    if instance == const_instance_BANK:
        build_path = settings.BuildBank
    elif instance == const_instance_IC:
        build_path = settings.BuildIC
    elif instance == const_instance_CLIENT:
        build_path = settings.BuildClient

    if build_path == '':
        print("NOT DOWNLOADING build for {}: no build path specified".format(instance))
        return

    print("BEGIN DOWNLOADING build {} for {}".format(build_path, instance))
    if not os.path.exists(build_path):
        print1("PATH {} does not exists".format(build_path))
        return

    if instance == const_instance_BANK:
        excluded_files = const_excluded_build_for_BANK
    elif instance == const_instance_IC:
        excluded_files = const_excluded_build_for_BANK
    elif instance == const_instance_CLIENT:
        excluded_files = const_excluded_build_for_CLIENT

    is20 = ('20.1' in build_path) or ('20.2' in build_path)

    if is20: # для билда 20-ой версии
        if instance == const_instance_IC: # выкладываем билд плагина для ИК
            __download_build__(settings.BuildBank, get_dir_PATCH_LIBFILES_INETTEMP(const_instance_BANK), '32', 'bssetup.msi', [])
            __download_build__(settings.BuildBank, get_dir_PATCH_LIBFILES_INETTEMP(const_instance_BANK), '32', 'CalcCRC.exe', [])
            __download_build__(build_path, get_dir_PATCH_LIBFILES_INETTEMP(const_instance_BANK), '32', 'BssPluginSetup.exe', [])
            __download_build__(build_path, get_dir_PATCH_LIBFILES_INETTEMP(const_instance_BANK), '32', 'BssPluginWebKitSetup.exe', [])
            __download_build__(build_path, get_dir_PATCH_LIBFILES_INETTEMP(const_instance_BANK), '32', 'BssPluginWebKitSetup.exe', [])
            for version in ['32', '64']: # выкладываем билд в LIBFILES32(64).BNK
                __download_build__(build_path, get_dir_PATCH_LIBFILES_BNK(instance, version), version, 'UpdateIc.exe', [])
        else:
            for version in ['32', '64']: # выкладываем остальной билд для Б и БК
                __download_build__(build_path, get_dir_PATCH_LIBFILES_EXE(instance, version), version, '*.exe', excluded_files)
                __download_build__(build_path, get_dir_PATCH_LIBFILES_EXE(instance, version), version, '*.ex', excluded_files)
                __download_build__(build_path, get_dir_PATCH_LIBFILES_EXE(instance, version), version, '*.bpl', excluded_files)
                __download_build__(build_path, get_dir_PATCH_CBSTART(instance, version), version, 'CBStart.exe', [])
                __download_build__(build_path, get_dir_PATCH_LIBFILES_SYSTEM(instance, version), version, '*.dll', excluded_files)

    print1("DONE DOWNLOADING build for {}".format(instance))


# -------------------------------------------------------------------------------------------------

def main():
    global_settings = read_config()
    clean(const_dir_TEMP)
    # clean(const_dir_PATCH)
    global_settings.StarteamPassword = getpassword('ENTER StarTeam password:')
    print('BEGIN DOWNLOADING')
    if download_starteam_by_label(global_settings) == 0:
        compare_directories_BEFORE_and_AFTER()
        search_for_DATA_FILES_without_10_FILES_and_download_them(global_settings, const_instance_BANK)
        search_for_DATA_FILES_without_10_FILES_and_download_them(global_settings, const_instance_CLIENT)
        generate_upgrade10_eif(const_instance_BANK)
        generate_upgrade10_eif(const_instance_CLIENT)
        download_build(global_settings, const_instance_BANK)
        download_build(global_settings, const_instance_IC)
        download_build(global_settings, const_instance_CLIENT)
    print("DONE!!!")
# -------------------------------------------------------------------------------------------------


def main_debug_without_clean():
    global_settings = read_config()
    #global_settings.StarteamPassword = getpassword('ENTER StarTeam password:')
    #print('BEGIN DOWNLOADING')
    #if download_starteam_by_label(global_settings) == 0:
    #    compare_directories_BEFORE_and_AFTER()
    #search_for_DATA_FILES_without_10_FILES_and_download_them(global_settings, const_instance_BANK)
    #search_for_DATA_FILES_without_10_FILES_and_download_them(global_settings, const_instance_CLIENT)
    #generate_upgrade10_eif(const_instance_BANK)
    #generate_upgrade10_eif(const_instance_CLIENT)
    download_build(global_settings, const_instance_BANK)
    download_build(global_settings, const_instance_IC)
    download_build(global_settings, const_instance_CLIENT)
    print("DONE!!!")
# -------------------------------------------------------------------------------------------------

#main()
main_debug_without_clean()
