from os import walk, makedirs, path as ospath
from PIL import Image
from shutil import copyfile
import logging.handlers
from configparser import ConfigParser
import sys
import progressbar
import time
Image.MAX_IMAGE_PIXELS = 1700000000

# conf logging
levels = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARNING': logging.WARNING, 'ERROR': logging.ERROR}
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
formatter2 = logging.Formatter('%(message)s')
console = logging.StreamHandler()
console.setFormatter(formatter)
filehandler = logging.handlers.RotatingFileHandler('app.log', maxBytes=1048576, backupCount=5)
# filehandler = logging.handlers.TimedRotatingFileHandler('NTC1001.log', when='M', backupCount=7)

filehandler.setFormatter(formatter)
log.addHandler(console)
log.addHandler(filehandler)

log.info('Start application')

config = ConfigParser()
# def values:
config['config'] = {'log_level': 'INFO',
                    '; Доступные log_levels': ', '.join(levels.keys()),
                    'resize_to': '1600',
                    '; resize_to': 'Размер в пикселях',
                    'out_path': 'D:\Dropbox\Projects\Python\Копирование изображений\work',
                    '; out_path': 'Папка для сохранения изображений',
                    'img_path': 'D:\Dropbox\Projects\Python\Копирование изображений\images',
                    '; img_path': 'Папка с изображениями',
                    'img_names': 'filenames.txt',
                    '; img_names': 'Файл со списком названий изображений в utf-8.\
                     Без расширений, каждое имя с новой строки'}

if not ospath.exists('config.ini'):
    log.warning('No config! It will be created with def values...')
    with open('config.ini', 'w', encoding='utf-8-sig') as configfile:
        config.write(configfile)
    sys.exit()
else:
    config.read('config.ini', encoding='utf-8-sig')
log.info('Logging level: ' + config['config']['log_level'])
log.setLevel(config['config']['log_level'])
console.setFormatter(formatter2)
filehandler.setFormatter(formatter2)
log.info('')

# список изображений
listfile = config['config']['img_names']
# папка с изображениями
path = config['config']['img_path']
# папка, куда будут скопированы файлы
outpath = config['config']['out_path']
done = '\\done\\'
other = '\\other\\'
# размер по большей стороне
MAX_SIZE = int(config['config']['resize_to'])
# екстеншены, которые будем ресайзить в первую очередь
extensions1 = ('jpg', 'jpeg')
# полный список поддерживаемых
extensions = ('tif', 'tiff', 'png', 'bmp', 'gif', 'jpg', 'jpeg')

basedir = ospath.abspath(ospath.dirname(__file__)) + '\\'
# получить список изображений из файла
listnames = tuple()
try:
    file = open(listfile, 'r', encoding='utf-8-sig')
    listnames = tuple(l.strip() for l in file if l.strip() is not '')
except Exception as msg:
    log.error(msg)
log.info('Names in ' + listfile + ': {}'.format(len(listnames)))
log.debug(' ' + '\n '.join(l for l in listnames))
log.debug('')


# найти файлы в исходной папке
# http://stackoverflow.com/a/5817256
log.info('Searching all files...')
files = []
for root, dirs, file in walk(path):
    for name in file:
        if name.split('.')[0] in listnames:
            files.append(ospath.join(root, name))

log.info('Found files: {}'.format(len(files)))
log.debug(' ' + '\n '.join(f for f in files))
log.debug('')

# all jpeg in list
jpeg_img = [i for i in files if i.split('.')[-1] in extensions1]
jpeg_onlynames = [n.split('\\')[-1].split('.')[0] for n in jpeg_img]


# no jpeg in list
other_img = [i for i in files
             if i.split('.')[-1]
             not in extensions1 and i.split('\\')[-1].split('.')[0]
             not in jpeg_onlynames]

files = jpeg_img + other_img
log.info('Filtered files: {}'.format(len(files)))
log.debug(' ' + '\n '.join(f for f in files))
log.debug('')

onlycopyednames = [f.split('\\')[-1].split('.')[0] for f in files]

notfound = [n for n in listnames if n not in onlycopyednames]
log.info('Not found files: {}'.format(len(notfound)))
if len(notfound):
    log.debug(' ' + '\n '.join(f for f in notfound))
log.debug('')

# создаем папку, если не существует
if not ospath.exists(outpath):
    makedirs(outpath)
if not ospath.exists(outpath + done):
    makedirs(outpath + done)
if not ospath.exists(outpath + other):
    makedirs(outpath + other)

status = {'Resized': 0, 'Not_resized': 0, 'Error_open': 0, 'Not_supported': 0, 'Err_resize': 0}
log.info('Resizing files...')
console.setFormatter(formatter)
filehandler.setFormatter(formatter)

bar = progressbar.ProgressBar(max_value=len(files),
                              # widgets=[progressbar.SimpleProgress()],
                              redirect_stdout=True)
i = 1
for file in files:
    if file.split('.')[-1] in extensions:
        try:
            image = Image.open(file)
            original_size = max(image.size[0], image.size[1])
            if original_size >= MAX_SIZE:
                if image.size[0] > image.size[1]:
                    resized_width = MAX_SIZE
                    resized_height = int(round((MAX_SIZE/float(image.size[0]))*image.size[1]))
                else:
                    resized_height = MAX_SIZE
                    resized_width = int(round((MAX_SIZE/float(image.size[1]))*image.size[0]))
                try:
                    image = image.convert("RGB").resize((resized_width, resized_height), Image.ANTIALIAS)
                    newpath = outpath + done + file.split('\\')[-1].split('.')[0] + '.jpg'
                    image.save(newpath, 'JPEG', dpi=(72, 72))
                    log.debug('Resized: ' + file.split('\\')[-1])
                    status['Resized'] += 1
                except Exception as msg:
                    newpath = outpath + other + file.split('\\')[-1]
                    image.save(newpath, 'JPEG', dpi=(72, 72))
                    log.error('Err resize: ' + file.split('\\')[-1])
                    status['Err_resize'] += 1
                    log.error(msg)
            else:
                log.debug('Not resized: ' + file.split('\\')[-1])
                status['Not_resized'] += 1
                newpath = outpath + done + file.split('\\')[-1].split('.')[0] + '.jpg'
                image.save(newpath, 'JPEG', dpi=(72, 72))
        except Exception as msg:
            log.error('Error open: ' + file.split('\\')[-1])
            status['Error_open'] += 1
            log.error(msg)
    else:
        newpath = outpath + other + file.split('\\')[-1]
        copyfile(file, newpath)
        log.warn('Not supported: ' + file.split('\\')[-1])
        status['Not_supported'] += 1
    if config['config']['log_level'] == 'INFO':
        bar.update(i)
        i += 1


console.setFormatter(formatter2)
filehandler.setFormatter(formatter2)

log.info('\n')
for key, value in status.items():
    log.info(key + ': ' + str(value))
log.info('Not found files: {}'.format(len(notfound)))
if len(notfound):
    log.warn(' ' + '\n '.join(f for f in notfound))
log.info('')
sys.exit()