import configparser
import os
import shutil
import subprocess
import filecmp
import re
import tempfile
import zipfile
import struct
import fnmatch
import sys


const_instance_BANK = "BANK"
const_instance_IC = "IC"
const_instance_CLIENT = "CLIENT"
const_instance_CLIENT_MBA = "CLIENT_MBA"
const_dir_TEMP = os.path.join(os.path.abspath(''), '_TEMP')
const_dir_TEMP_BUILD_BK = os.path.join(const_dir_TEMP, '_BUILD', 'BK')
const_dir_TEMP_BUILD_IC = os.path.join(const_dir_TEMP, '_BUILD', 'IC')
const_dir_TEMP_TEMPSOURCE = os.path.join(const_dir_TEMP, '_TEMP_SOURCE')
const_dir_BEFORE = os.path.join(const_dir_TEMP, '_BEFORE')
const_dir_AFTER = os.path.join(const_dir_TEMP, '_AFTER')
const_dir_COMPARED = os.path.join(const_dir_TEMP, '_COMPARE_RESULT')
const_dir_COMPARED_BLS = os.path.join(const_dir_COMPARED, 'BLS')
const_dir_COMPARED_BLS_SOURCE = os.path.join(const_dir_COMPARED_BLS, 'SOURCE')
const_dir_COMPARED_BLS_SOURCE_RCK = os.path.join(const_dir_COMPARED_BLS_SOURCE, 'RCK')
const_dir_PATCH = os.path.join(const_dir_TEMP, 'PATCH')

dir_COMPARED_BASE = lambda instance: os.path.join(os.path.join(const_dir_COMPARED, 'BASE'), instance)
dir_PATCH = lambda instance='': os.path.join(const_dir_PATCH, instance)
dir_PATCH_DATA = lambda instance: os.path.join(dir_PATCH(instance), 'DATA')
dir_PATCH_CBSTART = lambda instance, version='': os.path.join(dir_PATCH(instance), 'CBSTART{}'.format(version))
dir_PATCH_LIBFILES = lambda instance, version='': os.path.join(dir_PATCH(instance), 'LIBFILES{}'.format(version))
dir_PATCH_LIBFILES_USER = lambda instance: os.path.join(dir_PATCH_LIBFILES(instance), 'USER')
dir_PATCH_LIBFILES_SOURCE = os.path.join(dir_PATCH_LIBFILES(const_instance_BANK), 'SOURCE')

dir_PATCH_LIBFILES_BNK = lambda version='': os.path.join(dir_PATCH(const_instance_BANK), 'LIBFILES{}.BNK'.format(version))
dir_PATCH_LIBFILES_BNK_ADD = lambda: os.path.join(dir_PATCH_LIBFILES_BNK(), 'add')
dir_PATCH_LIBFILES_BNK_BSISET_EXE = lambda: os.path.join(dir_PATCH_LIBFILES_BNK(), 'bsiset', 'EXE')
dir_PATCH_LIBFILES_BNK_LICENSE_EXE = lambda: os.path.join(dir_PATCH_LIBFILES_BNK(), 'license', 'EXE')
dir_PATCH_LIBFILES_BNK_RTS = lambda: os.path.join(dir_PATCH_LIBFILES_BNK(), 'rts')
dir_PATCH_LIBFILES_BNK_RTS_EXE = lambda: os.path.join(dir_PATCH_LIBFILES_BNK_RTS(), 'EXE')
dir_PATCH_LIBFILES_BNK_RTS_SYSTEM = lambda: os.path.join(dir_PATCH_LIBFILES_BNK_RTS(), 'SYSTEM')

dir_PATCH_LIBFILES_BNK_WWW = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK(version), 'WWW')
dir_PATCH_LIBFILES_BNK_WWW_EXE = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW(version), 'EXE')
dir_PATCH_LIBFILES_BNK_WWW_BSIscripts = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW(version), 'BSI_scripts')
dir_PATCH_LIBFILES_BNK_WWW_BSIscripts_RTIc = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW_BSIscripts(version), 'rt_ic')
dir_PATCH_LIBFILES_BNK_WWW_BSIscripts_RTAdmin = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW_BSIscripts(version), 'rt_Admin')
dir_PATCH_LIBFILES_BNK_WWW_BSIscripts_RTWa = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW_BSIscripts(version), 'rt_wa')
dir_PATCH_LIBFILES_BNK_WWW_BSIsites = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW(version), 'BSI_sites')
dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTIc = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW_BSIsites(version), 'rt_ic')
dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTWa = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW_BSIsites(version), 'rt_wa')
dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTIc_CODE = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTIc(version), 'CODE')
dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTWa_CODE = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTWa(version), 'CODE')

dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTIc_CODE_BuildVersion = lambda build_version, version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTIc_CODE(version), build_version)
dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTWa_CODE_BuildVersion = lambda build_version, version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTWa_CODE(version), build_version)

dir_PATCH_LIBFILES_EXE = lambda instance, version='': os.path.join(dir_PATCH_LIBFILES(instance, version), 'EXE')
dir_PATCH_LIBFILES_SYSTEM = lambda instance, version='': os.path.join(dir_PATCH_LIBFILES(instance, version), 'SYSTEM')
dir_PATCH_LIBFILES_SUBSYS = lambda instance, version='': os.path.join(dir_PATCH_LIBFILES(instance, version), 'SUBSYS')
dir_PATCH_LIBFILES_INSTCLNT = lambda : os.path.join(dir_PATCH_LIBFILES_SUBSYS(const_instance_BANK), 'INSTCLNT')
dir_PATCH_LIBFILES_INETTEMP = lambda : os.path.join(dir_PATCH_LIBFILES_INSTCLNT(), 'INETTEMP')
dir_PATCH_LIBFILES_TEMPLATE = lambda : os.path.join(dir_PATCH_LIBFILES_INSTCLNT(), 'TEMPLATE')

dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX = lambda version: os.path.join(dir_PATCH_LIBFILES_TEMPLATE(), 'DISTRIB.X{}'.format(version))
dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX_CLIENT = lambda version: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX(version), 'CLIENT')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX_CLIENT_EXE = lambda version: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX_CLIENT(version), 'EXE')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX_CLIENT_SYSTEM = lambda version: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX_CLIENT(version), 'SYSTEM')
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGEX = lambda version: os.path.join(dir_PATCH_LIBFILES_TEMPLATE(), 'Language.X{}'.format(version))
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGEX_EN = lambda version: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_LANGUAGEX(version), 'ENGLISH')
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGEX_RU = lambda version: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_LANGUAGEX(version), 'RUSSIAN')

dir_PATCH_LIBFILES_TEMPLATE_DISTRIB = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE(), 'DISTRIB')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_DISTRIB(), 'CLIENT')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_EXE = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT(), 'EXE')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_SYSTEM = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT(), 'SYSTEM')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_USER = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT(), 'USER')
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE(), 'Language')
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_EN = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE(), 'ENGLISH')
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_RU = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE(), 'RUSSIAN')
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_EN_CLIENT_SYSTEM = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE(), 'ENGLISH', 'CLIENT', 'SYSTEM')
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_RU_CLIENT_SYSTEM = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE(), 'RUSSIAN', 'CLIENT', 'SYSTEM')

