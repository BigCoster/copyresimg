This application find and copy images with resize on the fly

Settings are located in the config.ini

Application creates several folders and log file.

In the folder with the name done get processed images or images
 of a smaller resolution and in the folder with the name other get the raw images.

For support .eps - install ghostscript and pleace path to ghostscript to
 Path environment variable

How to build

for compile to exe: pyinstaller --onefile --icon=icon_file.ico app.py