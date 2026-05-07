from setuptools import setup

setup(
    name='yapc',
    version='0.1-alpha',
    py_modules=['yapc'],
    install_requires=[
        'exifread',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'yapc=yapc:cli',
        ],
    },
    url='http://cyfive.ru/yapc',
    license='GNU GPL 3.0 or above',
    author='Stanislav V. Emets',
    author_email='emetssv@mail.ru',
    description='Yet Another Photo Catalog - Organize photos by EXIF capture date'
)
