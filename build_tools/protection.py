"""Run PJOrion from a private build copy, preserving its installed configuration."""
import base64
import configparser
from contextlib import contextmanager
from pathlib import Path
import shutil

from build_tools.package_tools import sha
from build_tools.validate_build_data import require

FILES = ('PjOrion.exe', 'PjOrion.ini', 'python27.dll', 'python27.zip', 'dispack.zip', 'dcpack.zip')


@contextmanager
def obfuscator(tools, run):
    if tools['obfuscator_command']:
        yield tools['obfuscator_command'], None
        return
    require(tools['pjorion_home'], 'PJOrion missing; configure pjorion_home or obfuscator_command')
    installed = Path(tools['pjorion_home'])
    for name in FILES:
        require((installed / name).is_file(), 'Missing PJOrion dependency: ' + name)
    require((installed / 'DLLs').is_dir(), 'PJOrion DLLs directory is missing')
    original = {name: sha(installed / name) for name in FILES}
    sandbox = run / 'pjorion'
    sandbox.mkdir()
    for name in FILES:
        shutil.copyfile(installed / name, sandbox / name)
    shutil.copytree(installed / 'DLLs', sandbox / 'DLLs')
    settings = configparser.ConfigParser(interpolation=None)
    settings.optionxform = str
    try:
        settings.read(sandbox / 'PjOrion.ini', encoding='utf-8-sig')
    except UnicodeError:
        settings.clear()
        settings.read(sandbox / 'PjOrion.ini', encoding='cp1252')
    options = {
        'GENERAL': {'CheckWebUpdate': '0', 'AutoConnect': '1'},
        'PATHS': {'Python': base64.b64encode(str(sandbox / 'python27.dll').encode()).decode(),
                  'SelectedDir': base64.b64encode(str(run / 'protected').encode()).decode()},
        'FILEASSOCIATIONS': {'RegisterApplication': '0', 'PY': '0', 'PYC': '0'},
        'CONTEXTMENU': {'Integrate': '0'},
        'WOTTRANSMISSION': {'SearchWOT': '0', 'WOT': ''},
        'OBFUSCATE': {'AllNamesIsPublic': '1', 'DetailedAnalysis': '1'},
        'PROTECT': {'ExecOnlyInWOT': '0', 'LockAttributesReview': '0', 'UseWOTInjector': '0', 'CreateBackupFile': '0'}
    }
    for section, values in options.items():
        if not settings.has_section(section):
            settings.add_section(section)
        for key, value in values.items():
            settings.set(section, key, value)
    with (sandbox / 'PjOrion.ini').open('w', encoding='utf-8', newline='\n') as stream:
        settings.write(stream)
    try:
        yield [str(sandbox / 'PjOrion.exe'), '--protect-bytecode-file={output}', '/exit'], sandbox
    finally:
        require(all(sha(installed / name) == digest for name, digest in original.items()), 'Installed PJOrion files changed')
