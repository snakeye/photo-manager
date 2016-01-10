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


def process_photo(database, file_path, relative_path, mime_type):
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

        tags = image.get_exif(file_path)

        mtime = image.get_original_timestamp(file_path)

        lat, lon = image.get_exif_location(tags)

        try:
            width = int(str(tags['EXIF ExifImageWidth']))
            height = int(str(tags['EXIF ExifImageLength']))
        except:
            width = 0
            height = 0

        sql = 'INSERT INTO photos' \
              + ' (path, dt, size, lat, lon, width, height, mime)' \
              + ' VALUES ("%s", %d, %d, %s, %s, %d, %d, "%s")' \
                % (relative_path,
                   (mtime - unix_epoch).total_seconds(),
                   statinfo.st_size,
                   str(lat) if lat else 'NULL',
                   str(lon) if lon else 'NULL',
                   width,
                   height,
                   mime_type)

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
    args = parser.parse_args()

    mimetypes.init()

    # add mime type for raw images
    mimetypes.add_type('image/raw', '.CR2')

    # directories
    source_dir = app.config.get('directories', 'photos')
    database_file = app.config.get('database', 'file')

    database = db.init(database_file)

    # 1. check for deleted files
    print 'Check for deleted files'

    cursor = db.fetch('SELECT id, path FROM photos')
    for row in cursor.fetchall():
        if not os.path.exists(os.path.join(source_dir, row[1])):
            db.get_conn().execute('DELETE FROM photos WHERE id = ?', row[0])
            sys.stdout.write('X')
        else:
            sys.stdout.write('.')
        sys.stdout.flush()

    print

    db.get_conn().commit()

    # 2. add new files
    print 'Add new files'

    skip_files = ['.DS_Store']
    image_types = ['image/jpeg', 'image/raw']

    for subdir, dirs, files in os.walk(source_dir):
        if util.is_dir_hidden(os.path.relpath(subdir, source_dir)):
            continue

        for file in files:
            if file in skip_files:
                continue

            #
            full_path = os.path.join(subdir, file)
            relative_path = os.path.relpath(full_path, source_dir)

            cursor = db.fetch('SELECT * FROM photos WHERE path = "%s"' % relative_path)
            row = cursor.fetchone()

            if row == None:
                #
                (mime_type, encoding) = mimetypes.guess_type(full_path)

                if mime_type in image_types:
                    process_photo(database, full_path, relative_path, mime_type)
                    sys.stdout.write('+')
                else:
                    sys.stdout.write(' ')
            else:
                sys.stdout.write('.')

            sys.stdout.flush()

    print

    database.close()
