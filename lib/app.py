import ConfigParser
import logging

config = None


def load_config(path='config/app.cfg'):
    global config
    config = ConfigParser.ConfigParser({
        'database_dir': '%(archive_dir)s'
    })
    config.read(path)


def init_logger(log_name):
    global config
    log_dir = config.get('directories', 'log')
    logging.basicConfig(filename=log_dir + '/' + log_name + '.log',
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)
