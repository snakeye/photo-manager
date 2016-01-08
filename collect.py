__author__ = 'snakeye'

import argparse
import os
import mimetypes
from datetime import *
import sys

import pymongo
import exifread
import struct
import imghdr
import jpeg

EXIF_DATE_TIME_ORIGINAL = 'EXIF DateTimeOriginal'


def do_jpeg(source_path, db):
    with open(source_path, 'rb') as fh:

        try:
            exif_raw = exifread.process_file(fh)
        except UnicodeEncodeError, e:
            return False

        if EXIF_DATE_TIME_ORIGINAL in exif_raw:
            try:
                mtime = datetime.strptime(str(exif_raw[EXIF_DATE_TIME_ORIGINAL]), '%Y:%m:%d %H:%M:%S')
            except ValueError, e:
                mtime = datetime.fromtimestamp(os.path.getmtime(source_path))
        else:
            mtime = datetime.fromtimestamp(os.path.getmtime(source_path))

        exif = {}
        for k, v in exif_raw.iteritems():
            exif[k] = str(v)

        photo = {
            'path': source_path,
            'date': mtime,
            'exif': exif,
        }

        print photo
        exit()

        photos = db.photos
        photos.insert_one(photo)

        sys.stdout.write('.')
        sys.stdout.flush()


if __name__ == "__main__":
    # parse command line
    parser = argparse.ArgumentParser(description='Collect photos')
    args = parser.parse_args()

    client = pymongo.MongoClient('localhost', 27017)

    db = client.photos

    source_dir = '/Users/snakeye/Pictures/Photos'

    skip_files = '.DS_Store'

    for subdir, dirs, files in os.walk(source_dir):
        for file in files:

            if file in skip_files:
                continue

            source_file = os.path.join(subdir, file)

            (mime_type, encoding) = mimetypes.guess_type(source_file)

            if mime_type == 'image/jpeg':
                do_jpeg(source_file, db)
            else:
                print "{} unknown mime type: {}".format(source_file, mime_type)