get_filename_UPGRADE10_eif = lambda instance: os.path.join(dir_PATCH(instance), 'Upgrade(10).eif')
print1 = lambda message: print('\t'+message)
#print2 = lambda message: print('\t\t'+message)


def getLastElementOfPath(path):
    result = ''
    path = os.path.normpath(path)
    names = path.split(os.path.sep)
    if len(names):
        result = names[len(names) - 1]
    return result


def split_filename(path):
    result = ''
    if os.path.isfile(path):
        result = getLastElementOfPath(path)
    return result


def split_lastdirname(path):
    result = ''
    if os.path.isdir(path):
        result = getLastElementOfPath(path)
    return result

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
const_excluded_build_for_BANK = ['autoupgr.exe', 'operedit.exe',
                                 'crccons.exe', 'crprotst.exe',
                                 'mbank.exe', 'memleak.exe',
                                 'msysleak.exe', 'nsfilead.exe',
                                 'nsservis.exe', 'nssrv.exe',
                                 'nstcpad.exe',
                                 'brhelper.exe', 'ctunnel.exe',
                                 'defstart.exe', 'defupdt.exe',
                                 'dosprot.exe',
                                 'lang2htm.exe',
                                 'licjoin.exe', 'lresedit.exe',
                                 'bsledit.exe', 'bssiclogparser.exe',
                                 'bssoapserver.exe', 'bsspluginhost.exe',
                                 'bsspluginmanager.exe', 'bsspluginsetup.exe',
                                 'bsspluginsetupnohost.exe', 'bsspluginwebkitsetup.exe',
                                 'bssuinst.exe', 'cliex.exe',
                                 'convertattaches.exe', 'copier.exe',
                                 'ectrlsd.bpl', 'eif2base.exe',
                                 'install.exe', 'lrescmp.exe',
                                 'lreseif.exe', 'odbcmon.exe',
                                 'abank.exe', 'alphalgn.exe',
                                 'pbls.exe',
                                 'rbtreed.bpl', 'rtoolsdt.bpl',
                                 'pmonitor.bpl', 'pmonitor.exe',
                                 'syneditd.bpl', 'updateic.exe',
                                 'virtualtreesd.bpl', 'eif2base64_srv.exe',
                                 'eif2base64_cli.dll', 'odbclog.dll',
                                 'olha.dll', 'olha10.dll',
                                 'olha9.dll', 'phemng.dll',
                                 'pika.dll',
                                 'authserv.exe',
                                 'bsroute.exe', 'bssaxset.exe',
                                 'bsdebug.exe', 'chngtree.exe',
                                 'blstest.exe', 'ptchglue.exe', 'ptchhelp.exe',
                                 'repcmd.exe', 'reqexec.exe',
                                 'sysupgr.exe',
                                 'testodbc.exe', 'testsign.exe',
                                 'textrepl.exe', 'transtbl.exe',
                                 'treeedit.exe', 'vbank.exe',
                                 'verifyer.exe']


# todo убрать из клиента rg_*
const_excluded_build_for_CLIENT = const_excluded_build_for_BANK + ['bsrdrct.exe',
                                                                   'bsauthserver.exe',
                                                                   'bsauthservice.exe',
                                                                   'bsem.exe',
                                                                   'cbank500.exe',
                                                                   'gbank.exe',
                                                                   'bsiset.exe',
                                                                   'inetcfg.exe',
                                                                   'bsmonitorserver.exe',
                                                                   'bsmonitorservice.exe',
                                                                   'btrdict.exe',
                                                                   'cbserv.exe',
                                                                   'combuff.exe',
                                                                   'alphamon.exe',
                                                                   'admin.exe',
                                                                   'phoneserver.exe',
                                                                   'phoneservice.exe',
                                                                   'iniconf.exe',
                                                                   'bsphone.bpl',
                                                                   'phetools.bpl',
                                                                   'infoserv.exe',
                                                                   'infoservice.exe',
                                                                   'bscc.exe',
                                                                   'protcore.exe',
                                                                   'rts.exe',
                                                                   'rtsadmin.exe',
                                                                   'rtsinfo.exe',
                                                                   'rtsmbc.exe',
                                                                   'rtsserv.exe',
                                                                   'bsdatapump.exe',
                                                                   'tcpagent.exe',
                                                                   'BSSAxInf.exe',
                                                                   'tredir.exe',
                                                                   'upgr20i.exe',
                                                                   'bsi.dll',
                                                                   'cr_altok2x.dll',
                                                                   'cr_ccm3x2x.dll',
                                                                   'cr_epass2x.dll',
                                                                   'cr_pass2x.dll',
                                                                   'cr_sms2x.dll',
                                                                   'dboblobtbl.dll',
                                                                   'dbofileattach.dll',
                                                                   'eif2base64_cli.dll',
                                                                   'ilshield.dll',
                                                                   'iltmail.dll',
                                                                   'llazklnk.dll',
                                                                   'llexctrl.dll',
                                                                   'llrpjet2.dll',
                                                                   'npbssplugin.dll',
                                                                   'perfcontrol.dll',
                                                                   'ptchmake.exe']
# -------------------------------------------------------------------------------------------------


class GlobalSettings:
    stcmd = ''
    StarteamServer = ''
    StarteamPort = ''
    StarteamLogin = ''
    StarteamProject = ''
    StarteamView = ''
    StarteamPassword = ''
    Labels = []
    BuildBK = ''
    BuildIC = ''
    BuildCrypto = ''
    PlaceBuildIntoPatch = False
    ClientEverythingInEXE = False
    LicenseServer = ''
    LicenseProfile = ''
# -------------------------------------------------------------------------------------------------


def getpassword(message):
    import getpass
    # running under PyCharm or not
    if 'PYCHARM_HOSTED' in os.environ:
        return getpass.fallback_getpass(message)
    else:
        return getpass.getpass(message)
# -------------------------------------------------------------------------------------------------


