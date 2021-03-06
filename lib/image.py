import exifread
from datetime import *
import os


def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None


def _convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format

    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m / 60.0) + (s / 3600.0)


def get_exif(path):
    """
    Get EXIF data from the file
    :param path:
    :return:
    """
    with open(path, 'rb') as fh:
        try:
            exif_data = exifread.process_file(fh)
        except UnicodeEncodeError, e:
            return {}

        return exif_data


def get_original_timestamp(path):
    exif_data = get_exif(path)
    try:
        if 'EXIF DateTimeOriginal' not in exif_data:
            raise ValueError()
        mtime = datetime.strptime(str(exif_data['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S')
    except ValueError, e:
        mtime = datetime.fromtimestamp(os.path.getmtime(path))

    return mtime


def get_exif_location(exif_data):
    """
    Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)
    """
    lat = None
    lon = None

    gps_latitude = _get_if_exist(exif_data, 'GPS GPSLatitude')
    gps_latitude_ref = _get_if_exist(exif_data, 'GPS GPSLatitudeRef')
    gps_longitude = _get_if_exist(exif_data, 'GPS GPSLongitude')
    gps_longitude_ref = _get_if_exist(exif_data, 'GPS GPSLongitudeRef')

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = _convert_to_degress(gps_latitude)
        if gps_latitude_ref.values[0] != 'N':
            lat = 0 - lat

        lon = _convert_to_degress(gps_longitude)
        if gps_longitude_ref.values[0] != 'E':
            lon = 0 - lon

    return lat, lon
