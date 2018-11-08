This application find and copy images with resize on the fly

Settings are located in the config.ini

Application creates several folders and log file.

In the folder with the name done get processed images or images
 of a smaller resolution and in the folder with the name other get the raw images.
 
On some pc need install Microsoft Visual C++ 2010 Redistributable Package (x86).
File name like a vcredist_x86.exe
For support .eps - install ghostscript 32 bit and put the path to ghostscript to
 Path environment variable like a C:\Program Files (x86)\gs\gs9.25\bin

How to build

for compile to exe: pyinstaller --onefile --icon=icon_file.ico CopyResImg.py