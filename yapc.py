#!/usr/bin/env python3

'''
 Yet Another Photo Catalog
 Author: Stanislav V. Emets
 e-mail: emetssv@mail.ru

'''
import os
import stat
import shutil
from datetime import datetime
from typing import Optional
import exifread
import click


def is_catalog(p_path: str) -> bool:
    if not os.path.isdir(p_path):
        return False
    if os.path.isfile(os.path.join(p_path, ".yapc")):
        return True
    else:
        return False


def create_catalog(p_path: str) -> Optional[bool]:
    if is_catalog(p_path):
        click.echo(f"Path {p_path} already yet another photo catalog!")
        return False

    if os.path.isdir(p_path):
        catalog_desc = open(os.path.join(p_path, ".yapc"), "w")
        catalog_desc.close()
        click.echo("Catalog successfully created!")
    else:
        click.echo(f"Path {p_path} not found!")
        return False


def get_photo_date(p_path: str) -> str:
    """Extract date from EXIF or fallback to file creation time."""
    date_original = ''
    
    if os.path.isfile(p_path):
        try:
            with open(p_path, 'rb') as img:
                exif_tags = exifread.process_file(img)
                date_original = str(exif_tags.get('EXIF DateTimeOriginal', ''))
                if date_original:
                    date_original = date_original.split(' ')[0]
        except (KeyError, Exception):
            pass

    if not date_original.strip():
        file_attr = os.stat(p_path)
        if stat.S_ISREG(file_attr.st_mode):
            date_original = datetime.fromtimestamp(file_attr.st_ctime)
            date_original = date_original.strftime('%Y:%m:%d')

    return date_original


def add_to_catalog(p_catalog: str, p_path: str, clean_source: bool = False, always_yes: bool = False) -> Optional[bool]:
    if not is_catalog(p_catalog):
        click.echo(f"{p_path} not yet another photo catalog")
        return False

    if os.path.isfile(p_path):
        date_original = get_photo_date(p_path)
        
        if not date_original:
            click.echo(f"Could not determine date for {p_path}")
            return False

        year, month, day = date_original.split(':')
        copy_path = os.path.join(p_catalog, year, month, day)

        if not os.path.isdir(copy_path):
            os.makedirs(copy_path, exist_ok=True)

        dest_path = os.path.join(copy_path, os.path.basename(p_path))
        
        # Check if file already exists
        if os.path.exists(dest_path):
            click.echo(f"File {os.path.basename(p_path)} already exists in catalog.")
            if not always_yes:
                if not click.confirm("Overwrite?"):
                    return False
        
        shutil.copy(p_path, dest_path)
        click.echo(f"Copied {p_path} to {dest_path}")

        if clean_source:
            if always_yes or click.confirm(f"Delete source file {p_path}?"):
                os.remove(p_path)
                click.echo(f"Deleted {p_path}")

    else:  # directory, call import
        import_to_catalog(p_catalog, p_path, clean_source, always_yes)


def import_to_catalog(p_catalog: str, p_path: str, clean_source: bool = False, always_yes: bool = False) -> None:
    if os.path.isdir(p_path):
        file_list = os.listdir(path=p_path)
        for file_name in file_list:
            file_name_full = os.path.join(p_path, file_name)
            if os.path.isfile(file_name_full):
                add_to_catalog(p_catalog, file_name_full, clean_source, always_yes)
            elif os.path.isdir(file_name_full):
                import_to_catalog(p_catalog, file_name_full, clean_source, always_yes)
    else:  # regular file, add to catalog
        add_to_catalog(p_catalog, p_path, clean_source, always_yes)


@click.group()
@click.version_option(version='0.1-alpha', prog_name='yapc')
def cli() -> None:
    """Yet Another Photo Catalog - Organize photos by EXIF capture date."""
    pass


@cli.command()
@click.argument('catalog_path', type=click.Path())
def create(catalog_path: str) -> None:
    """Create a new photo catalog at CATALOG_PATH."""
    create_catalog(catalog_path)


@cli.command()
@click.argument('catalog_path', type=click.Path())
@click.argument('file_path', type=click.Path())
@click.option('-d', '--del', 'clean_source', is_flag=True, help='Delete source file after adding')
@click.option('-y', '--yes', 'always_yes', is_flag=True, help='Answer yes to all prompts')
def add(catalog_path: str, file_path: str, clean_source: bool, always_yes: bool) -> None:
    """Add a photo file to the catalog."""
    add_to_catalog(catalog_path, file_path, clean_source, always_yes)


@cli.command()
@click.argument('catalog_path', type=click.Path())
@click.argument('folder_path', type=click.Path())
@click.option('-d', '--del', 'clean_source', is_flag=True, help='Delete source files after importing')
@click.option('-y', '--yes', 'always_yes', is_flag=True, help='Answer yes to all prompts')
def import_photos(catalog_path: str, folder_path: str, clean_source: bool, always_yes: bool) -> None:
    """Import photos from a folder into the catalog."""
    import_to_catalog(catalog_path, folder_path, clean_source, always_yes)


if __name__ == '__main__':
    cli()
