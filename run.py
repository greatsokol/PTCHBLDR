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
import time
import datetime


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
const_dir_COMPARED_WWW = os.path.join(const_dir_COMPARED, 'WWW')
const_dir_COMPARED_RT_TPL = os.path.join(const_dir_COMPARED, 'RT_TPL')
const_dir_COMPARED_RTF = os.path.join(const_dir_COMPARED, 'RTF')
const_dir_COMPARED_RTF_BANK = os.path.join(const_dir_COMPARED_RTF, 'Bank')
const_dir_COMPARED_RTF_CLIENT = os.path.join(const_dir_COMPARED_RTF, 'Client')
const_dir_COMPARED_RTF_REPJET = os.path.join(const_dir_COMPARED_RTF, 'RepJet')

const_dir_PATCH = os.path.join(const_dir_TEMP, 'PATCH')

dir_COMPARED_BASE = lambda instance: os.path.join(os.path.join(const_dir_COMPARED, 'BASE'), instance)
dir_PATCH = lambda instance='': os.path.join(const_dir_PATCH, instance)
dir_PATCH_DATA = lambda instance: os.path.join(dir_PATCH(instance), 'DATA')
dir_PATCH_CBSTART = lambda instance, version='': os.path.join(dir_PATCH(instance), 'CBSTART{}'.format(version))
dir_PATCH_LIBFILES = lambda instance, version='': os.path.join(dir_PATCH(instance), 'LIBFILES{}'.format(version))
dir_PATCH_LIBFILES_USER = lambda instance: os.path.join(dir_PATCH_LIBFILES(instance), 'USER')
dir_PATCH_LIBFILES_SOURCE = os.path.join(dir_PATCH_LIBFILES(const_instance_BANK), 'SOURCE')

dir_PATCH_LIBFILES_BNK = lambda version='': os.path.join(dir_PATCH(const_instance_BANK),
                                                         'LIBFILES{}.BNK'.format(version))
dir_PATCH_LIBFILES_BNK_ADD = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK(version), 'add')
dir_PATCH_LIBFILES_BNK_BSISET_EXE = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK(version), 'bsiset', 'EXE')
dir_PATCH_LIBFILES_BNK_LICENSE_EXE = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK(version), 'license', 'EXE')
dir_PATCH_LIBFILES_BNK_RTS = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK(version), 'rts')
dir_PATCH_LIBFILES_BNK_RTS_EXE = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_RTS(version), 'EXE')
dir_PATCH_LIBFILES_BNK_RTS_USER = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_RTS(version), 'USER')
dir_PATCH_LIBFILES_BNK_RTS_SYSTEM = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_RTS(version), 'SYSTEM')
dir_PATCH_LIBFILES_BNK_RTS_SUBSYS = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_RTS(version), 'SUBSYS')
dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_TEMPLATE = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_RTS_SUBSYS(version),
                                                                             'TEMPLATE')
dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_RTS_SUBSYS(version),
                                                                             'INSTCLNT')
dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE = lambda version='': os.path.join(
    dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT(version), 'TEMPLATE')
dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB = lambda version='': os.path.join(
    dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE(version), 'DISTRIB')
dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT = lambda version='': os.path.join(
    dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB(version), 'CLIENT')
dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT_SUBSYS = lambda version='': os.path.join(
    dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT(version), 'SUBSYS')
dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT = lambda version='': os.path.join(
    dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT_SUBSYS(version), 'PRINT')
dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT_RTF = lambda version='': os.path.join(
    dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT(version), 'RTF')
dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT_RepJet = lambda \
        version='': os.path.join(
    dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT(version),
    'RepJet')

dir_PATCH_LIBFILES_BNK_WWW = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK(version), 'WWW')
dir_PATCH_LIBFILES_BNK_WWW_EXE = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW(version), 'EXE')
dir_PATCH_LIBFILES_BNK_WWW_BSIscripts = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW(version),
                                                                        'BSI_scripts')
dir_PATCH_LIBFILES_BNK_WWW_BSIscripts_RTIc = lambda version='': os.path.join(
    dir_PATCH_LIBFILES_BNK_WWW_BSIscripts(version), 'rt_ic')
dir_PATCH_LIBFILES_BNK_WWW_BSIscripts_RTAdmin = lambda version='': os.path.join(
    dir_PATCH_LIBFILES_BNK_WWW_BSIscripts(version), 'rt_Admin')
dir_PATCH_LIBFILES_BNK_WWW_BSIscripts_RTWa = lambda version='': os.path.join(
    dir_PATCH_LIBFILES_BNK_WWW_BSIscripts(version), 'rt_wa')
dir_PATCH_LIBFILES_BNK_WWW_BSIsites = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW(version), 'BSI_sites')
dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTIc = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW_BSIsites(version),
                                                                           'rt_ic')
dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTWa = lambda version='': os.path.join(dir_PATCH_LIBFILES_BNK_WWW_BSIsites(version),
                                                                           'rt_wa')
dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTIc_CODE = lambda version='': os.path.join(
    dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTIc(version), 'CODE')
dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTWa_CODE = lambda version='': os.path.join(
    dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTWa(version), 'CODE')

dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTIc_CODE_BuildVersion = lambda build_version, version='': os.path.join(
    dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTIc_CODE(version), build_version)
dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTWa_CODE_BuildVersion = lambda build_version, version='': os.path.join(
    dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTWa_CODE(version), build_version)

dir_PATCH_LIBFILES_EXE = lambda instance, version='': os.path.join(dir_PATCH_LIBFILES(instance, version), 'EXE')
dir_PATCH_LIBFILES_SYSTEM = lambda instance, version='': os.path.join(dir_PATCH_LIBFILES(instance, version), 'SYSTEM')
dir_PATCH_LIBFILES_SUBSYS = lambda instance, version='': os.path.join(dir_PATCH_LIBFILES(instance, version), 'SUBSYS')
dir_PATCH_LIBFILES_SUBSYS_TEMPLATE = lambda: os.path.join(dir_PATCH_LIBFILES_SUBSYS(const_instance_BANK, ''),
                                                          'TEMPLATE')
dir_PATCH_LIBFILES_SUBSYS_PRINT = lambda instance, version='': os.path.join(
    dir_PATCH_LIBFILES_SUBSYS(instance, version), 'PRINT')
dir_PATCH_LIBFILES_SUBSYS_PRINT_RTF = lambda instance, version='': os.path.join(
    dir_PATCH_LIBFILES_SUBSYS_PRINT(instance, version), 'RTF')
dir_PATCH_LIBFILES_SUBSYS_PRINT_REPJET = lambda instance, version='': os.path.join(
    dir_PATCH_LIBFILES_SUBSYS_PRINT(instance, version), 'RepJet')
dir_PATCH_LIBFILES_INSTCLNT = lambda: os.path.join(dir_PATCH_LIBFILES_SUBSYS(const_instance_BANK), 'INSTCLNT')
dir_PATCH_LIBFILES_INETTEMP = lambda: os.path.join(dir_PATCH_LIBFILES_INSTCLNT(), 'INETTEMP')
dir_PATCH_LIBFILES_TEMPLATE = lambda: os.path.join(dir_PATCH_LIBFILES_INSTCLNT(), 'TEMPLATE')

dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX = lambda version: os.path.join(dir_PATCH_LIBFILES_TEMPLATE(),
                                                                    'DISTRIB.X{}'.format(version))
dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX_CLIENT = lambda version: os.path.join(
    dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX(version), 'CLIENT')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX_CLIENT_EXE = lambda version: os.path.join(
    dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX_CLIENT(version), 'EXE')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX_CLIENT_SYSTEM = lambda version: os.path.join(
    dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX_CLIENT(version), 'SYSTEM')
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGEX = lambda version: os.path.join(dir_PATCH_LIBFILES_TEMPLATE(),
                                                                     'Language.X{}'.format(version))
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGEX_EN = lambda version: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_LANGUAGEX(version),
                                                                        'ENGLISH')
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGEX_RU = lambda version: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_LANGUAGEX(version),
                                                                        'RUSSIAN')

dir_PATCH_LIBFILES_TEMPLATE_DISTRIB = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE(), 'DISTRIB')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_DISTRIB(), 'CLIENT')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_EXE = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT(),
                                                                      'EXE')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_SYSTEM = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT(),
                                                                         'SYSTEM')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_SUBSYS = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT(),
                                                                         'SUBSYS')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT = lambda: os.path.join(
    dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_SUBSYS(), 'PRINT')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT_RTF = lambda: os.path.join(
    dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT(), 'RTF')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT_RepJet = lambda: os.path.join(
    dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT(), 'RepJet')
dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_USER = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT(),
                                                                       'USER')
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE(), 'Language')
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_EN = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE(), 'ENGLISH')
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_RU = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE(), 'RUSSIAN')
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_EN_CLIENT_SYSTEM = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE(),
                                                                             'ENGLISH', 'CLIENT', 'SYSTEM')
dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_RU_CLIENT_SYSTEM = lambda: os.path.join(dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE(),
                                                                             'RUSSIAN', 'CLIENT', 'SYSTEM')

get_filename_UPGRADE10_eif = lambda instance: os.path.join(dir_PATCH(instance), 'Upgrade(10).eif')


def log(message_text):
    log_file_name = os.path.join(os.path.abspath(''), 'log.txt')
    with open(log_file_name, mode='a') as f:
        print(message_text)
        f.writelines('\n' + message_text)


def get_last_element_of_path(path):
    result = ''
    path = os.path.normpath(path)
    names = path.split(os.path.sep)
    if len(names):
        result = names[len(names) - 1]
    return result


def split_filename(path):
    result = ''
    if os.path.isfile(path):
        result = get_last_element_of_path(path)
    return result


