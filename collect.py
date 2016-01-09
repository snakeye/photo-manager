__author__ = 'snakeye'

import argparse
import os
import mimetypes
from datetime import *
import sys
import exifread
# import struct
# import imghdr
# import jpeg
import sqlite3
import logging
from exif import gps

EXIF_DATE_TIME_ORIGINAL = 'EXIF DateTimeOriginal'

epoch = datetime(1970, 1, 1)


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
    global epoch

    with open(file_path, 'rb') as fh:

        statinfo = os.stat(file_path)

        try:
            tags = exifread.process_file(fh)
        except UnicodeEncodeError, e:
            return False

        # for tag in tags.keys():
        #     if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
        #         print tag, tags[tag]

        try:
            if EXIF_DATE_TIME_ORIGINAL not in tags:
                raise ValueError
            mtime = datetime.strptime(str(tags[EXIF_DATE_TIME_ORIGINAL]), '%Y:%m:%d %H:%M:%S')
        except ValueError, e:
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

        lat, lon = gps.get_lat_lon(tags)

        sql = 'INSERT INTO photos' \
              + ' (path, dt, size, lat, lon)' \
              + ' VALUES ("%s", %d, %d, %s, %s)' % (relative_path,
                                                    (mtime - epoch).total_seconds(),
                                                    statinfo.st_size,
                                                    str(lat) if lat else 'NULL',
                                                    str(lon) if lon else 'NULL')

        try:
            database.execute(sql)
            database.commit()
        except sqlite3.IntegrityError as e:
            return False

    return True


def split_path(path):
    """
    Split path into a list
    :param path: path
    :type path: str
    :return: path parts
    :rtype: list
    """
    dirname = path
    path_parts = []
    while True:
        dirname, leaf = os.path.split(dirname)
        if (leaf):
            path_parts = [leaf] + path_parts  # Adds one element, at the beginning of the list
        else:
            # Uncomment the following line to have also the drive, in the format "Z:\"
            # path_split = [dirname] + path_split
            break;
    return path_parts


def is_dir_hidden(path):
    relative_dir = split_path(path)
    for dirname in relative_dir:
        if dirname[0] == '.':
            return True
    return False


if __name__ == "__main__":

    # parse command line
    parser = argparse.ArgumentParser(description='Collect photos')
    parser.add_argument('directory', help='Directory with photos', type=str)
    args = parser.parse_args()

    source_dir = args.directory

    database = sqlite3.connect(os.path.join(source_dir, 'data', 'photos.db'))

    skip_files = ['.DS_Store']

    for subdir, dirs, files in os.walk(source_dir):

        if is_dir_hidden(os.path.relpath(subdir, source_dir)):
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
                #logging.warning("%s unknown mime type: %s" % (relative_path, mime_type))
                pass

            sys.stdout.write('.')
            sys.stdout.flush()

    print

    database.close()
