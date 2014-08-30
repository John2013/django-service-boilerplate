#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function

import subprocess
import sys

from lib import fix_sys_paths, import_project_stub_settings, \
    venv_script_file, separate_requirements, make_temp_file, venv_pip_file, \
    pip_install, venv_activate_command


__author__ = 'pahaz'

if __name__ == "__main__":
    PRODUCTION_MODE = False
    USE_PIP_CACHE = True
    USE_FIXES = False

    if '--production' in sys.argv:
        PRODUCTION_MODE = True
    if '--no-use-pip-cache' in sys.argv:
        USE_PIP_CACHE = False
    if '--no-use-fixes' in sys.argv:
        USE_FIXES = False

    _PROJECT_STUB_SETTINGS_ = "_project_.stub_settings"

    fix_sys_paths()
    s = import_project_stub_settings(_PROJECT_STUB_SETTINGS_)

    print("\nMAKE VIRTUALENV\n")
    subprocess.call(['virtualenv', s.PATH_TO_PROJECT_VENV_DIR])

    if USE_FIXES and sys.platform == 'win32':
        print("\nINSTALL PIL [hotfix for windows]\n")
        easy_install = venv_script_file(s, 'easy_install')
        subprocess.call([easy_install, 'PIL'])

    print("\nINSTALL REQUIREMENTS\n")
    req = separate_requirements(s)
    common_req = req['common']
    dev_req = req['dev']

    print("\n# ! #\n# COMMON requirements:\n\n\n" + ''.join(common_req))
    print("\n# ! #\n# DEV requirements:\n\n\n" + ''.join(dev_req))

    common = make_temp_file(''.join(common_req))
    dev = make_temp_file(''.join(dev_req))

    pip = venv_pip_file(s)
    print("""
     # COMMON #
     """)
    pip_install(pip, common, USE_PIP_CACHE)
    if not PRODUCTION_MODE:
        print("""
     # DEV #
     """)
        pip_install(pip, dev, USE_PIP_CACHE)

    print("""NOW ACTIVATE:
     * {help_activate_venv}
    """.format(help_activate_venv=venv_activate_command(s)))