def makedirs(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except BaseException as e:
        print1('ERROR: can''t create directory "{}" ({})'.format(path, e))
# -------------------------------------------------------------------------------------------------


def list_files(path, mask):
    return [os.path.join(d, filename) for d, _, files in os.walk(path) for filename in fnmatch.filter(files, mask)]


# -------------------------------------------------------------------------------------------------
def list_files_by_list(path, mask_list):
    res_list = []
    for mask in mask_list:
        res_list += [os.path.join(d, filename) for d, _, files in os.walk(path) for filename in fnmatch.filter(files, mask)]
    return res_list


# -------------------------------------------------------------------------------------------------
def list_files_remove_paths_and_change_extension(path, newext, mask_list):
    return [os.path.splitext(bls_file)[0] + newext for bls_file in
                  [split_filename(bls_file) for bls_file in list_files_by_list(path, mask_list)]]


# Print iterations progress
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 2, barLength = 100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    filledLength    = int(round(barLength * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '#' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('%s [%s] %s%s %s\r' % (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()
    if iteration == total:
        print("\n")


# -------------------------------------------------------------------------------------------------
def copyfiles(src_dir, dest_dir, wildcards=['*.*'], excluded_files=[]):
    for wildcard in wildcards:
        files = list_files(src_dir, wildcard)
        for filename_with_path in files:
            filename = split_filename(filename_with_path)
            if filename.lower() not in excluded_files and filename != '.' and filename != '..':
                makedirs(dest_dir)
                try:
                    shutil.copy2(filename_with_path, dest_dir)
                except BaseException as e:
                    print1('ERROR: can\'t copy file "{}" to "{}" ({})'.format(filename_with_path, dest_dir, e))


# -------------------------------------------------------------------------------------------------
def copyfiles_of_version(src_dir, dest_dir, exe_version, wildcards=['*.*'], excluded_files=[]):
    for wildcard in wildcards:
        files = list_files(src_dir, wildcard)
        for filename_with_path in files:
            filename = split_filename(filename_with_path)
            if filename.lower() not in excluded_files and filename != '.' and filename != '..':
                makedirs(dest_dir)
                try:
                    if get_binary_platform(filename_with_path) == exe_version:
                        shutil.copy2(filename_with_path, dest_dir)
                except BaseException as e:
                    print1('ERROR: can\'t copy file "{}" to "{}" ({})'.format(filename_with_path, dest_dir, e))


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
        raise BaseException(exc_info)


def clean(path, masks=[]):
    if os.path.exists(path):
        try:
            if masks:
                print('CLEANING {} for {} files'.format(path, masks))
                for mask in masks:
                    [os.remove(os.path.join(d, filename)) for d, _, files in os.walk(path) for filename in fnmatch.filter(files, mask)]
            else:
                print('CLEANING {}'.format(path))
                shutil.rmtree(path, onerror=__onerror_handler__)
        except FileNotFoundError:
            pass  # если папка отсутствует, то продолжаем молча
        except BaseException as e:
            print1('ERROR when cleaning ({})'.format(e))
            return False
    return True
# -------------------------------------------------------------------------------------------------


def read_config():
    settings = GlobalSettings()
    ini_filename = 'settings.ini'
    section_special = 'SPECIAL'
    section_common = 'COMMON'
    section_labels = 'LABELS'
    section_build = 'BUILD'
    try:
        parser = configparser.RawConfigParser()
        res = parser.read(ini_filename, encoding="UTF-8")
        if res.count == 0:  # если файл настроек не найден
            raise FileNotFoundError('NOT FOUND {}'.format(ini_filename))
        settings.stcmd = parser.get(section_common, 'stcmd').strip()
        settings.StarteamServer = parser.get(section_common, 'StarteamServer').strip()
        settings.StarteamPort = parser.get(section_common, 'StarteamPort').strip()
        settings.StarteamProject = parser.get(section_special, 'StarteamProject').strip()
        settings.StarteamView = parser.get(section_special, 'StarteamView').strip()
        settings.StarteamLogin = parser.get(section_special, 'StarteamLogin').strip()
        settings.LicenseServer = parser.get(section_special, 'LicenseServer').strip()
        settings.LicenseProfile = parser.get(section_special, 'LicenseProfile').strip()
        settings.Labels = parser.items(section_labels)
        settings.BuildBK = parser.get(section_build, 'BK').strip()
        settings.BuildIC = parser.get(section_build, 'IC').strip()
        settings.BuildCrypto = parser.get(section_build, 'Crypto').strip()
        settings.PlaceBuildIntoPatch = parser.get(section_build, 'PlaceBuildIntoPatch').lower() == 'true'
        settings.ClientEverythingInEXE = parser.get(section_special, 'ClientEverythingInEXE').lower() == 'true'

        # проверка Labels -----------------------------------
        all_labels = ''
        for label in settings.Labels:
            all_labels += label[1].strip()

        if not settings.Labels or not all_labels:  # Если не дали совсем никаких меток для загрузки
            raise ValueError('NO LABELS defined in {}'.format(ini_filename))

        # проверка stsmd -----------------------------------
        if settings.stcmd:  # если пусть к stcmd не задан
            settings.stcmd = os.path.normpath(settings.stcmd)
            settings.stcmd = settings.stcmd+os.sep+'stcmd.exe'
            if not os.path.exists(settings.stcmd):
                raise FileNotFoundError('NOT FOUND '+settings.stcmd)
        else:
            raise FileNotFoundError('NOT DEFINED path to stcmd')

        # проверка путей к билду
        if settings.BuildBK and not os.path.exists(settings.BuildBK):
            raise FileNotFoundError('NOT FOUND "{}"'.format(settings.BuildBK))
        if settings.BuildIC and not os.path.exists(settings.BuildIC):
            raise FileNotFoundError('NOT FOUND "{}"'.format(settings.BuildIC))

    except BaseException as e:
        print('ERROR when reading settings from file "{}":\n\t\t{}'.format(ini_filename, e))
        return None
    else:
        print('SETTINGS LOADED:\n\tStarteamProject = {}\n\tStarteamView = {}\n\tLabels = {}\n\tstcmd = {}'.
              format(settings.StarteamProject, settings.StarteamView, settings.Labels, settings.stcmd))
        return settings
# -------------------------------------------------------------------------------------------------


def check_labels(settings):
    pass;
# -------------------------------------------------------------------------------------------------


def download_starteam(settings, labels_list, path_for_after, path_for_before, st_path_to_download='', st_file_to_download=''):
    total_result = False
    key_AltStarteamView = "_StarteamView".lower()  # Приставка к названию метки, в которой содержится название доп вида стартима
    try:
        if labels_list is None:
            labels_list = [('any','')]
        for key, label in labels_list:
            if key_AltStarteamView not in key:  # Если название метки не содержит "_StarteamView"
                if not label and not st_file_to_download:
                    raise ValueError('No label or file to download specified')
                message = 'DOWNLOADING'
                if st_file_to_download:
                    message += ' files "{}{}"'.format(st_path_to_download, st_file_to_download)
                if label:
                    message += ' files for label "{}"'.format(label)


                if (key == 'LabelBefore'.lower()) or (key == 'DateBefore'.lower()):
                    outdir = path_for_before
                else:
                    outdir = path_for_after

                # Если у метки есть указание для скачивания в альтернативном виде,
                # например Label22_StarteamView = DBO:Release_17:VIP:GPB:GPB 017.3 107N
                StarteamView = settings.StarteamView
                try:
                    Label_AltStarteamView = dict(labels_list)[key+key_AltStarteamView]
                    if Label_AltStarteamView is not None:
                        StarteamView = Label_AltStarteamView
                        message += ' from "'+StarteamView+'"'
                except KeyError as e:
                    pass;

                launch_string = quote(settings.stcmd)
                launch_string += ' co -nologo -stop -q -x -o -is -p "{}:{}@{}:{}/{}/{}"'.format(
                                    settings.StarteamLogin,
                                    settings.StarteamPassword,
                                    settings.StarteamServer,
                                    settings.StarteamPort,
                                    settings.StarteamProject,
                                    StarteamView)

                if st_path_to_download:
                    launch_string += '/"{}"'.format(st_path_to_download)
                launch_string += ' -rp ' + quote(outdir)
                if (key == 'datebefore') or (key == 'dateafter'):
                    if label:
                        launch_string += ' -vd ' + quote(label)
                else:
                    if label:
                        launch_string += ' -vl ' + quote(label)
                if st_file_to_download:
                    launch_string += " "+st_file_to_download

                # print(launch_string)
                print(message + '. Please wait...')
                result = subprocess.call(launch_string)
                if result == 0:
                    # print1('FINISHED '+message)
                    total_result += True
                else:
                    print1('ERROR '+message)
                    total_result += False

    except BaseException as e:
        print1('ERROR when downloading from Starteam ({})'.format(e))
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
                print1('copying {}'.format(path))
                makedirs(wheretocopy)
                shutil.copy2(path, wheretocopy)
            else:
                print1('something wrong {} -> {}'.format(path, wheretocopy))

    if dircmp.right_only:
        for file in dircmp.right_only:
            path = os.path.join(after, file)
            if os.path.isfile(path):
                print1('copying {}'.format(path))
                makedirs(wheretocopy)
                shutil.copy2(path, wheretocopy)
            else:
                print1('copying DIR with contents {}'.format(path))
                clean(os.path.join(wheretocopy, file))
                shutil.copytree(path, os.path.join(wheretocopy, file))
# -------------------------------------------------------------------------------------------------


def compare_directories_BEFORE_and_AFTER():
    if os.path.exists(const_dir_BEFORE):
        print('BEGIN compare directories:')
        print1('BEFORE: {}'.format(const_dir_BEFORE))
        print1('AFTER:  {}'.format(const_dir_AFTER))
        __compare_and_copy_dirs_recursively__(const_dir_BEFORE, const_dir_AFTER, const_dir_COMPARED)
    else:
        os.rename(const_dir_AFTER, const_dir_COMPARED)
        print('USING folder "AFTER" as compare result, because "BEFORE" not exists:')
        print1('BEFORE (not exists): {}'.format(const_dir_BEFORE))
        print1('AFTER              : {}'.format(const_dir_AFTER))

    print('\tFINISHED compare directories. LOOK at {}'.format(const_dir_COMPARED))
# -------------------------------------------------------------------------------------------------


def make_upgrade10_eif_string_by_file_name(counter, file_name):
    result = ''
    file_type_match = re.findall('\((?:\d+|data)\)\.eif', file_name, flags=re.IGNORECASE)
    if len(file_type_match):
        structure_type_raw = file_type_match[0]
        structure_type = re.sub(r'\.eif', '', structure_type_raw, flags=re.IGNORECASE).replace('(', '').replace(')', '')
        if structure_type.upper() == 'DATA':
            return ''  # пропускаем data-файлы, за них ответят 10-файлы
        file_name = file_name.replace(structure_type_raw, '')
        if structure_type == '10':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|FALSE|TRUE|FALSE|NULL|NULL|NULL|NULL|NULL|'Таблицы'>"  # TODO здесь все сложно
        elif structure_type == '12':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|TRUE|NULL|NULL|NULL|NULL|NULL|'Визуальные формы'>"
        elif structure_type == '14':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|FALSE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Конфигурации'>"
        elif structure_type == '16':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Автопроцедуры'>"
        elif structure_type == '18':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Профили'>"
        elif structure_type == '19':
            result = "<{}|{}|'{}'|TRUE|FALSE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Роли'>"
        elif structure_type == '20':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Привелегии'>"
        elif structure_type == '21':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Пользователи'>"
        elif structure_type == '30':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|TRUE|NULL|NULL|NULL|NULL|NULL|'Сценарии'>"
        elif structure_type == '65':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'RTS что-то'>"
        elif structure_type == '66':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'RTS Errors params'>"
        elif structure_type == '71':
            result = "<{}|{}|'{}'|TRUE|FALSE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Генераторы'>"
        elif structure_type == '72':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Структуры отображений'>"
        elif structure_type == '73':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Хранимые процедуры'>"
        elif structure_type in ['50', '81']:
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|FALSE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Простые операции'>"
        elif structure_type in ['51', '82']:
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|FALSE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Табличные операции'>"
        elif structure_type in ['52', '83'] :
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|FALSE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Документарные операции'>"
        elif structure_type == '84':
            result = "<{}|{}|'{}'|TRUE|FALSE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Статусы'>"
        else:
            print1('ERROR unknown structure type {} for filename {}'.format(structure_type, file_name))

        return '  '+result.format(counter, structure_type, file_name)+'\n'
    else:
        print1('ERROR can not detect structure type by filename ({})'.format(file_name))
# -------------------------------------------------------------------------------------------------


def download_TABLE10_files_for_DATA_FILES(settings, instance):
    eif_list = list_files(dir_COMPARED_BASE(instance), "*.eif")
    for eif_file in eif_list:
        # проверим соответствует ли название файла формату "*(data).eif"
        file_type_match = re.findall(r'\(data\)\.eif', eif_file, flags=re.IGNORECASE)
        if len(file_type_match):
            eif10_file = str(eif_file).replace(file_type_match[0], '(10).eif')
            # отрежем путь (splitfilename не пашет, если файла нет)
            eif10_file = getLastElementOfPath(eif10_file)
            # и проверим есть ли файл eif10_file в списке файлов eif_list
            exists = [file1 for file1 in eif_list if re.search(re.escape(eif10_file), file1)]
            if not exists:
                # если файла eif10_file в списке загруженных файлов нет, то выгрузим его из стартима
                # сначала пытаемся выгрузить для 17 версии (папка TABLES), если не получается, то для 15 версии )(Table)
                if not download_starteam(settings, None, const_dir_COMPARED, '', 'BASE/'+instance+'/TABLES/', eif10_file):
                    download_starteam(settings, None, const_dir_COMPARED, '', 'BASE/' + instance + '/Table/', eif10_file)
# -------------------------------------------------------------------------------------------------


def generate_upgrade10_eif(instance):
    eif_list = list_files(dir_COMPARED_BASE(instance), '*.eif')
    if len(eif_list) > 0:
        data_dir = dir_PATCH_DATA(instance)
        makedirs(data_dir)
        for eif_file in eif_list:
            try:
                shutil.copy2(eif_file, data_dir)
            except EnvironmentError as e:
                print1('Unable to copy file. %s' % e)

        eif_list = list_files(data_dir, '*.eif')
        if len(eif_list) > 0:
            with open(get_filename_UPGRADE10_eif(instance), mode='w') as f:
                f.writelines(const_UPGRADE10_HEADER)
                counter = 1
                for eif_file in eif_list:
                    eif_file_name = split_filename(eif_file)
                    line = make_upgrade10_eif_string_by_file_name(counter, eif_file_name)
                    if line:
                        f.writelines(line)
                        counter += 1
                f.writelines(const_UPGRADE10_FOOTER)


# -------------------------------------------------------------------------------------------------
def get_version_from_win32_pe(file):
    # http://windowssdk.msdn.microsoft.com/en-us/library/ms646997.aspx
    sig = struct.pack("32s", u"VS_VERSION_INFO".encode("utf-16-le"))
    # This pulls the whole file into memory, so not very feasible for
    # large binaries.
    try:
        filedata = open(file).read()
    except IOError:
        return "Unknown"
    offset = filedata.find(sig)
    if offset == -1:
        return "Unknown"

    filedata = filedata[offset + 32: offset + 32 + (13 * 4)]
    version_struct = struct.unpack("13I", filedata)
    ver_ms, ver_ls = version_struct[4], version_struct[5]
    return "%d.%d.%d.%d" % (ver_ls & 0x0000ffff, (ver_ms & 0xffff0000) >> 16,
                            ver_ms & 0x0000ffff, (ver_ls & 0xffff0000) >> 16)


# -------------------------------------------------------------------------------------------------
def get_binary_platform(fullFilePath):
    IMAGE_FILE_MACHINE_I386=332
    IMAGE_FILE_MACHINE_IA64=512
    IMAGE_FILE_MACHINE_AMD64=34404

    try:
        with open(fullFilePath, 'rb') as f:
            s=f.read(2).decode(encoding="utf-8", errors="strict")
            if s!="MZ":
                return None
                # print("Not an EXE file")
            else:
                f.seek(60)
                s=f.read(4)
                header_offset=struct.unpack("<L", s)[0]
                f.seek(header_offset+4)
                s=f.read(2)
                machine=struct.unpack("<H", s)[0]

                if machine==IMAGE_FILE_MACHINE_I386:
                    return "Win32"
                    #print("IA-32 (32-bit x86)")
                elif machine==IMAGE_FILE_MACHINE_IA64:
                    return "Win64"
                    #print("IA-64 (Itanium)")
                elif machine==IMAGE_FILE_MACHINE_AMD64:
                    return "Win64"
                    #print("AMD64 (64-bit x86)")
                else:
                    return "Unknown"
                    #print("Unknown architecture")
    except BaseException:
        return None


# -------------------------------------------------------------------------------------------------
def __get_exe_file_info__(fullFilePath):
    # http://windowssdk.msdn.microsoft.com/en-us/library/ms646997.aspx
    sig = struct.pack("32s", u"VS_VERSION_INFO".encode("utf-16-le"))
    # This pulls the whole file into memory, so not very feasible for
    # large binaries.
    try:
        with open(fullFilePath, 'rb') as f:
            filedata = f.read()
    except BaseException:
        return None
    offset = filedata.find(sig)
    if offset == -1:
        return None

    filedata = filedata[offset + 32: offset + 32 + (13*4)]
    version_struct = struct.unpack("13I", filedata)
    ver_ms, ver_ls = version_struct[4], version_struct[5]
    return "%d.%d.%d.%d" % (ver_ls & 0x0000ffff, (ver_ms & 0xffff0000) >> 16,
                            ver_ms & 0x0000ffff, (ver_ls & 0xffff0000) >> 16)
# -------------------------------------------------------------------------------------------------


def get_build_version(build_path):
    result = 'unknown'
    try:
        if os.path.exists(build_path):
            files = list_files(build_path, 'cbank.exe')
            files += list_files(build_path, 'BRHelper.exe')
            files += list_files(build_path, 'cryptlib2x.dll')
            files += list_files(build_path, 'npBSSPlugin.dll')
            files += list_files(build_path, 'CryptLib.dll')
            for f in files:
                ver = None
                try:
                    ver = __get_exe_file_info__(f)
                except FileNotFoundError:
                    pass
                if ver is not None:
                    result = ver
                    break

    except BaseException as e:
        print1('ERROR: can not detect version of build ({})'.format(e))
        raise e
    return result


# -------------------------------------------------------------------------------------------------
def open_encoding_aware(path):
    encodings = ['windows-1251', 'utf-8']
    for e in encodings:
        try:
            fh = open(path, 'r', encoding=e)
            fh.readlines()
            fh.seek(0)
        except ValueError as err:
            pass
            #print1('Got error "{}" with {} , trying different encoding ({} was used)'.format(err, path, e))
        else:
            #print1('opening the file {} with encoding:  {}'.format(path, e))
            return fh
    return None


# -------------------------------------------------------------------------------------------------
def bls_get_uses_graph(path):
    def __replace_unwanted_symbols__(pattern, string):
        find_all = re.findall(pattern, string, flags=re.MULTILINE)
        for find_here in find_all:
            string = string.replace(find_here, '')
        return string

    bls_uses_graph = {}
    files = list_files(path, '*.bls')
    for file_name in files:
        with open_encoding_aware(file_name) as f:
            if f:
                text = f.read()
                # удаляем комментарии, которые располагаются между фигурными скобками "{ .. }"
                text = __replace_unwanted_symbols__(r'{[\S\s]*?}', text)
                # удаляем комментарии, которые располагаются между скобками "(* .. *)"
                text = __replace_unwanted_symbols__(r'\(\*[\S\s]*?\*\)', text)
                # удаляем однострочные комментарии, которые начинаются на "//"
                text = __replace_unwanted_symbols__(r'//.*', text)
                # находим текст между словом "uses" и ближайшей точкой с запятой
                list_of_uses = re.findall(r'(?<=\buses\s)(?s)(.*?)(?=;)', text, flags=re.IGNORECASE|re.MULTILINE)

                file_name_without_path = split_filename(file_name).lower()
                # добавляем пустой элемент для файла "file_name", на случай, если файл не имеет uses
                bls_uses_graph.update({file_name_without_path: [file_name, []]})

                if len(list_of_uses):
                    for text_of_uses in list_of_uses:
                        # разбиваем найденный текст на части между запятыми
                        uses_list = [line.strip()+'.bls' for line in text_of_uses.split(',') if line.strip()]
                        if uses_list:
                            # проверим, что такой файл еще не был обработан

                            item_already_in_list = bls_uses_graph.get(file_name_without_path)
                            # если элемент с названием "file_name_without_path" уже есть в списке bls_uses_graph
                            if item_already_in_list:
                                # то дополним его [список_зависимостей] списком "uses_list"
                                item_already_in_list[1].extend(uses_list)
                            else:
                                # TODO: ЭТА ВЕТКА НЕ НУЖНА, НАДО УДАЛИТЬ (ВЫШЕ УЖЕ ДОБАВЛЯЮ ПУСТОЙ ЭЛЕМЕНТ)
                                # если файла нет в списке зависимостей,
                                # то добавим "{название_файла: [полное_название_с_путем, [список_зависимостей]]}"
                                bls_uses_graph.update({file_name_without_path: [file_name, uses_list]})
    return bls_uses_graph


# -------------------------------------------------------------------------------------------------
def __BlsCompile__(BuildPath, BlsFileName, BlsPath, UsesList, LicServer, LicProfile):
    # print(BlsPath)
    # проверим, есть ли компилятор
    bscc_path = os.path.join(BuildPath, 'bscc.exe')
    if not os.path.exists(bscc_path):
        # компилятора нет, ошибка
        raise FileNotFoundError('Compiler {} not found'.format(bscc_path))
    run_str = bscc_path+' {} -M0 -O0 -S{} -A{}'.format(BlsPath, LicServer, LicProfile)
    '''
    subprocess.call(run_str)
    return True
    '''
    process = subprocess.Popen(run_str, shell=False, stdout=subprocess.PIPE)  # , stderr=subprocess.PIPE
    out, err = process.communicate()
    process.stdout.close()
    str_res = '\n\t\t\t'+out.decode('windows-1251').replace('\n', '\n\t\t\t')
    # succesfully с ошибкой. так и должно быть
    if 'Compiled succesfully' not in str_res and \
       'Compiled with warnings' not in str_res:
        print1('ERROR: File "{}", Uses list "{}"{}'.format(BlsFileName, UsesList, str_res))
        print1('COMPILATION continues. Please wait...')
        return False
    else:
        # print1('Compiled "{}"'.format(bls_file_name))
        return True


# -------------------------------------------------------------------------------------------------
def __BlsCompileAll__(LicServer, LicProfile, BuildPath, BlsUsesGraph, BlsFileName, ObservedList, SuccessList):
    BlsFileName = BlsFileName.lower()
    if BlsFileName not in ObservedList:  # если файл отсутствует в списке обработанных
        BlsItemInfo = BlsUsesGraph.get(BlsFileName)
        #print(BlsItemInfo)
        if BlsItemInfo:
            UsesList = BlsItemInfo[1]
            BlsFilePath = BlsItemInfo[0]
            if len(UsesList):  # если файл зависит от других файлов, то проведем
                for UsesFileName in UsesList:  # компиляцию каждого файла
                    __BlsCompileAll__(LicServer, LicProfile, BuildPath, BlsUsesGraph, UsesFileName, ObservedList, SuccessList)
            # добавляем в список учтенных файлов
            ObservedList.append(BlsFileName)
            if __BlsCompile__(BuildPath, BlsFileName, BlsFilePath, UsesList, LicServer, LicProfile):
                # компилируем и добавляем в список успешно откомпилированных
                SuccessList.append(BlsFileName)
                printProgress(len(SuccessList), len(BlsUsesGraph), decimals=0, barLength=20)
        else:
            print1('No information about file to compile "{}". Probably not all SOURCE were downloaded.'.format(BlsFileName))


# -------------------------------------------------------------------------------------------------
def BlsCompileAll(lic_server, lic_profile, build_path, source_path):
    clean(build_path, ['*.bls', '*.bll'])  # очищаем каталог билда от bls и bll
    print('BEGIN BLS COMPILATION. Please wait...')
    copyfiles(source_path, build_path, ['*.bls'], [])   # копируем в каталог билда все bls
    bls_uses_graph = bls_get_uses_graph(build_path)     # строим граф зависимостей по строкам uses
    observed_list = []
    compiled_successfully = []
    try:
        for bls_file_name in bls_uses_graph:                # компилируем все bls
            __BlsCompileAll__(lic_server, lic_profile, build_path, bls_uses_graph,
                                bls_file_name, observed_list, compiled_successfully)
        print1("COMPILED {} of {}".format(len(compiled_successfully), len(bls_uses_graph)))
        return True
    except FileNotFoundError as e:
        print1('ERROR: {}'.format(e))
        return False


# -------------------------------------------------------------------------------------------------
def __extract_build__(build_path):
    build_zip_file = split_filename(build_path)
    if '.zip' in build_zip_file.lower():
        build_tmp_dir = os.path.join(tempfile.gettempdir(), build_zip_file)
        clean(build_tmp_dir)
        print('EXTRACTING BUILD "{}" in "{}"'.format(build_path, build_tmp_dir))
        try:
            with zipfile.ZipFile(build_path) as z:
                z.extractall(os.path.join(tempfile.gettempdir(), build_zip_file))
                # запомним путь во временный каталог в качестве
                # нового пути к билду для последующего применения
                build_path = build_tmp_dir
        except BaseException as e:
            print1('ERROR EXTRACTING BUILD "{}"'.format(e))
        # конец разархивации
    return build_path


# -------------------------------------------------------------------------------------------------
def __copy_build__(build_path, build_path_crypto, dest_path):
    # проверка наличия пути build_path
    if not build_path:
        return
    if not os.path.exists(build_path):
        print1('PATH {} does not exists'.format(build_path))
        return
    # если ссылка на билд указывает не на каталог, а на файл архива
    # попробуем провести разархивацию во временный каталог
    build_path = __extract_build__(build_path)
    if build_path_crypto:
        build_path_crypto = __extract_build__(build_path_crypto)
    # определяем версию билда
    version = get_build_version(build_path)
    if ('20.1' in version) or ('20.2' in version):
        for release in ['32', '64']:
            win_rel = 'Win{}\\Release'.format(release)
            src = os.path.join(build_path, win_rel)
            dst = os.path.join(dest_path, win_rel)
            clean(dst)
            print('COPYING BUILD {} from "{}" in "{}"'.format(version, src, dst))
            copyfiles(src, dst, ['*.exe', '*.ex', '*.bpl', '*.dll'], [])
            if build_path_crypto:
                src = os.path.join(build_path_crypto, win_rel)
                print('COPYING CRYPTO BUILD {} from "{}" in "{}"'.format(version, src, dst))
                copyfiles(src, dst, ['CryptLib.dll', 'cr_*.dll'], [])
    else:
        clean(dest_path)
        print('COPYING BUILD {} from "{}" in "{}"'.format(version, build_path, dest_path))
        copyfiles(build_path, dest_path, ['*.exe', '*.ex', '*.bpl', '*.dll'], [])
        if build_path_crypto:
            print('COPYING CRYPTO BUILD {} from "{}" in "{}"'.format(version, build_path, dest_path))
            copyfiles(build_path_crypto, dest_path, ['CryptLib.dll', 'cr_*.dll'], [])
    return version


# -------------------------------------------------------------------------------------------------
def download_build(settings):
    build = settings.BuildBK
    buildIC = settings.BuildIC
    buildCrypto = settings.BuildCrypto

    instances = []
    if build:
        instances.append(const_instance_BANK)
        instances.append(const_instance_CLIENT)
        instances.append(const_instance_CLIENT_MBA)
        build_version = __copy_build__(build, buildCrypto, const_dir_TEMP_BUILD_BK)
    if buildIC:
        instances.append(const_instance_IC)
        buildIC_version = __copy_build__(buildIC, buildCrypto, const_dir_TEMP_BUILD_IC)

    if not len(instances):
        return False

    for instance in instances:
        if instance in [const_instance_BANK, const_instance_CLIENT, const_instance_CLIENT_MBA]:
            is20 = ('20.1' in build_version) or ('20.2' in build_version)
            if is20 and instance == const_instance_BANK:
                build_path = os.path.join(const_dir_TEMP_BUILD_BK, 'Win32\\Release')
                # это копируются все файлы, которые будут участвовать в компиляции BLS на следующем шаге
                # т.к. в результате __copy_build__ весь билд оказывается разделен на Win32 и Win64
                copyfiles(build_path, const_dir_TEMP_BUILD_BK, ['*.*'], [])
        else:
            is20 = ('20.1' in buildIC_version) or ('20.2' in buildIC_version)

        #  Если в настройках включено копирование билда в патч
        if settings.PlaceBuildIntoPatch:
            print('COPYING build into patch for {}'.format(instance))
            if instance == const_instance_BANK:
                excluded_files = const_excluded_build_for_BANK
            elif instance == const_instance_IC:
                excluded_files = const_excluded_build_for_BANK
            elif instance in [const_instance_CLIENT, const_instance_CLIENT_MBA]:
                excluded_files = const_excluded_build_for_CLIENT
            if is20:  # для билда 20-ой версии
                if instance == const_instance_IC:  # выкладываем билд плагина для ИК
                    build_path_bank = os.path.join(const_dir_TEMP_BUILD_BK, 'Win32\\Release')  # подготовим путь к билду банка
                    mask = ['bssetup.msi', 'CalcCRC.exe']
                    copyfiles(build_path_bank, dir_PATCH_LIBFILES_INETTEMP(), mask, [])
                    mask = ['BssPluginSetup.exe', 'BssPluginWebKitSetup.exe', 'BssPluginWebKitSetup.exe']
                    copyfiles(build_path_bank, dir_PATCH_LIBFILES_INETTEMP(), mask, [])

                    for release in ['32', '64']:  # выкладываем билд в LIBFILES32(64).BNK
                        copyfiles(build_path_bank, dir_PATCH_LIBFILES_BNK(release), ['UpdateIc.exe'], [])
                        copyfiles(build_path_bank, dir_PATCH_LIBFILES_BNK_WWW_EXE(release), ['bsiset.exe'], [])
                        mask = ['bsi.dll', 'bsi.jar']
                        copyfiles(build_path_bank, dir_PATCH_LIBFILES_BNK_WWW_BSIscripts_RTIc(release), mask, [])
                        copyfiles(build_path_bank, dir_PATCH_LIBFILES_BNK_WWW_BSIscripts_RTWa(release), mask, [])

                        build_path = os.path.join(const_dir_TEMP_BUILD_IC, 'Win{}\\Release'.format(release))
                        mask = ['BssPluginSetup.exe', 'BssPluginWebKitSetup.exe', 'BssPluginSetup64.exe']
                        for subversion in ['64', '32']:  # subversion - чтобы перекрестно положить файлы 32 бита в каталог 64, и наоборот
                            copyfiles(build_path, dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTIc_CODE_BuildVersion(buildIC_version, release), mask, [])
                            copyfiles(build_path, dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTWa_CODE_BuildVersion(buildIC_version, release), mask, [])

                else:
                    if instance == const_instance_BANK:
                        build_path = os.path.join(const_dir_TEMP_BUILD_BK, 'Win32\\Release')
                        # это копируются все файлы, которые будут участвовать в компиляции BLS на следующем шаге
                        # т.к. в результате __copy_build__ весь билд оказывается разделен на Win32 и Win64
                        copyfiles(build_path, const_dir_TEMP_BUILD_BK, ['*.*'], [])
                        copyfiles(build_path, dir_PATCH(), ['CBStart.exe'], [])  # один файл CBStart.exe в корень патча
                    for release in ['32', '64']:  # выкладываем остальной билд для Б и БК для версий 32 и 64
                        build_path = os.path.join(const_dir_TEMP_BUILD_BK, 'Win{}\\Release'.format(release))
                        mask = ['*.exe', '*.ex', '*.bpl']
                        copyfiles(build_path, dir_PATCH_LIBFILES_EXE(instance, release), mask, excluded_files)
                        copyfiles(build_path, dir_PATCH_LIBFILES_SYSTEM(instance, release), ['*.dll'], excluded_files)
                        copyfiles(build_path, dir_PATCH_CBSTART(instance, release), ['CBStart.exe'], [])
                        if instance == const_instance_BANK:
                            # заполняем TEMPLATE шаблон клиента в банковском патче
                            mask = ['*.exe', '*.ex', '*.bpl']
                            copyfiles(build_path, dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX_CLIENT_EXE(release), mask, const_excluded_build_for_CLIENT)
                            copyfiles(build_path, dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX_CLIENT_SYSTEM(release), ['*.dll'], const_excluded_build_for_CLIENT)
                            mask = ['CalcCRC.exe', 'Setup.exe', 'Install.exe', 'eif2base.exe', 'ilKern.dll', 'GetIName.dll']
                            copyfiles(build_path, dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX(release), mask, [])
                            mask = ['ilGroup.dll', 'iliGroup.dll', 'ilProt.dll']
                            copyfiles(build_path, dir_PATCH_LIBFILES_TEMPLATE_LANGUAGEX_EN(release), mask, [])
                            copyfiles(build_path, dir_PATCH_LIBFILES_TEMPLATE_LANGUAGEX_RU(release), mask, [])

            else:  # для билдов 15 и 17
                if instance in [const_instance_BANK, const_instance_CLIENT, const_instance_CLIENT_MBA]:
                    # выкладываем билд для Б и БК
                    build_path = const_dir_TEMP_BUILD_BK
                    mask = ['*.exe', '*.ex', '*.bpl']  # todo bpl-ки в SYSTEM или в EXE?
                    copyfiles(build_path, dir_PATCH_LIBFILES_EXE(instance), mask, excluded_files)
                    if settings.ClientEverythingInEXE and instance == const_instance_CLIENT:
                        copyfiles(build_path, dir_PATCH_LIBFILES_EXE(instance), ['*.dll'], excluded_files)
                    else:
                        copyfiles(build_path, dir_PATCH_LIBFILES_SYSTEM(instance), ['*.dll'], excluded_files)

                if instance == const_instance_BANK:
                    copyfiles(build_path, dir_PATCH(), ['CBStart.exe'], [])  # один файл в корень
                    # заполняем билдом TEMPLATE шаблон клиента в банковском патче
                    mask = ['*.exe', '*.ex', '*.bpl']
                    copyfiles(build_path, dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_EXE(), mask, const_excluded_build_for_CLIENT)
                    if settings.ClientEverythingInEXE:
                        copyfiles(build_path, dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_EXE(), ['*.dll'], const_excluded_build_for_CLIENT)
                    else:
                        copyfiles(build_path, dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_SYSTEM(), ['*.dll'], const_excluded_build_for_CLIENT)
                    mask = ['CalcCRC.exe', 'Setup.exe', 'Install.exe', 'eif2base.exe', 'ilKern.dll', 'GetIName.dll']
                    copyfiles(build_path, dir_PATCH_LIBFILES_TEMPLATE_DISTRIB(), mask, [])
                    mask = ['ilGroup.dll', 'iliGroup.dll', 'ilProt.dll']
                    copyfiles(build_path, dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_EN(), mask, [])
                    copyfiles(build_path, dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_RU(), mask, [])
                    copyfiles(build_path, dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_EN_CLIENT_SYSTEM(), mask, [])
                    copyfiles(build_path, dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_RU_CLIENT_SYSTEM(), mask, [])
                    # заполняем LIBFILES.BNK в банковском патче билдом для БК
                    mask = ['autoupgr.exe', 'bscc.exe', 'compiler.exe', 'operedit.exe', 'testconn.exe', 'treeedit.exe']
                    copyfiles(build_path, dir_PATCH_LIBFILES_BNK_ADD(), mask, [])
                    copyfiles(build_path, dir_PATCH_LIBFILES_BNK_BSISET_EXE(), ['bsiset.exe'], [])
                    copyfiles(build_path, dir_PATCH_LIBFILES_BNK_LICENSE_EXE(), ['protcore.exe'], [])

                if instance == const_instance_IC:
                    # заполняем LIBFILES.BNK в банковском патче билдом для ИК
                    build_path = const_dir_TEMP_BUILD_IC
                    mask = ['bssaxset.exe', 'inetcfg.exe', 'rts.exe', 'rtsconst.exe', 'rtsinfo.exe']
                    copyfiles(build_path, dir_PATCH_LIBFILES_BNK_RTS_EXE(), mask, [])
                    mask = ['llComDat.dll', 'llrtscfg.dll', 'llxmlman.dll', 'msxml2.bpl']
                    copyfiles(build_path, dir_PATCH_LIBFILES_BNK_RTS_SYSTEM(), mask, [])
                    copyfiles(build_path, dir_PATCH_LIBFILES_BNK_WWW_BSIscripts_RTIc(), ['bsi.dll'], [])
                    copyfiles(build_path, dir_PATCH_LIBFILES_BNK_WWW_BSIscripts_RTAdmin(), ['bsi.dll'], [])
                    # todo INETTEMP
    return True


# -------------------------------------------------------------------------------------------------
def copy_bls():
    bls_version = '15'
    if os.path.exists(const_dir_COMPARED_BLS):
        source_dir = const_dir_COMPARED_BLS
        dest_dir = dir_PATCH_LIBFILES_SOURCE
        if os.path.exists(const_dir_COMPARED_BLS_SOURCE):
            # если такой путь существует, значит BLS выложены как для 17/20 версии
            source_dir = const_dir_COMPARED_BLS_SOURCE
            dest_dir = os.path.join(dest_dir,'BLS')
            bls_version = '17/20'
        clean(dest_dir)
        print('COPYING BLS ("{}" version style) from "{}" to {}'.format(bls_version, source_dir, dest_dir))
        try:
            shutil.copytree(source_dir, dest_dir)
        except BaseException as e:
            print1('ERROR when copying ({})'.format(e))
        return True
    else:
        print('NOT COPYING BLS. Path {} not exists'.format(const_dir_COMPARED_BLS))
        return False


# -------------------------------------------------------------------------------------------------
def copy_bll(client_everything_in_exe):
    print('COPYING BLL files to patch')
    bll_files_only_bank = list_files_remove_paths_and_change_extension(const_dir_COMPARED, '.bll', ['?b*.bls', 'RT_*.bls'])
    bll_files_only_mba = list_files_remove_paths_and_change_extension(const_dir_COMPARED_BLS_SOURCE_RCK, '.bll', ['*.bls'])
    bll_files_all = list_files_remove_paths_and_change_extension(const_dir_COMPARED, '.bll', ['*.bls'])
    bll_files_tmp = list_files_by_list(const_dir_TEMP_BUILD_BK, bll_files_all)
    if len(bll_files_tmp) != len(bll_files_all):
        print1('ERROR: Not all changed BLS files were compiled {}'.format(list(set(bll_files_all) - set(bll_files_tmp))))
        return False

    bll_files_client_mba = list(set(bll_files_all) - set(bll_files_only_bank))
    bll_files_client = list(set(bll_files_client_mba) - set(bll_files_only_mba))

    # копируем bll для банка по списку bll_files_all
    copyfiles(const_dir_TEMP_BUILD_BK, dir_PATCH_LIBFILES_USER(const_instance_BANK), bll_files_all, [])

    # копируем bll для клиента по разнице списков  bll_files_all-bll_files_only_bank
    if client_everything_in_exe:
        copyfiles(const_dir_TEMP_BUILD_BK, dir_PATCH_LIBFILES_EXE(const_instance_CLIENT), bll_files_client, [])
        copyfiles(const_dir_TEMP_BUILD_BK, dir_PATCH_LIBFILES_EXE(const_instance_CLIENT_MBA), bll_files_client_mba, [])
        copyfiles(const_dir_TEMP_BUILD_BK, dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_EXE(), bll_files_client, [])
    else:
        copyfiles(const_dir_TEMP_BUILD_BK, dir_PATCH_LIBFILES_USER(const_instance_CLIENT), bll_files_client, [])
        copyfiles(const_dir_TEMP_BUILD_BK, dir_PATCH_LIBFILES_USER(const_instance_CLIENT_MBA), bll_files_client_mba, [])
        copyfiles(const_dir_TEMP_BUILD_BK, dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_USER(), bll_files_client, [])
    return True


# -------------------------------------------------------------------------------------------------
def download_mba_dll(settings):
    if download_starteam(settings, None, const_dir_TEMP_BUILD_BK, '', 'DLL/', '*.dll'):
        copyfiles_of_version(os.path.join(const_dir_TEMP_BUILD_BK, 'DLL'), const_dir_TEMP_BUILD_BK, 'Win32', ['*.dll'], [])
        return True


# -------------------------------------------------------------------------------------------------
def main():
    global_settings = read_config()
    if global_settings is None:
        return
    if not clean(const_dir_TEMP):
        return
    # clean(const_dir_PATCH)
    global_settings.StarteamPassword = getpassword('ENTER StarTeam password for {}:'.format(global_settings.StarteamLogin))
    print('BEGIN ----------------')
    if download_starteam(global_settings, global_settings.Labels, const_dir_AFTER, const_dir_BEFORE):
        compare_directories_BEFORE_and_AFTER()
        for instance in [const_instance_BANK, const_instance_CLIENT, const_instance_CLIENT_MBA]:
            download_TABLE10_files_for_DATA_FILES(global_settings, instance)
            generate_upgrade10_eif(instance)
        ShouldCompileBLS = copy_bls()
        if download_build(global_settings):  # если завершена загрузка билда
            # загрузим дополнительный билд (если есть)
            if ShouldCompileBLS:
                download_mba_dll(global_settings)
                # загрузим все исходники текущей ревизии
                if download_starteam(global_settings, None, const_dir_TEMP_TEMPSOURCE, '', 'BLS/', '*.bls'):
                    # загрузим поверх ревизии исходников, помеченные метками
                    if download_starteam(global_settings, global_settings.Labels, const_dir_TEMP_TEMPSOURCE, '', 'BLS/', '*.bls'):
                        # запустим компиляцию этой каши
                        if BlsCompileAll(global_settings.LicenseServer, global_settings.LicenseProfile, const_dir_TEMP_BUILD_BK, const_dir_TEMP_TEMPSOURCE):
                            # копируем готовые BLL в патч
                            copy_bll(global_settings.ClientEverythingInEXE)
    print('DONE -----------------')


# -------------------------------------------------------------------------------------------------
def main_debug_without_clean():
    global_settings = read_config()
    if global_settings is None:
        return
    # if not clean(const_dir_TEMP):
    #    return
    # clean(const_dir_PATCH)
    #global_settings.StarteamPassword = getpassword('ENTER StarTeam password for {}:'.format(global_settings.StarteamLogin))
    print('BEGIN')
    '''
    if download_starteam(global_settings, global_settings.Labels, const_dir_AFTER, const_dir_BEFORE):
        compare_directories_BEFORE_and_AFTER()
        download_TABLE10_files_for_DATA_FILES(global_settings, const_instance_BANK)
        download_TABLE10_files_for_DATA_FILES(global_settings, const_instance_CLIENT)
        generate_upgrade10_eif(const_instance_BANK)
        generate_upgrade10_eif(const_instance_CLIENT)
    '''
    '''
    if download_build(global_settings):  # если завершена загрузка билда
        # загрузим дополнительный билд
        download_starteam(global_settings, None, const_dir_TEMP_BUILD_BK, '', 'DLL/', '*.dll')
        # загрузим все исходники текущей ревизии
        if download_starteam(global_settings, None, const_dir_TEMP_TEMPSOURCE, '', 'BLS/', '*.bls'):
            # загрузим поверх ревизии исходников, помеченные метками
            if download_starteam(global_settings, global_settings.Labels, const_dir_TEMP_TEMPSOURCE, '', 'BLS/', '*.bls'):
                # запустим компиляцию этой каши
                pass
    '''
    if BlsCompileAll(global_settings.LicenseServer, global_settings.LicenseProfile, const_dir_TEMP_BUILD_BK, const_dir_TEMP_TEMPSOURCE):
      # копируем готовые BLL в патч
      copy_bll(global_settings.ClientEverythingInEXE)
    print('DONE!!!\a')


#main_debug_without_clean()
#bls_get_uses_graph('D:\\tokill')
main()
#generate_upgrade10_eif(const_instance_CLIENT_MBA)






