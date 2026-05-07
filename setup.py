from setuptools import setup

setup(
    name='yapc',
    version='0.1',
    py_modules=['yapc'],
    install_requires=[
        'exifread',
    ],
    entry_points={
        'console_scripts': [
            'yapc=yapc:main',
        ],
    },
    url='http://cyfive.ru/yapc',
    license='GNU GPL 3.0 or above',
    author='Stanislav V. Emets',
    author_email='emetssv@mail.ru',
    description='Yet Another Photo Catalog'
)
