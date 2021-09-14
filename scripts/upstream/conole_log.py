import os
import logging
import time
from logging import Handler, FileHandler, StreamHandler
import yaml

class PathFileHandler(FileHandler):
    def __init__(self, path, filename, mode='a+', encoding='UTF-8', delay=False):
        if not os.path.exists(path):
            os.mkdir(path)
        self.baseFilename = os.path.join(path, filename)
        self.mode = mode
        self.encoding = encoding
        self.delay = delay
        if delay:
            Handler.__init__(self)
            self.stream = None
        else:
            StreamHandler.__init__(self, self._open())


class Loggers(object):
    # 日志级别关系映射
    level_relations = {
        'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING,
        'error': logging.ERROR, 'critical': logging.CRITICAL
    }

    def __init__(self, path, filename='{date}.log'.format(date=time.strftime("%Y-%m-%d_%H%M", time.localtime())), level='info', log_dir='log',
                 fmt='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)

        self.directory = os.path.join(path, log_dir)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别
        stream_handler = logging.StreamHandler()  # 往屏幕上输出
        stream_handler.setFormatter(format_str)
        file_handler = PathFileHandler(path=self.directory, filename=filename, mode='a+')
        file_handler.setFormatter(format_str)
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)


class ConfigFile(object):
    def __init__(self, path, filename='config.yaml'):
        self.directory = path
        self.configfile = os.path.join(self.directory, filename)
        PathFileHandler(path=self.directory, filename=filename, mode='a+')

    def FulshConfig(self):
        while True:
            self.params = None
            while self.params == None:
                self.params = yaml.load(open(self.configfile), Loader=yaml.FullLoader)

    def SetConfig(self, dataset, **srr):
        self.dataset = dataset
        self.params[dataset] = self.dataset
        # up config
        with open(self.params, 'w', encoding="utf-8") as nf:
            yaml.dump(self.params, nf)
        self.FulshConfig()

