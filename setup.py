from setuptools import setup
from version import *
setup(
    name='ingestconfigcreator',
    author = 'Zhi Wei Li',
    version = version,
    install_requires=['pandas', 'openpyxl', 'numpy', 'snowflake-connector-python', 'customtkinter']
)