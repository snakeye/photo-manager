#!/usr/bin/env python

__author__ = 'snakeye'

import argparse
import os
import mimetypes
from datetime import *
import sys
import exifread
import sqlite3
from lib import image, app, db, util
import logging

EXIF_DATE_TIME_ORIGINAL = 'EXIF DateTimeOriginal'

unix_epoch = datetime(1970, 1, 1)


def process_jpeg(database, file_path, relative_path):
    """
    Process JPEG file

    :param database:
    :type database: sqlite3.Connection
    :param file_path: Path to JPEG file
    :type file_path: str
    :param relative_path:
    :type relative_path: str
    :return:
    :rtype: bool
    """
    global unix_epoch

    with open(file_path, 'rb') as fh:

        statinfo = os.stat(file_path)

        try:
            tags = exifread.process_file(fh)
        except UnicodeEncodeError, e:
            return False

        try:
            if EXIF_DATE_TIME_ORIGINAL not in tags:
                raise ValueError
            mtime = datetime.strptime(str(tags[EXIF_DATE_TIME_ORIGINAL]), '%Y:%m:%d %H:%M:%S')
        except ValueError, e:
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

        lat, lon = image.get_exif_location(tags)

        sql = 'INSERT INTO photos' \
              + ' (path, dt, size, lat, lon)' \
              + ' VALUES ("%s", %d, %d, %s, %s)' % (relative_path,
                                                    (mtime - unix_epoch).total_seconds(),
                                                    statinfo.st_size,
                                                    str(lat) if lat else 'NULL',
                                                    str(lon) if lon else 'NULL')

        try:
            database.execute(sql)
            database.commit()
        except sqlite3.IntegrityError as e:
            return False

    return True


if __name__ == "__main__":

    # load application config
    app.load_config()

    # init logger
    app.init_logger('update_db')

    # parse command line
    parser = argparse.ArgumentParser(description='Update photo database')
    parser.add_argument('archive', help='Directory with photo archive', type=str, nargs='?',
                        default=app.config.get('photos', 'archive_dir'))
    parser.add_argument('-d', '--database', help='Directory with photos database', type=str,
                        default=app.config.get('photos', 'database_dir'))
    args = parser.parse_args()

    source_dir = args.archive
    database_dir = args.database

    database = db.init(database_dir)

    skip_files = ['.DS_Store']

    for subdir, dirs, files in os.walk(source_dir):
        if util.is_dir_hidden(os.path.relpath(subdir, source_dir)):
            continue

        for file in files:

            if file in skip_files:
                continue

            full_path = os.path.join(subdir, file)
            relative_path = os.path.relpath(full_path, source_dir)

            (mime_type, encoding) = mimetypes.guess_type(full_path)

            if mime_type == 'image/jpeg':
                process_jpeg(database, full_path, relative_path)
            else:
                logging.warning("%s unknown mime type: %s" % (relative_path, mime_type))

            sys.stdout.write('.')
            sys.stdout.flush()

    print

    database.close()
