__author__ = 'snakeye'

import argparse
import os
import mimetypes
from datetime import datetime
import exifread

EXIF_DATE_TIME_ORIGINAL = 'EXIF DateTimeOriginal'


def do_jpeg(source_path, target_root):
    with open(source_path, 'rb') as fh:

        try:
            tags = exifread.process_file(fh)
        except UnicodeEncodeError, e:
            return False

        # for tag, value in tags.iteritems():
        #     print "{}:\t{}".format(tag, value)

        source_name = os.path.basename(source_path)
        dir_name = os.path.basename(os.path.dirname(source_path))

        #

        #
        if EXIF_DATE_TIME_ORIGINAL in tags:
            try:
                mtime = datetime.strptime(str(tags[EXIF_DATE_TIME_ORIGINAL]), '%Y:%m:%d %H:%M:%S')
            except ValueError, e:
                mtime = datetime.fromtimestamp(os.path.getmtime(source_path))
        else:
            mtime = datetime.fromtimestamp(os.path.getmtime(source_path))

        #
        target_name = os.path.splitext(source_name)[0]

        #
        dir = dir_name.split(',')
        if len(dir) > 1:
            dir.pop()
            target_name += ' - ' + ', '.join(dir)

        target_name += '.jpeg'

        #
        target_dir = os.path.join(target_root, mtime.strftime('%Y/%m/%d'))

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        target_path = os.path.join(target_dir, target_name)

        print(source_path, target_path)
        os.rename(source_path, target_path)

    return True


def do_raw(source_path, target_root):
    with open(source_path, 'rb') as fh:
        try:
            tags = exifread.process_file(fh)
        except UnicodeEncodeError, e:
            return False

        source_name = os.path.basename(source_path)
        dir_name = os.path.basename(os.path.dirname(source_path))

        #
        if EXIF_DATE_TIME_ORIGINAL in tags:
            try:
                mtime = datetime.strptime(str(tags[EXIF_DATE_TIME_ORIGINAL]), '%Y:%m:%d %H:%M:%S')
            except ValueError, e:
                mtime = datetime.fromtimestamp(os.path.getmtime(source_path))
        else:
            mtime = datetime.fromtimestamp(os.path.getmtime(source_path))

        #
        target_name = os.path.splitext(source_name)[0]

        #
        dir = dir_name.split(',')
        if len(dir) > 1:
            dir.pop()
            target_name += ' - ' + ', '.join(dir)

        target_name += '.CR2'

        #
        target_dir = os.path.join(target_root, mtime.strftime('%Y/%m/%d'))

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        target_path = os.path.join(target_dir, target_name)

        print(source_path, target_path)
        os.rename(source_path, target_path)


def do_gif(source_path, target_root):
    source_name = os.path.basename(source_path)
    target_name = os.path.splitext(source_name)[0] + '.gif'

    #
    if not os.path.exists(target_root):
        os.makedirs(target_root)

    target_path = os.path.join(target_root, target_name)

    print(source_path, target_path)
    os.rename(source_path, target_path)


def do_video(source_path, target_root):
    source_name = os.path.basename(source_path)
    target_name = source_name

    #
    if not os.path.exists(target_root):
        os.makedirs(target_root)

    target_path = os.path.join(target_root, target_name)

    print(source_path, target_path)
    os.rename(source_path, target_path)


if __name__ == "__main__":
    # parse command line
    parser = argparse.ArgumentParser(description='Sort photos')
    args = parser.parse_args()

    mimetypes.init()

    source_dir = '/Volumes/Data/Pictures/Unsorted'
    target_dir = '/Volumes/Data/Pictures/Photos'
    gif_dir = '/Users/snakeye/Pictures/GIF'
    video_dir = '/Users/snakeye/Pictures/Videos'

    video_types = ['video/quicktime', 'video/mp4', 'video/x-m4v', 'video/x-msvideo']

    skip_files = '.DS_Store'

    for subdir, dirs, files in os.walk(source_dir):
        for file in files:

            if file in skip_files:
                continue

            source_file = os.path.join(subdir, file)

            (mime_type, encoding) = mimetypes.guess_type(source_file)

            if mime_type == 'image/jpeg':
                do_jpeg(source_file, target_dir)
            elif mime_type == 'image/gif':
                #do_gif(source_file, gif_dir)
                pass
            elif mime_type in video_types:
                #do_video(source_file, video_dir)
                pass
            else:
                filename, file_extension = os.path.splitext(file)
                if file_extension == '.CR2':
                    do_raw(source_file, target_dir)

                print "{} unknown mime type: {}".format(source_file, mime_type)
