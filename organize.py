#!/usr/bin/env python

__author__ = 'snakeye'

import logging
import argparse
import os
import mimetypes
from lib import app, image, util


def move_file(source_path, target_root, organize_by_date=False, fix_extension=False, mime_type=None):
    """
    Move file to archive directory

    :param source_path:
    :param target_root:
    :param mime_type:
    :return:
    :rtype: bool
    """

    # form target directory path
    if organize_by_date:
        mtime = image.get_original_timestamp(source_path)
        target_dir = os.path.join(target_root, mtime.strftime('%Y/%m/%d'))
    else:
        target_dir = target_root

    # create target directory if not exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # create file name
    source_basename = os.path.basename(source_path)

    if fix_extension and mime_type != None:
        target_basename = os.path.splitext(source_basename)[0]
        target_basename += mimetypes.guess_extension(mime_type, False)
    else:
        target_basename = source_basename

    # create full path to target file
    target_path = os.path.join(target_dir, target_basename)

    # move file
    os.rename(source_path, target_path)

    # log result
    logging.info('Copied %s to %s' % (source_path, target_path))

    return True


if __name__ == "__main__":
    # load application config
    app.load_config()

    # init logger
    app.init_logger('organize')

    # parse command line
    parser = argparse.ArgumentParser(description='Organize photos')
    args = parser.parse_args()

    mimetypes.init()

    # add mime type for raw images
    mimetypes.add_type('image/raw', '.CR2')

    # skip files with names
    skip_files = ['.DS_Store']

    # mime type definitions
    archive_types = ['image/jpeg', 'image/raw']
    other_types = ['image/png', 'image/tiff']
    video_types = ['video/quicktime', 'video/mp4', 'video/x-m4v', 'video/x-msvideo']

    source_dir = app.config.get('directories', 'unsorted')

    for subdir, dirs, files in os.walk(source_dir):

        # skip hidden directoires
        if util.is_dir_hidden(os.path.relpath(subdir, source_dir)):
            continue

        # process all files
        for file in files:

            # skip some files
            if file in skip_files:
                continue

            # combine full path to file
            source_file = os.path.join(subdir, file)

            # guess file type
            (mime_type, encoding) = mimetypes.guess_type(source_file)

            if mime_type in archive_types:
                move_file(source_file, app.config.get('directories', 'photos'), organize_by_date=True)
            elif mime_type == 'image/gif':
                move_file(source_file, app.config.get('directories', 'gif'))
            elif mime_type in other_types:
                move_file(source_file, app.config.get('directories', 'other'))
            elif mime_type in video_types:
                move_file(source_file, app.config.get('directories', 'video'))
            else:
                logging.warning("File %s has unknown mime type: %s" % (source_file, mime_type))