def split_lastdirname(path):
    result = ''
    if os.path.isdir(path):
        result = get_last_element_of_path(path)
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
                                                                   'llazklnk.dll',
                                                                   'llexctrl.dll',
                                                                   'llrpjet2.dll',
                                                                   'npbssplugin.dll',
                                                                   'perfcontrol.dll',
                                                                   'ptchmake.exe',
                                                                   'updateal.exe',
                                                                   'TranConv.exe',
                                                                   'wwwgate.exe',
                                                                   'TestTran.exe',
                                                                   'infoinst.exe',
                                                                   'gate_tst.exe',
                                                                   'testconn.exe',
                                                                   'etoknman.exe',
                                                                   'stunnel.exe',
                                                                   'defcfgup.exe',
                                                                   'rxctl5.bpl',
                                                                   'rtsrcfg.exe',
                                                                   'rtsconst.exe',
                                                                   'rtftobmp.exe',
                                                                   'PtchMakeCl.exe',
                                                                   'PrintServer.exe',
                                                                   'phonelib.bpl',
                                                                   'NewBase.exe',
                                                                   'btrieve.bpl',
                                                                   'mssobjs.bpl',
                                                                   'bsslgn.exe',
                                                                   'compiler.exe',
                                                                   'VrfAgava.exe',
                                                                   'BSSAxInf.exe',
                                                                   'bsImport.exe',
                                                                   'lresexpt.bpl',
                                                                   'BSChecker.exe',
                                                                   'bs1.exe',
                                                                   'VerifCCom.exe',
                                                                   'blksrv.bpl',
                                                                   'bssetup.exe',
                                                                   'aqtora32.dll',
                                                                   'blocksrv.dll',
                                                                   'rg_verb4.dll',
                                                                   'rg_vesta.dll',
                                                                   'cc.dll',
                                                                   'ccom.dll',
                                                                   'rg_vldt.dll',
                                                                   'sendreq.dll',
                                                                   'signcom.dll',
                                                                   'TrConvL.dll',
                                                                   'wsxml.dll',
                                                                   'llmsshnd.dll',
                                                                   'llmssobj.dll',
                                                                   'llsocket.dll',
                                                                   'llnetusr.dll',
                                                                   'cr_epass.dll',
                                                                   'llnotify.dll',
                                                                   'llnsPars.dll',
                                                                   'llnstool.dll',
                                                                   'llPhone.dll',
                                                                   'llPrReq.dll',
                                                                   'llrrts.dll',
                                                                   'ilCpyDocEx.dll',
                                                                   'llrtscfg.dll',
                                                                   'cr_pass.dll',
                                                                   'cr_sms.dll',
                                                                   'cr_util.dll',
                                                                   'llsmpp.dll',
                                                                   'llsnap.dll',
                                                                   'llsonic.dll',
                                                                   'devauth.dll',
                                                                   'devcheck.dll',
                                                                   'Dialogic.dll',
                                                                   'llSRP.dll',
                                                                   'eif2base.dll',
                                                                   'Emulator.dll',
                                                                   'LLSysInf.dll',
                                                                   'GetIName.dll',
                                                                   'lltblxml.dll',
                                                                   'llTrAuth.dll',
                                                                   'llTrServ.dll',
                                                                   'llubstr.dll',
                                                                   'llVTB.dll',
                                                                   'llwebdav.dll',
                                                                   'llwsexc.dll',
                                                                   'llxml3ed.dll',
                                                                   'llxmlcnz.dll',
                                                                   'mig173.dll',
                                                                   'mssreq.dll',
                                                                   'notiflog.dll',
                                                                   'rbaseal.dll',
                                                                   'RBProxy.dll',
                                                                   'rg_agava.dll',
                                                                   'rg_altok.dll',
                                                                   'rg_bsssl.dll',
                                                                   'rg_call.dll',
                                                                   'libcrypt.dll',
                                                                   'rg_calus.dll',
                                                                   'rg_ccm3e.dll',
                                                                   'llamqdll.dll',
                                                                   'rg_ccm3x.dll',
                                                                   'rg_ccom2.dll',
                                                                   'llCGate.dll',
                                                                   'rg_clear.dll',
                                                                   'rg_crypc.dll',
                                                                   'rg_cryptfld.dll',
                                                                   'rg_efssl.dll',
                                                                   'rg_exc4.dll',
                                                                   'rg_lite.dll',
                                                                   'llmssreq.dll',
                                                                   'lledint.dll',
                                                                   'rg_msapi.dll',
                                                                   'llepass.dll',
                                                                   'rg_msp11.dll',
                                                                   'rg_msp13.dll',
                                                                   'llfraud.dll',
                                                                   'llgraph.dll',
                                                                   'llgraph1.dll',
                                                                   'rg_msp2.dll',
                                                                   'rg_mspex.dll',
                                                                   'llhttp.dll',
                                                                   'rg_ossl.dll'
                                                                   ]


# -------------------------------------------------------------------------------------------------
class GlobalSettings:
    def __init__(self):
        self.stcmd = ''
        self.starteam_server = ''
        self.starteam_port = ''
        self.starteam_login = ''
        self.starteam_project = ''
        self.starteam_view = ''
        self.starteam_password = ''
        self.Labels = []
        self.BuildBK = ''
        self.BuildIC = ''
        self.BuildCrypto = ''
        self.PlaceBuildIntoPatchBK = False
        self.PlaceBuildIntoPatchIC = False
        self.ClientEverythingInEXE = False
        self.BuildRTSZIP = False
        self.LicenseServer = ''
        self.LicenseProfile = ''
        self.Is20Version = None
        self.BLLVersion = ''
        self.__success = False
        self.read_config()

    def was_success(self):
        return self.__success

    def read_config(self):
        ini_filename = 'settings.ini'
        section_special = 'SPECIAL'
        section_common = 'COMMON'
        section_labels = 'LABELS'
        section_build = 'BUILD'
        try:
            if not os.path.exists(ini_filename):
                raise FileNotFoundError('NOT FOUND ' + ini_filename)
            parser = configparser.RawConfigParser()
            res = parser.read(ini_filename, encoding="UTF-8")
            if res.count == 0:  # если файл настроек не найден
                raise FileNotFoundError('NOT FOUND {}'.format(ini_filename))
            self.stcmd = parser.get(section_common, 'stcmd').strip()
            self.starteam_server = parser.get(section_common, 'StarteamServer').strip()
            self.starteam_port = parser.get(section_common, 'StarteamPort').strip()
            self.starteam_project = parser.get(section_special, 'StarteamProject').strip()
            self.starteam_view = parser.get(section_special, 'StarteamView').strip()
            self.starteam_login = parser.get(section_special, 'StarteamLogin').strip()
            self.LicenseServer = parser.get(section_special, 'LicenseServer').strip()
            self.LicenseProfile = parser.get(section_special, 'LicenseProfile').strip()
            self.Labels = parser.items(section_labels)
            self.BuildBK = parser.get(section_build, 'BK').strip()
            self.BuildIC = parser.get(section_build, 'IC').strip()
            self.BuildCrypto = parser.get(section_build, 'Crypto').strip()
            self.PlaceBuildIntoPatchBK = parser.get(section_build, 'PlaceBuildIntoPatchBK').lower() == 'true'
            self.PlaceBuildIntoPatchIC = parser.get(section_build, 'PlaceBuildIntoPatchIC').lower() == 'true'
            self.ClientEverythingInEXE = parser.get(section_special, 'ClientEverythingInEXE').lower() == 'true'
            self.BuildRTSZIP = parser.get(section_special, 'BuildRTSZIP').lower() == 'true'
            self.BLLVersion = parser.get(section_build, 'BLLVersion').strip()
            # проверка Labels -----------------------------------
            all_labels = ''
            for label in self.Labels:
                all_labels += label[1].strip()

            if not self.Labels or not all_labels:  # Если не дали совсем никаких меток для загрузки
                raise ValueError('NO LABELS defined in {}'.format(ini_filename))

            # проверка stsmd -----------------------------------
            if self.stcmd:  # если пусть к stcmd не задан
                self.stcmd = os.path.normpath(self.stcmd)
                self.stcmd = self.stcmd + os.sep + 'stcmd.exe'
                if not os.path.exists(self.stcmd):
                    raise FileNotFoundError('NOT FOUND ' + self.stcmd)
            else:
                raise FileNotFoundError('NOT DEFINED path to stcmd')

            # проверка путей к билду
            if self.BuildBK and not os.path.exists(self.BuildBK):
                raise FileNotFoundError('NOT FOUND "{}"'.format(self.BuildBK))
            if self.BuildIC and not os.path.exists(self.BuildIC):
                raise FileNotFoundError('NOT FOUND "{}"'.format(self.BuildIC))

        except BaseException as e:
            log('ERROR when reading settings from file "{}":\n\t\t{}'.format(ini_filename, e))

        else:
            self.__success = True
            log('SETTINGS LOADED:\n\t'
                'StarteamProject = {}\n\t'
                'StarteamView = {}\n\t'
                'Labels = {}\n\t'
                'Licence server = {}\n\t'
                'Licence profile = {}\n\t'
                'Path to stcmd.exe = {}\n\t'
                'Build RTS.ZIP = {}\n\t'
                'Place BLL/DLL in EXE folder of Client patch = {}\n\t'
                'Place build files in patch = {}\n\t'
                'Place IC build files in patch = {}\n\t'
                'Path to build files = {}\n\t'
                'Path to IC build files = {}\n\t'
                'BLL version={}'.
                format(self.starteam_project, self.starteam_view, self.Labels, self.LicenseServer,
                       self.LicenseProfile, self.stcmd, self.BuildRTSZIP, self.ClientEverythingInEXE,
                       self.PlaceBuildIntoPatchBK, self.PlaceBuildIntoPatchIC, self.BuildBK, self.BuildIC,
                       self.BLLVersion))


