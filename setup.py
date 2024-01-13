from setuptools import setup, find_packages

import json
import os

if __name__ == '__main__':
    setup(
        name='wfenv',
        version=os.getenv('PACKAGE_VERSION', '0.0.1'),
        package_dir={"": "package"},  # Optional
        packages=find_packages('package'),
        description='A package',
        install_requires=['termcolor', 'pywin32', 'psutil'],
        entry_points={
            'console_scripts': ['wf-clean=wfenv:clean_main', 'wf-scan=wfenv:scan_main', 'wf-unsuspice=wfenv:unsuspice_main']
        }
    )
