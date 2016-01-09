import os


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
    """
    Checks if the path have hidden subdirectories
    :param path:
    :type path: str
    :return:
    :rtype: bool
    """
    relative_dir = split_path(path)
    for dirname in relative_dir:
        if dirname[0] == '.':
            return True
    return False