# -------------------------------------------------------------------------------------------------
def get_password(message_text):
    import getpass
    # running under PyCharm or not
    if 'PYCHARM_HOSTED' in os.environ:
        return getpass.fallback_getpass(message_text)
    else:
        return getpass.getpass(message_text)


# -------------------------------------------------------------------------------------------------
def copy_tree(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                copy_tree(os.path.join(src, f),
                          os.path.join(dest, f),
                          ignore)
    else:
        shutil.copyfile(src, dest)


# -------------------------------------------------------------------------------------------------
def makedirs(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except BaseException as e:
        log('\tERROR: can''t create directory "{}" ({})'.format(path, e))


# -------------------------------------------------------------------------------------------------
def list_files(path, mask):
    files_list = [os.path.join(d, filename) for d, _, files in os.walk(path)
                  for filename in fnmatch.filter(files, mask)]
    return sorted(files_list)


# -------------------------------------------------------------------------------------------------
def list_files_by_list(path, mask_list):
    res_list = []
    for mask in mask_list:
        res_list += [os.path.join(d, filename) for d, _, files in os.walk(path)
                     for filename in fnmatch.filter(files, mask)]
    return res_list


# -------------------------------------------------------------------------------------------------
def list_files_remove_paths_and_change_extension(path, newext, mask_list):
    return [os.path.splitext(bls_file)[0] + newext for bls_file in
            [split_filename(bls_file) for bls_file in list_files_by_list(path, mask_list)]]


# -------------------------------------------------------------------------------------------------
# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=2, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    filled_length = int(round(bar_length * iteration / float(total)))
    percents = round(100.00 * (iteration / float(total)), decimals)
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write('%s [%s] %s%s %s\r' % (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()
    if iteration == total:
        log("\n")


# -------------------------------------------------------------------------------------------------
def copy_files(src_dir, dest_dir, wildcards=None, excluded_files=None):
    if wildcards is None:
        wildcards = ['*.*']
    if excluded_files is None:
        excluded_files = []
    for wildcard in wildcards:
        files = list_files(src_dir, wildcard)
        for filename_with_path in files:
            filename = split_filename(filename_with_path)
            if filename.lower() not in excluded_files and filename != '.' and filename != '..':
                makedirs(dest_dir)
                try:
                    shutil.copy2(filename_with_path, dest_dir)
                except BaseException as e:
                    log('\tERROR: can\'t copy file "{}" to "{}" ({})'.format(filename_with_path, dest_dir, e))


# -------------------------------------------------------------------------------------------------
def copyfiles_of_version(src_dir, dest_dir, exe_version, wildcards=None, excluded_files=None):
    if wildcards is None:
        wildcards = ['*.*']
    if excluded_files is None:
        excluded_files = []
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
                    log('\tERROR: can\'t copy file "{}" to "{}" ({})'.format(filename_with_path, dest_dir, e))


# -------------------------------------------------------------------------------------------------
def quote(string2prepare):
    return "\"" + string2prepare + "\""


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
    # if not os.access(path, os.W_OK):
    # Is the error an access error ?
    os.chmod(path, stat.S_IWRITE)
    os.chmod(path, stat.S_IWUSR)
    func(path)
    # else:
    #   raise BaseException(exc_info)


def clean(path, masks=None):
    if os.path.exists(path):
        try:
            if masks:
                log('CLEANING {} for {} files'.format(path, masks))
                for mask in masks:
                    # чистим все файлы по маске mask
                    [os.remove(os.path.join(d, filename)) for d, _, files in os.walk(path) for filename in
                     fnmatch.filter(files, mask)]
            else:
                log('\nCLEANING {}'.format(path))
                # Сначала чистим все файлы,
                [os.remove(os.path.join(d, filename)) for d, _, files in os.walk(path) for filename in files]
                # потом чистим все
                shutil.rmtree(path, onerror=__onerror_handler__)
        except FileNotFoundError:
            pass  # если папка отсутствует, то продолжаем молча
        except BaseException as e:
            log('\tERROR when cleaning ({})'.format(e))
            return False
    return True


# -------------------------------------------------------------------------------------------------
def starteam_list_directories(settings, label, label_command, excluded_folders=None):
    out = None
    counter = 0
    while (out is None) and (counter < 2):
        counter += 1
        launch_string = quote(settings.stcmd)
        launch_string += ' list -nologo -x -cf -p "{}:{}@{}:{}/{}/{}"'.format(
            settings.starteam_login,
            settings.starteam_password,
            settings.starteam_server,
            settings.starteam_port,
            settings.starteam_project,
            settings.starteam_view)
        message_text = '\nLoading directories from Starteam'
        if label_command:
            launch_string += label_command
            message_text += ' for label(date) "{}"'.format(label)
        log(message_text + '. Please wait...')
        process = subprocess.Popen(launch_string, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        process.stdout.close()
        if err:
            message_text = '\tCan not download directories for label(date) {}.'.format(label)
            label = datetime.datetime.fromtimestamp(time.time()).strftime('%d.%m.%y %H:%M')
            label_command = ' -cfgd ' + quote(label)
            if counter == 1:
                message_text += ' TRYING to load directories for current time {}.'.format(label)
            log(message_text)
            out = None
        else:
            str_res = out.decode('windows-1251')
            if str_res:
                dir_list = str_res.splitlines()
                del dir_list[0]  # В первой строке будет путь к виду стартима
                dir_list = [dir_name.strip().replace('\\', '') for dir_name in dir_list]
                dir_list.sort()
                dir_list_return = []
                if excluded_folders:
                    excluded_folders_lower = [excluded_folder.lower() for excluded_folder in excluded_folders]
                    for directory in dir_list:
                        if directory.lower() not in excluded_folders_lower and \
                                'not in view' not in directory.lower() and \
                                'missing ' not in directory.lower():
                            dir_list_return.append(directory)
                log('\tList of directories: {}'.format(dir_list_return))
                if len(dir_list_return) > 0:
                    return dir_list_return
                else:
                    return None
            else:
                return None


# -------------------------------------------------------------------------------------------------
def download_starteam(settings, labels_list, path_for_after, path_for_before, st_path_to_download='',
                      st_file_to_download=''):
    total_result = False
    # Приставка к названию метки, в которой содержится название доп вида стартима
    key_alt_starteam_view = "_StarteamView".lower()
    try:
        if labels_list is None:
            labels_list = [('any', '')]
        for key, label in labels_list:
            is_download_between_dates = (key == 'datebefore' or key == 'dateafter')
            is_download_initial_state = (key == 'labelbefore' or key == 'datebefore')
            label_command_dir = label_command = ''
            if label:
                if is_download_between_dates:
                    label_command_dir = label_command = ' -cfgd ' + quote(label)
                else:
                    label_command_dir = ' -cfgl ' + quote(label)
                    label_command = ' -vl ' + quote(label)
            starteam_dirs = None
            if st_path_to_download == '':
                starteam_dirs = starteam_list_directories(settings, label, label_command_dir,
                                                          ['BLL', 'BLL_Client', 'Doc', '_Personal',
                                                           '_TZ', '_ProjectData', '_ProjectData2',
                                                           'BUILD', 'History', 'Scripts', 'DLL',
                                                           'Config'])
            if starteam_dirs is None:
                starteam_dirs = ['']
            for starteam_dir in starteam_dirs:
                if starteam_dir == '':
                    starteam_dir = st_path_to_download
                # Если название метки НЕ содержит "_StarteamView", то будем грузить
                # (а если содержит, то это не метка, а приставка с указанием вида в стартиме)
                if key_alt_starteam_view not in key:
                    if not label and not st_file_to_download:
                        raise ValueError('No label or file to download specified')
                    message_text = 'DOWNLOADING'
                    if st_file_to_download:
                        message_text += ' files "{}{}"'.format(starteam_dir, st_file_to_download)
                    if label:
                        message_text += ' files for label(date) "{}" from {}'.format(label, starteam_dir)

                    if is_download_initial_state:
                        outdir = path_for_before
                    else:
                        outdir = path_for_after

                    message_text += ' to "{}"'.format(outdir)

                    # Если у метки есть указание для скачивания в альтернативном виде,
                    # например Label22_StarteamView = DBO:Release_17:VIP:GPB:GPB 017.3 107N
                    starteam_view = settings.starteam_view
                    try:
                        label_alt_starteam_view = dict(labels_list)[key + key_alt_starteam_view]
                        if label_alt_starteam_view is not None:
                            starteam_view = label_alt_starteam_view
                            message_text += ' from "' + starteam_view + '"'
                    except KeyError:
                        pass

                    launch_string = quote(settings.stcmd)
                    launch_string += ' co -nologo -stop -q -x -o -is -p "{}:{}@{}:{}/{}/{}'.format(
                        settings.starteam_login,
                        settings.starteam_password,
                        settings.starteam_server,
                        settings.starteam_port,
                        settings.starteam_project,
                        starteam_view)
                    if starteam_dir:
                        launch_string += '/{}'.format(starteam_dir)
                    launch_string += '"'
                    launch_string += ' -rp "{}"'.format(outdir)
                    if label_command:
                        launch_string += label_command
                    if st_file_to_download:
                        launch_string += " " + st_file_to_download

                    log(message_text + '. Please wait...')
                    result = subprocess.call(launch_string)
                    if result == 0:
                        # log('\tFINISHED '+message_text)
                        total_result += True
                    else:
                        log('\tERROR ' + message_text)
                        total_result += False

    except BaseException as e:
        log('\tERROR when downloading from Starteam ({})'.format(e))
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
                log('\tcopying {}'.format(path))
                makedirs(wheretocopy)
                shutil.copy2(path, wheretocopy)
            else:
                log('\tsomething wrong {} -> {}'.format(path, wheretocopy))

    if dircmp.right_only:
        for file in dircmp.right_only:
            path = os.path.join(after, file)
            if os.path.isfile(path):
                log('\tcopying {}'.format(path))
                makedirs(wheretocopy)
                shutil.copy2(path, wheretocopy)
            else:
                log('\tcopying DIR with contents {}'.format(path))
                clean(os.path.join(wheretocopy, file))
                copy_tree(path, os.path.join(wheretocopy, file))


# -------------------------------------------------------------------------------------------------


def compare_directories_before_and_after():
    if os.path.exists(const_dir_BEFORE):
        log('BEGIN compare directories:')
        log('\tBEFORE: {}'.format(const_dir_BEFORE))
        log('\tAFTER:  {}'.format(const_dir_AFTER))
        __compare_and_copy_dirs_recursively__(const_dir_BEFORE, const_dir_AFTER, const_dir_COMPARED)
    else:
        os.rename(const_dir_AFTER, const_dir_COMPARED)
        log('\tUSING folder "AFTER" as compare result, because "BEFORE" not exists:')
        log('\tBEFORE (not exists): {}'.format(const_dir_BEFORE))
        log('\tAFTER              : {}'.format(const_dir_AFTER))
    if os.path.exists(const_dir_COMPARED):
        log('\tFINISHED compare directories. LOOK at {}'.format(const_dir_COMPARED))
        return True
    else:
        log('\tFINISHED compare directories. NO CHANGES!!!')
        return False


# -------------------------------------------------------------------------------------------------


def make_upgrade10_eif_string_for_tables(file_name):
    file_name_lower = file_name.lower()

    # Для дефолтных таблиц и таблиц в памяти
    if file_name_lower.endswith('default') or \
            file_name_lower.startswith('root') or \
            file_name_lower == 'customeroldrpl' or \
            file_name_lower == 'memorydiasoftbuf':
        result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|FALSE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Таблицы'>"

    elif file_name.find(".") > 0:  # Для блобов
        result = "<{}|{}|'{}'|TRUE|FALSE|FALSE|FALSE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Таблицы'>"

    # обновление дельтой
    elif file_name_lower == 'orderstartflag':
        result = "<{}|{}|'{}'|TRUE|TRUE|TRUE|TRUE|TRUE|TRUE|'Flag'|NULL|NULL|NULL|NULL|'Таблицы'>" \
                 " #TODO проверьте data таблицы"
    elif file_name_lower == 'docschemesettings':
        result = "<{}|{}|'{}'|TRUE|TRUE|TRUE|TRUE|TRUE|TRUE|'ID'|NULL|NULL|NULL|NULL|'Таблицы'>" \
                 " #TODO проверьте data таблицы"
    elif file_name_lower == 'docprintsettings':
        result = "<{}|{}|'{}'|TRUE|TRUE|TRUE|TRUE|TRUE|TRUE|'BranchID,CustId,SchemeId'|NULL|NULL|NULL|NULL|'Таблицы'>" \
                 " #TODO проверьте data таблицы"
    elif file_name_lower == 'docmultiprintsettings':
        result = "<{}|{}|'{}'|TRUE|TRUE|TRUE|TRUE|TRUE|TRUE|'SchemeID,PrintFormName'|NULL|NULL|NULL|NULL|'Таблицы'>" \
                 " #TODO проверьте data таблицы"
    elif file_name_lower == 'filtersettings':
        result = "<{}|{}|'{}'|TRUE|TRUE|TRUE|TRUE|TRUE|TRUE|'ScrollerName'|NULL|NULL|NULL|NULL|'Таблицы'> " \
                 "#TODO проверьте data таблицы"
    elif file_name_lower == 'linktxt':
        result = "<{}|{}|'{}'|TRUE|TRUE|TRUE|TRUE|TRUE|TRUE|'NameFormat'|NULL|NULL|NULL|NULL|'Таблицы'> " \
                 "#TODO проверьте data таблицы"
    elif file_name_lower == 'absmanagertype':
        result = "<{}|{}|'{}'|TRUE|TRUE|TRUE|TRUE|TRUE|TRUE|'ID'|NULL|NULL|NULL|NULL|'Таблицы'>"
    elif file_name_lower == 'dcmversions':
        result = "<{}|{}|'{}'|TRUE|TRUE|TRUE|TRUE|TRUE|TRUE|'SchemeID,PatchNewVersion'|NULL|NULL|NULL|NULL|'Таблицы'>"
    elif file_name_lower == 'transschema':
        result = "<{}|{}|'{}'|TRUE|TRUE|TRUE|TRUE|TRUE|TRUE|'ConnType,SchemaName'|NULL|NULL|NULL|NULL|'Таблицы'>"
    elif file_name_lower == 'remotenavmenus':
        result = "<{}|{}|'{}'|TRUE|TRUE|TRUE|TRUE|TRUE|TRUE|'ID'|NULL|NULL|NULL|NULL|'Таблицы'> " \
                 "#TODO проверьте data таблицы"
    elif file_name_lower == 'remotenavtrees':
        result = "<{}|{}|'{}'|TRUE|TRUE|TRUE|TRUE|TRUE|TRUE|'ID'|NULL|NULL|NULL|NULL|'Таблицы'> " \
                 "#TODO проверьте data таблицы, обновлять нужно только эталонное дерево"
    elif file_name_lower == 'offersettings':
        result = "<{}|{}|'{}'|TRUE|TRUE|TRUE|TRUE|TRUE|TRUE|'Autokey'|NULL|NULL|NULL|NULL|'Таблицы'>"

    # пересоздание
    elif file_name_lower == 'postclnt':
        result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|FALSE|NULL|NULL|NULL|NULL|NULL|'Таблицы'>"

    # полностью заменяющиеся данные:
    elif file_name_lower == 'noticeconfig' or file_name_lower == 'paygrndparam' or \
            file_name_lower == 'mailreport' or file_name_lower == 'wanavtrees' or \
            file_name_lower == 'balaccountsettings' or file_name_lower == 'rkobranches' or \
            file_name_lower == 'mb2_versionsinfo' or file_name_lower == 'mb_remotecfg' or \
            file_name_lower == 'nocopydocfields' or file_name_lower == 'mbamsgxmlstructure' or \
            file_name_lower == 'mbamsgscheme' or file_name_lower == 'mbamsgdocstatus' or \
            file_name_lower == 'mbadocumentssettings' or file_name_lower == 'smssettings' or \
            file_name_lower == 'azkestimate':
        result = "<{}|{}|'{}'|TRUE|TRUE|TRUE|TRUE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Таблицы'>"

    elif file_name_lower == 'controlsettings' or \
            file_name_lower == 'controlconstants' or \
            file_name_lower == 'controlgroups':
        result = "<{}|{}|'{}'|  ДОЛЖЕН БЫТЬ ВЫЗОВ uaControls или другой ua-шки  >"

    else:  # Если заливается структура полностью
        result = "<{}|{}|'{}'|TRUE|TRUE|TRUE|TRUE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Таблицы'> " \
                 "#TODO проверьте способ обновления таблицы, сейчас - заливается полностью. " \
                 "Для дельты и обновления строк: |TRUE|TRUE|TRUE|TRUE|TRUE|TRUE|'название_полей'. " \
                 "Только заменить структуру десятки: |TRUE|FALSE|FALSE|FALSE|TRUE|FALSE|NULL. " \
                 "Заменить структуру и пересоздать: |TRUE|TRUE|FALSE|TRUE|TRUE|FALSE|NULL."
    return result


# -------------------------------------------------------------------------------------------------


def make_upgrade10_eif_string_by_file_name(counter, file_name):
    result = ''
    file_type_match = re.findall(r'\((?:\d+|data)\)\.eif', file_name, flags=re.IGNORECASE)
    if len(file_type_match):
        structure_type_raw = file_type_match[0]
        structure_type = re.sub(r'\.eif', '', structure_type_raw, flags=re.IGNORECASE).replace('(', '').replace(')', '')
        if structure_type.upper() == 'DATA':
            return ''  # пропускаем data-файлы, за них ответят 10-файлы
        file_name = file_name.replace(structure_type_raw, '')
        if structure_type == '10':
            result = make_upgrade10_eif_string_for_tables(file_name)
        elif structure_type == '12':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|TRUE|NULL|NULL|NULL|NULL|NULL|'Визуальные формы'>"
        elif structure_type == '14':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|FALSE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Конфигурации'> " \
                     "#TODO проверьте настройку"
        elif structure_type == '16':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Автопроцедуры'>"
        elif structure_type == '18':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Профили'>"
        elif structure_type == '19':
            result = "<{}|{}|'{}'|TRUE|FALSE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Роли'>"
        elif structure_type == '20':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Привилегии'>"
        elif structure_type == '21':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Пользователи'>"
        elif structure_type == '30':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|TRUE|FALSE|TRUE|NULL|NULL|NULL|NULL|NULL|'Сценарии'>"
        elif structure_type == '65':
            if file_name.lower() == 'subsys(65).eif' or file_name.lower() == 'mbsc2(65).eif':
                result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|FALSE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'RTS SUBSYS(65)'> " \
                         "#TODO проверьте настройку"
            else:
                result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|FALSE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'RTS(65)'>"
        elif structure_type == '66':
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|FALSE|FALSE|TRUE|NULL|NULL|NULL|NULL|NULL|'RTS Errors/Tasks params'>"
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
        elif structure_type in ['52', '83']:
            result = "<{}|{}|'{}'|TRUE|TRUE|FALSE|FALSE|FALSE|FALSE|NULL|NULL|NULL|NULL|NULL|'Документарные операции'>"
        elif structure_type == '84':
            result = "<{}|{}|'{}'|TRUE|FALSE|FALSE|TRUE|TRUE|TRUE|NULL|NULL|NULL|NULL|NULL|'Статусы'>"
        else:
            log('\tERROR unknown structure type {} for filename {}'.format(structure_type, file_name))

        return '  ' + result.format(counter, structure_type, file_name) + '\n'
    else:
        log('\tERROR can not detect structure type by filename ({})'.format(file_name))


# -------------------------------------------------------------------------------------------------
def download_table_10_files_for_data_files(settings, instance):
    eif_list = list_files(dir_COMPARED_BASE(instance), "*.eif")
    for eif_file in eif_list:
        # проверим соответствует ли название файла формату "*(data).eif"
        file_type_match = re.findall(r'\(data\)\.eif', eif_file, flags=re.IGNORECASE)
        if len(file_type_match):
            eif10_file = str(eif_file).replace(file_type_match[0], '(10).eif')
            # отрежем путь (splitfilename не пашет, если файла нет)
            eif10_file = get_last_element_of_path(eif10_file)
            # и проверим есть ли файл eif10_file в списке файлов eif_list
            exists = [file1 for file1 in eif_list if re.search(re.escape(eif10_file), file1)]
            if not exists:
                # если файла eif10_file в списке загруженных файлов нет, то выгрузим его из стартима
                # сначала пытаемся выгрузить для 17 версии (папка TABLES), если не получается, то для 15 версии )(Table)
                if not download_starteam(settings, None, const_dir_COMPARED, '', 'BASE/' + instance + '/TABLES/',
                                         eif10_file):
                    download_starteam(settings, None, const_dir_COMPARED, '', 'BASE/' + instance + '/Table/',
                                      eif10_file)


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
                log('\tUnable to copy file. %s' % e)

        eif_list = list_files(data_dir, '*.eif')
        if len(eif_list) > 0:
            with open(get_filename_UPGRADE10_eif(instance), mode='w') as f:
                f.writelines(const_UPGRADE10_HEADER)

                line = make_upgrade10_eif_string_by_file_name(1, 'Version(14).eif')
                f.writelines(line)
                counter = 2
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
        file_data = open(file).read()
    except IOError or FileNotFoundError:
        return "Unknown"
    offset = file_data.find(str(sig))
    if offset == -1:
        return "Unknown"

    file_data = b''
    file_data = file_data[offset + 32: offset + 32 + (13 * 4)]
    version_structure = struct.unpack("13I", file_data)
    ver_ms, ver_ls = version_structure[4], version_structure[5]
    return "%d.%d.%d.%d" % (ver_ls & 0x0000ffff, (ver_ms & 0xffff0000) >> 16,
                            ver_ms & 0x0000ffff, (ver_ls & 0xffff0000) >> 16)


# -------------------------------------------------------------------------------------------------
def get_binary_platform(full_file_path):
    image_file_machine_i386 = 332
    image_file_machine_ia64 = 512
    image_file_machine_amd64 = 34404

    try:
        with open(full_file_path, 'rb') as f:
            s = f.read(2).decode(encoding="utf-8", errors="strict")
            if s != "MZ":
                return None
                # log("Not an EXE file")
            else:
                f.seek(60)
                s = f.read(4)
                header_offset = struct.unpack("<L", s)[0]
                f.seek(header_offset + 4)
                s = f.read(2)
                machine = struct.unpack("<H", s)[0]

                if machine == image_file_machine_i386:
                    return "Win32"
                    # log("IA-32 (32-bit x86)")
                elif machine == image_file_machine_ia64:
                    return "Win64"
                    # log("IA-64 (Itanium)")
                elif machine == image_file_machine_amd64:
                    return "Win64"
                    # log("AMD64 (64-bit x86)")
                else:
                    return "Unknown"
                    # log("Unknown architecture")
    except IOError or FileNotFoundError:
        return None


# -------------------------------------------------------------------------------------------------
def __get_exe_file_info__(full_file_path):
    # http://windowssdk.msdn.microsoft.com/en-us/library/ms646997.aspx
    sig = struct.pack("32s", u"VS_VERSION_INFO".encode("utf-16-le"))
    # This pulls the whole file into memory, so not very feasible for
    # large binaries.
    try:
        with open(full_file_path, 'rb') as f:
            file_data = f.read()
    except IOError or FileNotFoundError:
        return None
    offset = file_data.find(sig)
    if offset == -1:
        return None

    file_data = file_data[offset + 32: offset + 32 + (13 * 4)]
    version_structure = struct.unpack("13I", file_data)
    ver_ms, ver_ls = version_structure[4], version_structure[5]
    return "%d.%d.%d.%d" % (ver_ls & 0x0000ffff, (ver_ms & 0xffff0000) >> 16,
                            ver_ms & 0x0000ffff, (ver_ls & 0xffff0000) >> 16)


# -------------------------------------------------------------------------------------------------


def extract_build_version(build_path):
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
                except IOError or FileNotFoundError:
                    pass
                # отладочный билд имеет кривую версию, нужно пропустить
                if (ver is not None) and (ver != '1.0.0.0') and (ver != '0.0.0.0'):
                    result = ver
                    break

    except BaseException as e:
        log('\tERROR: can not detect version of build ({})'.format(e))
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
        except ValueError:
            pass
        else:
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
                list_of_uses = re.findall(r'(?<=\buses\s)(?s)(.*?)(?=;)', text, flags=re.IGNORECASE | re.MULTILINE)

                file_name_without_path = split_filename(file_name).lower()
                # добавляем пустой элемент для файла "file_name", на случай, если файл не имеет uses
                bls_uses_graph.update({file_name_without_path: [file_name, []]})

                if len(list_of_uses):
                    for text_of_uses in list_of_uses:
                        # разбиваем найденный текст на части между запятыми
                        uses_list = [line.strip() + '.bls' for line in text_of_uses.split(',') if line.strip()]
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
                                # bls_uses_graph.update({file_name_without_path: [file_name, uses_list]})
                                pass

    return bls_uses_graph


# -------------------------------------------------------------------------------------------------
def __bls_compile_one_file__(build_path, bls_file_name, bls_path, uses_list, lic_server, lic_profile, version):
    # log(BlsPath)
    # проверим, есть ли компилятор
    bscc_path = os.path.join(build_path, 'bscc.exe')
    if not os.path.exists(bscc_path):
        # компилятора нет, ошибка
        raise FileNotFoundError('Compiler {} not found'.format(bscc_path))
    run_str = bscc_path + ' "{}" -M0 -O0 -S{} -A{}'.format(bls_path, lic_server, lic_profile)
    if version:
        run_str = run_str + ' -V"{}"'.format(version)
    # log(run_str)
    '''
    subprocess.call(run_str)
    return True
    '''
    process = subprocess.Popen(run_str, shell=False, stdout=subprocess.PIPE)  # , stderr=subprocess.PIPE
    out, err = process.communicate()
    process.stdout.close()
    str_res = '\n\t\t\t' + out.decode('windows-1251').replace('\n', '\n\t\t\t')
    # succesfully с ошибкой. так и должно быть
    if 'Compiled succesfully' not in str_res and \
            'Compiled with warnings' not in str_res:
        log('\tERROR: File "{}", Uses list "{}"{}'.format(bls_file_name, uses_list, str_res))
        log('\tCOMPILATION continues. Please wait...')
        return False
    else:
        # log('\tCompiled "{}"'.format(bls_file_name))
        return True


# -------------------------------------------------------------------------------------------------
def __bls_compile_all_implementation__(lic_server, lic_profile, build_path,
                                       bls_uses_graph, bls_file_name, observed_list,
                                       version, tabs):
    bls_file_name = bls_file_name.lower()
    if bls_file_name not in observed_list:  # если файл отсутствует в списке обработанных
        percents = int(100.00 * len(observed_list) / len(bls_uses_graph))
        log("{:>3}%".format(percents) + tabs + "{}".format(bls_file_name))
        bls_item_info = bls_uses_graph.get(bls_file_name)
        if bls_item_info:
            bls_file_path = bls_item_info[0]
            uses_list = bls_item_info[1]
            if len(uses_list):  # если файл зависит от других файлов, то проведем
                for UsesFileName in uses_list:  # компиляцию каждого файла
                    __bls_compile_all_implementation__(lic_server,
                                                       lic_profile,
                                                       build_path,
                                                       bls_uses_graph,
                                                       UsesFileName,
                                                       observed_list,
                                                       version, tabs + "\t")
            if __bls_compile_one_file__(build_path, bls_file_name, bls_file_path,
                                        uses_list, lic_server, lic_profile, version):
                observed_list.append(bls_file_name)  # добавляем в список учтенных файлов
        else:
            log(tabs + 'No information about file to compile "{}". Probably not all SOURCE were downloaded.'.format(
                bls_file_name))


# -------------------------------------------------------------------------------------------------
def bls_compile_all(lic_server, lic_profile, build_path, source_path, bll_version):
    clean(build_path, ['*.bls', '*.bll'])  # очищаем каталог билда от bls и bll
    log('BEGIN BLS COMPILATION. Please wait...')
    copy_files(source_path, build_path, ['*.bls'], [])  # копируем в каталог билда все bls
    bls_uses_graph = bls_get_uses_graph(build_path)  # строим граф зависимостей по строкам uses
    observed_list = []
    try:
        for bls_file_name in bls_uses_graph:  # компилируем все bls
            __bls_compile_all_implementation__(lic_server, lic_profile, build_path, bls_uses_graph,
                                               bls_file_name, observed_list,
                                               bll_version, "\t")
        log("\tCOMPILED {} of {}".format(len(observed_list), len(bls_uses_graph)))
        return True
    except FileNotFoundError as e:
        log('\tERROR: {}'.format(e))
        return False


# -------------------------------------------------------------------------------------------------
def __extract_build__(build_path):
    build_zip_file = split_filename(build_path)
    if '.zip' in build_zip_file.lower():
        build_tmp_dir = os.path.join(tempfile.gettempdir(), build_zip_file)
        clean(build_tmp_dir)
        log('EXTRACTING BUILD "{}" in "{}"'.format(build_path, build_tmp_dir))
        try:
            with zipfile.ZipFile(build_path) as z:
                z.extractall(os.path.join(tempfile.gettempdir(), build_zip_file))
                # запомним путь во временный каталог в качестве
                # нового пути к билду для последующего применения
                build_path = build_tmp_dir
        except BaseException as e:
            log('\tERROR EXTRACTING BUILD "{}"'.format(e))
        # конец разархивации
    return build_path


# -------------------------------------------------------------------------------------------------
def is_20_version(version):
    return ('20.1' in version) or ('20.2' in version) or ('20.3' in version)


# -------------------------------------------------------------------------------------------------
def __copy_build_ex__(build_path, build_path_crypto, dest_path, only_get_version):
    # проверка наличия пути build_path
    if not build_path:
        return
    if not os.path.exists(build_path):
        log('\tPATH {} does not exists'.format(build_path))
        return
    # если ссылка на билд указывает не на каталог, а на файл архива
    # попробуем провести разархивацию во временный каталог
    build_path = __extract_build__(build_path)
    if build_path_crypto:
        build_path_crypto = __extract_build__(build_path_crypto)
    # определяем версию билда
    version = extract_build_version(build_path)
    if not only_get_version:
        if is_20_version(version):
            for release in ['32', '64']:
                win_rel = 'Win{}\\Release'.format(release)
                src = os.path.join(build_path, win_rel)
                dst = os.path.join(dest_path, win_rel)
                clean(dst)
                log('COPYING BUILD {} from "{}" in "{}"'.format(version, src, dst))
                copy_files(src, dst, ['*.exe', '*.ex', '*.bpl', '*.dll'], [])
                if build_path_crypto:
                    src = os.path.join(build_path_crypto, win_rel)
                    log('COPYING CRYPTO BUILD {} from "{}" in "{}"'.format(version, src, dst))
                    copy_files(src, dst, ['CryptLib.dll', 'cr_*.dll'], [])
        else:
            clean(dest_path)
            log('COPYING BUILD {} from "{}" in "{}"'.format(version, build_path, dest_path))
            copy_files(build_path, dest_path, ['*.exe', '*.ex', '*.bpl', '*.dll'], [])
            if build_path_crypto:
                log('COPYING CRYPTO BUILD {} from "{}" in "{}"'.format(version, build_path, dest_path))
                copy_files(build_path_crypto, dest_path, ['CryptLib.dll', 'cr_*.dll'], [])
    return version


# -------------------------------------------------------------------------------------------------
def __copy_build__(build_path, build_path_crypto, dest_path):
    return __copy_build_ex__(build_path, build_path_crypto, dest_path, False)


# -------------------------------------------------------------------------------------------------
def get_build_version(settings):
    log('Detecting BUILD VERSION')
    version = __copy_build_ex__(settings.BuildBK, None, None, True)
    log('\tBUILD VERSION is {}'.format(version))
    return version


# -------------------------------------------------------------------------------------------------
def download_build(settings):
    build = settings.BuildBK
    build_ic = settings.BuildIC
    build_crypto = settings.BuildCrypto
    build_version = build_ic_version = ''
    instances = []
    if build:
        instances.append(const_instance_BANK)
        instances.append(const_instance_CLIENT)
        instances.append(const_instance_CLIENT_MBA)
        build_version = __copy_build__(build, build_crypto, const_dir_TEMP_BUILD_BK)
    if build_ic:
        instances.append(const_instance_IC)
        build_ic_version = __copy_build__(build_ic, build_crypto, const_dir_TEMP_BUILD_IC)

    if not len(instances):
        return False

    for instance in instances:
        if instance in [const_instance_BANK, const_instance_CLIENT, const_instance_CLIENT_MBA]:
            is20 = is_20_version(build_version)
            if is20 and instance == const_instance_BANK:
                build_path = os.path.join(const_dir_TEMP_BUILD_BK, 'Win32\\Release')
                # это копируются все файлы, которые будут участвовать в компиляции BLS на следующем шаге
                # т.к. в результате __copy_build__ весь билд оказывается разделен на Win32 и Win64
                copy_files(build_path, const_dir_TEMP_BUILD_BK, ['*.*'], [])
        else:
            is20 = is_20_version(build_ic_version)
        settings.Is20Version = is20

        #  Если в настройках включено копирование билда в патч
        if settings.PlaceBuildIntoPatchBK or settings.PlaceBuildIntoPatchIC:
            log('COPYING build into patch for {}'.format(instance))
            excluded_files = ''
            if instance == const_instance_BANK:
                excluded_files = const_excluded_build_for_BANK
            elif instance == const_instance_IC:
                excluded_files = const_excluded_build_for_BANK
            elif instance in [const_instance_CLIENT, const_instance_CLIENT_MBA]:
                excluded_files = const_excluded_build_for_CLIENT
            if is20:  # для билда 20-ой версии
                if instance == const_instance_IC and settings.PlaceBuildIntoPatchIC:  # выкладываем билд плагина для ИК
                    build_path_bank = os.path.join(const_dir_TEMP_BUILD_BK,
                                                   'Win32\\Release')  # подготовим путь к билду банка
                    mask = ['bssetup.msi', 'CalcCRC.exe']
                    copy_files(build_path_bank, dir_PATCH_LIBFILES_INETTEMP(), mask, [])
                    mask = ['BssPluginSetup.exe', 'BssPluginWebKitSetup.exe']
                    copy_files(build_path_bank, dir_PATCH_LIBFILES_INETTEMP(), mask, [])

                    for release in ['32', '64']:  # выкладываем билд в LIBFILES32(64).BNK
                        build_path_bank = os.path.join(const_dir_TEMP_BUILD_BK, 'Win{}\\Release'.format(release))
                        copy_files(build_path_bank, dir_PATCH_LIBFILES_BNK(release), ['UpdateIc.exe'], [])
                        copy_files(build_path_bank, dir_PATCH_LIBFILES_BNK_WWW_EXE(release), ['bsiset.exe'], [])
                        mask = ['bsi.dll', 'bsi.jar']
                        copy_files(build_path_bank, dir_PATCH_LIBFILES_BNK_WWW_BSIscripts_RTIc(release), mask, [])
                        copy_files(build_path_bank, dir_PATCH_LIBFILES_BNK_WWW_BSIscripts_RTWa(release), mask, [])

                        build_path = os.path.join(const_dir_TEMP_BUILD_IC, 'Win{}\\Release'.format('32'))
                        mask = ['BssPluginSetup.exe', 'BssPluginSetupAdmin.exe', 'BssPluginSetupNoHost.exe',
                                'BssPluginWebKitSetup.exe', 'BssPluginSetup64.exe', 'BssPluginSetupGPB.exe',
                                'BssPluginSetupGPBNoHost.exe']
                        copy_files(build_path,
                                   dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTIc_CODE_BuildVersion(build_ic_version,
                                                                                              release),
                                   mask, [])
                        copy_files(build_path,
                                   dir_PATCH_LIBFILES_BNK_WWW_BSIsites_RTWa_CODE_BuildVersion(build_ic_version,
                                                                                              release),
                                   mask, [])

                elif settings.PlaceBuildIntoPatchBK:
                    if instance == const_instance_BANK:
                        build_path = os.path.join(const_dir_TEMP_BUILD_BK, 'Win32\\Release')
                        # это копируются все файлы, которые будут участвовать в компиляции BLS на следующем шаге
                        # т.к. в результате __copy_build__ весь билд оказывается разделен на Win32 и Win64
                        copy_files(build_path, const_dir_TEMP_BUILD_BK, ['*.*'], [])
                        copy_files(build_path, dir_PATCH(), ['CBStart.exe'], [])  # один файл CBStart.exe в корень патча
                    for release in ['32', '64']:  # выкладываем остальной билд для Б и БК для версий 32 и 64
                        build_path = os.path.join(const_dir_TEMP_BUILD_BK, 'Win{}\\Release'.format(release))
                        mask = ['*.exe', '*.ex', '*.bpl']
                        copy_files(build_path, dir_PATCH_LIBFILES_EXE(instance, release), mask, excluded_files)
                        copy_files(build_path, dir_PATCH_LIBFILES_SYSTEM(instance, release), ['*.dll'], excluded_files)
                        copy_files(build_path, dir_PATCH_CBSTART(instance, release), ['CBStart.exe'], [])
                        if instance == const_instance_BANK:
                            # заполняем TEMPLATE шаблон клиента в банковском патче
                            mask = ['*.exe', '*.ex', '*.bpl']
                            copy_files(build_path, dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX_CLIENT_EXE(release), mask,
                                       const_excluded_build_for_CLIENT)
                            copy_files(build_path, dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX_CLIENT_SYSTEM(release),
                                       ['*.dll'], const_excluded_build_for_CLIENT)
                            mask = ['CalcCRC.exe', 'Setup.exe', 'Install.exe', 'eif2base.exe', 'ilKern.dll',
                                    'GetIName.dll']
                            copy_files(build_path, dir_PATCH_LIBFILES_TEMPLATE_DISTRIBX(release), mask, [])
                            mask = ['ilGroup.dll', 'iliGroup.dll', 'ilProt.dll', 'ilCpyDoc.dll']
                            copy_files(build_path, dir_PATCH_LIBFILES_TEMPLATE_LANGUAGEX_EN(release), mask, [])
                            copy_files(build_path, dir_PATCH_LIBFILES_TEMPLATE_LANGUAGEX_RU(release), mask, [])

            else:  # для билдов 15 и 17
                build_path = const_dir_TEMP_BUILD_BK
                if instance in [const_instance_BANK, const_instance_CLIENT, const_instance_CLIENT_MBA] \
                        and settings.PlaceBuildIntoPatchBK:
                    # выкладываем билд для Б и БК
                    mask = ['*.exe', '*.ex', '*.bpl']
                    copy_files(build_path, dir_PATCH_LIBFILES_EXE(instance), mask, excluded_files)
                    if settings.ClientEverythingInEXE and instance == const_instance_CLIENT:
                        copy_files(build_path, dir_PATCH_LIBFILES_EXE(instance), ['*.dll'], excluded_files)
                    else:
                        copy_files(build_path, dir_PATCH_LIBFILES_SYSTEM(instance), ['*.dll'], excluded_files)

                if instance == const_instance_BANK and settings.PlaceBuildIntoPatchBK:
                    copy_files(build_path, dir_PATCH(), ['CBStart.exe'], [])  # один файл в корень
                    # заполняем билдом TEMPLATE шаблон клиента в банковском патче
                    mask = ['*.exe', '*.ex', '*.bpl']
                    copy_files(build_path, dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_EXE(), mask,
                               const_excluded_build_for_CLIENT)
                    if settings.ClientEverythingInEXE:
                        copy_files(build_path, dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_EXE(), ['*.dll'],
                                   const_excluded_build_for_CLIENT)
                    else:
                        copy_files(build_path, dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_SYSTEM(), ['*.dll'],
                                   const_excluded_build_for_CLIENT)
                    mask = ['CalcCRC.exe', 'Setup.exe', 'Install.exe', 'eif2base.exe', 'ilKern.dll', 'GetIName.dll']
                    copy_files(build_path, dir_PATCH_LIBFILES_TEMPLATE_DISTRIB(), mask, [])
                    mask = ['ilGroup.dll', 'iliGroup.dll', 'ilProt.dll', 'ilCpyDoc.dll']
                    copy_files(build_path, dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_EN(), mask, [])
                    copy_files(build_path, dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_RU(), mask, [])
                    copy_files(build_path, dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_EN_CLIENT_SYSTEM(), mask, [])
                    copy_files(build_path, dir_PATCH_LIBFILES_TEMPLATE_LANGUAGE_RU_CLIENT_SYSTEM(), mask, [])
                    # заполняем LIBFILES.BNK в банковском патче билдом для БК
                    mask = ['autoupgr.exe', 'bscc.exe', 'compiler.exe', 'operedit.exe', 'testconn.exe', 'treeedit.exe']
                    copy_files(build_path, dir_PATCH_LIBFILES_BNK_ADD(), mask, [])
                    copy_files(build_path, dir_PATCH_LIBFILES_BNK_BSISET_EXE(), ['bsiset.exe'], [])
                    copy_files(build_path, dir_PATCH_LIBFILES_BNK_LICENSE_EXE(), ['protcore.exe'], [])

                if instance == const_instance_IC and settings.PlaceBuildIntoPatchIC:
                    # заполняем LIBFILES.BNK в банковском патче билдом для ИК
                    build_path = const_dir_TEMP_BUILD_IC
                    mask = ['bssaxset.exe', 'inetcfg.exe', 'rts.exe', 'rtsconst.exe', 'rtsinfo.exe']
                    if settings.BuildRTSZIP:
                        copy_files(build_path, dir_PATCH_LIBFILES_BNK_RTS_EXE(), mask, [])
                    else:
                        copy_files(build_path, dir_PATCH_LIBFILES_EXE(const_instance_BANK), mask, [])
                    mask = ['llComDat.dll', 'llrtscfg.dll', 'llxmlman.dll', 'msxml2.bpl']
                    if settings.BuildRTSZIP:
                        copy_files(build_path, dir_PATCH_LIBFILES_BNK_RTS_SYSTEM(), mask, [])
                    else:
                        copy_files(build_path, dir_PATCH_LIBFILES_SYSTEM(const_instance_BANK), mask, [])
                    copy_files(build_path, dir_PATCH_LIBFILES_BNK_WWW_BSIscripts_RTIc(), ['bsi.dll'], [])
                    copy_files(build_path, dir_PATCH_LIBFILES_BNK_WWW_BSIscripts_RTAdmin(), ['bsi.dll'], [])
                    # todo INETTEMP
    return True


# -------------------------------------------------------------------------------------------------
def copy_bls(clean_destdir, source_dir, dest_dir):
    bls_version = '15'
    if os.path.exists(source_dir):
        # source_dir = const_dir_COMPARED_BLS
        # dest_dir = dir_PATCH_LIBFILES_SOURCE
        if os.path.exists(os.path.join(source_dir, 'SOURCE')):
            # если такой путь существует, значит BLS выложены как для 17/20 версии
            source_dir = os.path.join(source_dir, 'SOURCE')
            dest_dir = os.path.join(dest_dir, 'BLS')
            bls_version = '17/20'
        if clean_destdir:
            clean(dest_dir)
        log('COPYING BLS ("{}" version style) from "{}" to {}'.format(bls_version, source_dir, dest_dir))
        try:
            copy_tree(source_dir, dest_dir)
        except BaseException as e:
            log('\tERROR when copying ({})'.format(e))
            return False
        return True
    else:
        log('NOT COPYING BLS. Path {} not exists'.format(source_dir))
        return False


# -------------------------------------------------------------------------------------------------
def copy_bll(settings):
    log('COPYING BLL files to patch')
    bll_files_only_bank = list_files_remove_paths_and_change_extension(const_dir_COMPARED, '.bll', ['?b*.bls'])
    bll_files_only_rts = list_files_remove_paths_and_change_extension(const_dir_COMPARED, '.bll',
                                                                      ['RT_*.bls', 'sscommon.bls', 'ssxml.bls',
                                                                       'sserrors.bls'])
    bll_files_only_mba = list_files_remove_paths_and_change_extension(const_dir_COMPARED_BLS_SOURCE_RCK, '.bll',
                                                                      ['*.bls'])
    bll_files_all = list_files_remove_paths_and_change_extension(const_dir_COMPARED, '.bll', ['*.bls'])
    bll_files_tmp = list_files_by_list(const_dir_TEMP_BUILD_BK, bll_files_all)
    if len(bll_files_tmp) != len(bll_files_all):
        log('\tERROR: Not all changed BLS files were compiled {}'.format(list(set(bll_files_all) - set(bll_files_tmp))))
        return False

    bll_files_client_mba = list(set(bll_files_all) - set(bll_files_only_bank) - set(bll_files_only_rts))
    bll_files_client = list(set(bll_files_client_mba) - set(bll_files_only_mba))
    bll_files_all = list(set(bll_files_all) - set(bll_files_only_rts))

    # копируем bll для банка по списку bll_files_all
    copy_files(const_dir_TEMP_BUILD_BK, dir_PATCH_LIBFILES_USER(const_instance_BANK), bll_files_all, [])
    # копируем bll для RTS по списку bll_files_only_rts
    if settings.BuildRTSZIP:
        if settings.Is20Version:
            for release in ['32', '64']:
                copy_files(const_dir_TEMP_BUILD_BK, dir_PATCH_LIBFILES_BNK_RTS_USER(release), bll_files_only_rts, [])
        else:
            copy_files(const_dir_TEMP_BUILD_BK, dir_PATCH_LIBFILES_BNK_RTS_USER(), bll_files_only_rts, [])
    else:
        copy_files(const_dir_TEMP_BUILD_BK, dir_PATCH_LIBFILES_USER(const_instance_BANK), bll_files_only_rts, [])

    # копируем bll для клиента по разнице списков  bll_files_all-bll_files_only_bank
    if settings.ClientEverythingInEXE:
        copy_files(const_dir_TEMP_BUILD_BK, dir_PATCH_LIBFILES_EXE(const_instance_CLIENT), bll_files_client, [])
        copy_files(const_dir_TEMP_BUILD_BK, dir_PATCH_LIBFILES_EXE(const_instance_CLIENT_MBA), bll_files_client_mba, [])
        copy_files(const_dir_TEMP_BUILD_BK, dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_EXE(), bll_files_client, [])
    else:
        copy_files(const_dir_TEMP_BUILD_BK,
                   dir_PATCH_LIBFILES_USER(const_instance_CLIENT),
                   bll_files_client, [])
        copy_files(const_dir_TEMP_BUILD_BK,
                   dir_PATCH_LIBFILES_USER(const_instance_CLIENT_MBA),
                   bll_files_client_mba, [])
        copy_files(const_dir_TEMP_BUILD_BK,
                   dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_USER(),
                   bll_files_client, [])
    return True


# -------------------------------------------------------------------------------------------------
def copy_www(settings):
    source_dir = const_dir_COMPARED_WWW
    if os.path.exists(source_dir):
        try:
            if settings.Is20Version:
                for release in ['32', '64']:
                    dest_dir = dir_PATCH_LIBFILES_BNK_WWW(release)
                    log('COPYING WWW files to {}'.format(dest_dir))
                    copy_tree(source_dir, dest_dir)
            else:
                dest_dir = dir_PATCH_LIBFILES_BNK_WWW()
                log('COPYING WWW files to {}'.format(dest_dir))
                copy_tree(source_dir, dest_dir)
        except BaseException as e:
            log('\tERROR when copying ({})'.format(e))
    else:
        log('NOT COPYING WWW. Path {} not exists'.format(source_dir))


# -------------------------------------------------------------------------------------------------
def copy_rt_tpl(settings):
    source_dir = const_dir_COMPARED_RT_TPL
    if os.path.exists(source_dir):
        try:
            if settings.BuildRTSZIP:
                if settings.Is20Version:
                    for release in ['32', '64']:
                        dest_dir = dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_TEMPLATE(release)
                        log('COPYING RT_TPL files to {}'.format(dest_dir))
                        copy_tree(source_dir, dest_dir)
                else:
                    dest_dir = dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_TEMPLATE()
                    log('COPYING RT_TPL files to {}'.format(dest_dir))
                    copy_tree(source_dir, dest_dir)
            else:
                dest_dir = dir_PATCH_LIBFILES_SUBSYS_TEMPLATE()
                log('COPYING RT_TPL files to {}'.format(dest_dir))
                copy_tree(source_dir, dest_dir)

        except BaseException as e:
            log('\tERROR when copying ({})'.format(e))
    else:
        log('NOT COPYING RT_TPL. Path {} not exists'.format(source_dir))


# -------------------------------------------------------------------------------------------------
def copy_rtf(settings):
    source_dirs = [const_dir_COMPARED_RTF, const_dir_COMPARED_RTF_BANK,
                   const_dir_COMPARED_RTF_CLIENT, const_dir_COMPARED_RTF_REPJET]
    for source_dir in source_dirs:
        if os.path.exists(source_dir):
            dest_dirs = []
            what = 'RTF'
            # Общие и банковские
            if source_dir in [const_dir_COMPARED_RTF, const_dir_COMPARED_RTF_BANK]:
                dest_dirs.append(dir_PATCH_LIBFILES_SUBSYS_PRINT_RTF(const_instance_BANK))
            # Общие и клиентские
            if source_dir in [const_dir_COMPARED_RTF, const_dir_COMPARED_RTF_CLIENT]:
                dest_dirs.append(dir_PATCH_LIBFILES_SUBSYS_PRINT_RTF(const_instance_CLIENT))
                dest_dirs.append(dir_PATCH_LIBFILES_SUBSYS_PRINT_RTF(const_instance_CLIENT_MBA))
                dest_dirs.append(dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT_RTF())
                if settings.BuildRTSZIP:
                    if settings.Is20Version:
                        dest_dirs.append(
                            dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT_RTF('32'))
                        dest_dirs.append(
                            dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT_RTF('64'))
                    else:
                        dest_dirs.append(
                            dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT_RTF())
            # RepJet для всех
            if source_dir == const_dir_COMPARED_RTF_REPJET:
                what = 'RepJet'
                dest_dirs.append(dir_PATCH_LIBFILES_SUBSYS_PRINT_REPJET(const_instance_BANK))
                dest_dirs.append(dir_PATCH_LIBFILES_SUBSYS_PRINT_REPJET(const_instance_CLIENT))
                dest_dirs.append(dir_PATCH_LIBFILES_SUBSYS_PRINT_REPJET(const_instance_CLIENT_MBA))
                dest_dirs.append(dir_PATCH_LIBFILES_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT_RepJet())
                if settings.BuildRTSZIP:
                    if settings.Is20Version:
                        dest_dirs.append(
                            dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT_RepJet(
                                '32'))
                        dest_dirs.append(
                            dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT_RepJet(
                                '64'))
                    else:
                        dest_dirs.append(
                            dir_PATCH_LIBFILES_BNK_RTS_SUBSYS_INSTCLNT_TEMPLATE_DISTRIB_CLIENT_SUBSYS_PRINT_RepJet())
            for dest_dir in dest_dirs:
                log('COPYING {} files to {}'.format(what, dest_dir))
                copy_files(source_dir, dest_dir)
        else:
            log('NOT COPYING RTF from {}. Path not exists'.format(source_dir))


# -------------------------------------------------------------------------------------------------
def download_mba_dll(settings):
    if download_starteam(settings, None, const_dir_TEMP_BUILD_BK, '', 'DLL/', '*.dll'):
        copyfiles_of_version(os.path.join(const_dir_TEMP_BUILD_BK, 'DLL'),
                             const_dir_TEMP_BUILD_BK, 'Win32', ['*.dll'], [])
        return True


# -------------------------------------------------------------------------------------------------
def ask_starteam_password(settings):
    if settings.starteam_password == '':
        settings.starteam_password = get_password('\nMaestro, please, ENTER StarTeam PASSWORD for "{}":'.
                                                  format(settings.starteam_login))
    result = settings.starteam_password.strip() != ''
    if not result:
        log('ERROR: Empty password!')
    return result


# -------------------------------------------------------------------------------------------------
def make_decision_compilation_or_restart():
    continue_compilation = False
    if os.path.exists(const_dir_TEMP_TEMPSOURCE):
        log('Folder {} EXISTS. So we could CONTINUE bls-compilation.\n'
            '\tAsking Maestro for decision.'.format(const_dir_TEMP_TEMPSOURCE))
        continue_compilation = input('Maestro, please, ENTER any letter to CONTINUE bls '
                                     'compilation (otherwise patch building will be RESTARTED):') != ''
        if continue_compilation:
            log('\tMaestro decided to CONTINUE with bls-compilation instead of restart patch building')
        else:
            log('\tMaestro decided to RESTART patch building instead of CONTINUE with bls-compilation')
        if not continue_compilation:
            response = input(
                '\tREALLY?!\n\tMaestro, please, ENTER "Y" to CLEAR ALL and RESTART patch building:').upper()
            if response and response != 'Y':
                log('\tERROR: wrong answer {}'.format(response))
                exit(1000)
            continue_compilation = response != 'Y'
    return continue_compilation


# -------------------------------------------------------------------------------------------------
def main():
    log('{:=^120}'.format(''))
    global_settings = GlobalSettings()  # read_config()
    if not global_settings.was_success():
        return

    bls_just_downloaded = False
    continue_compilation = make_decision_compilation_or_restart()

    if not continue_compilation:
        if not clean(const_dir_TEMP):
            return

    if not continue_compilation:
        log('\nBUILD BEGIN {}'.
            format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
    else:
        log('\nCOMPILATION CONTINUED {}'.
            format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))

    # Если пользователь не выбрал продолжение компиляции, запустим
    # ЭТАП ЗАГРУЗКИ ПО МЕТКАМ И СРАВНЕНИЯ РЕВИЗИЙ:
    if not continue_compilation:
        if ask_starteam_password(global_settings):
            if download_starteam(global_settings, global_settings.Labels, const_dir_AFTER, const_dir_BEFORE):
                if not compare_directories_before_and_after():
                    log('\nEXIT -----------------')
                    return
                for instance in [const_instance_BANK, const_instance_CLIENT, const_instance_CLIENT_MBA]:
                    download_table_10_files_for_data_files(global_settings, instance)
                    generate_upgrade10_eif(instance)
                bls_just_downloaded = continue_compilation = copy_bls(True,
                                                                      const_dir_COMPARED_BLS,
                                                                      dir_PATCH_LIBFILES_SOURCE)
                need_download_build = \
                    continue_compilation or global_settings.PlaceBuildIntoPatchBK or \
                    global_settings.PlaceBuildIntoPatchIC
                build_downloaded = False
                # если требуется загрузка билда (для компиляции или для помещения в патч)
                if need_download_build:
                    build_downloaded = download_build(global_settings)
                #  если требуется загрузка билда и предыдущая загрузка основного билда успешна
                if build_downloaded and need_download_build:
                    download_mba_dll(global_settings)
                # Если билд не скачивался (при этом мы определяемся с версией билда),
                # то все равно попробуем получить его версию, чтобы определиться с каталогами
                # для выкладывания ИК
                if not build_downloaded:
                    build_version = get_build_version(global_settings)
                    global_settings.Is20Version = is_20_version(build_version)
                copy_www(global_settings)
                copy_rt_tpl(global_settings)
                copy_rtf(global_settings)
                continue_compilation = continue_compilation and (build_downloaded or not need_download_build)

    # если ЭТАП ЗАГРУЗКИ завершился успешно,
    # или пользователь выбрал переход к компиляции
    # запускаем ЭТАП КОМПИЛЯЦИИ bls-файлов:
    if continue_compilation:
        do_download_bls = True
        # если bls-файлы были загружены не на ЭТАПЕ ЗАГРУЗКИ, спросим не стоит ли перезагрузить
        if not bls_just_downloaded:
            do_download_bls = input('Enter any letter to DOWNLOAD all bls-sources again:') != ''
        # если пользователь не отказался от загрузки всех исходников
        # или если все bls были загружены на ЭТАПЕ ЗАГРУЗКИ
        if do_download_bls:
            continue_compilation = False
            if ask_starteam_password(global_settings):
                # загрузим все исходники текущей ревизии
                continue_compilation = download_starteam(global_settings, None,
                                                         const_dir_TEMP_TEMPSOURCE,
                                                         const_dir_TEMP_TEMPSOURCE,
                                                         'BLS/', '*.bls')
                if continue_compilation:
                    # тест - не выкачивать, а взять результат сравнения
                    copy_bls(False,
                             const_dir_COMPARED_BLS,
                             const_dir_TEMP_TEMPSOURCE)
                    '''
                    # загрузим поверх ревизии исходников, помеченные метками
                    continue_compilation = download_starteam(global_settings,
                                                             global_settings.Labels,
                                                             const_dir_TEMP_TEMPSOURCE,
                                                             const_dir_TEMP_TEMPSOURCE,
                                                             'BLS/', '*.bls')
                    '''
        # запустим компиляцию этой каши
        if continue_compilation:
            if bls_compile_all(global_settings.LicenseServer, global_settings.LicenseProfile,
                               const_dir_TEMP_BUILD_BK, const_dir_TEMP_TEMPSOURCE,
                               global_settings.BLLVersion):
                # копируем готовые BLL в патч
                copy_bll(global_settings)
    log('\nDONE -----------------')


main()
