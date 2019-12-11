from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='libRL',
    version='1.1.1',
    description='Python library for characterizing Microwave Absorption',
    long_description=long_description,
    url='https://github.com/1mikegrn/libRL',
    author='Michael Green',
    author_email='1mikegrn@gmail.com',
    license='GPL-3.0',

    classifiers=[
        'Development Status :: 3 - Beta',
        'Intended Audience :: STEM research',
        'License :: OSI Approved :: GPL-3.0 License',
    ],

    packages=find_packages(),

    package_data={
        'libRL': ['*.pyx', '*.pyd']
    },

    include_package_data=True,
    python_requires='>=3.6',

    install_requires=[
        'numpy',
        'scipy',
        'pandas',
        'pathos',
        'xlrd',
        'matplotlib',
        'cython',
    ],

    project_urls={
        'GitHub': 'https://github.com/1mikegrn/libRL',
        'DocSite': 'https://1mikegrn.github.io/libRL/',
        'Personal Blog': 'http://www.inorganicexposure.com',
        'Google Scholar': 'https://scholar.google.com/citations?user=DxFljRYAAAAJ&hl=en'
    }
)