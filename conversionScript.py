from pathlib import os
# from wand.image import Image as wi
import sys, json, asyncio
import logging
import zipfile
import tarfile
from pdf2image import convert_from_path
from PIL import Image
import binascii

async def main():
    try:
        await convert_to_tiff(sys.argv[1])
    except Exception as e:
        logging.warning('Error: {}'.format(e))

async def convert_to_tiff(source):
    namelist = []
    archive = {}

    if os.path.isdir(source):
        await convertDirectory(source)
    elif zipfile.is_zipfile(source):
        print("Input is a zip file")
        archive = zipfile.ZipFile(source, "r")
        namelist = [name for name in archive.namelist() if not name.startswith("__MACOSX")]

    elif tarfile.is_tarfile(source):
        print("Input is a tar file")
        archive = tarfile.TarFile(source, "r")
        namelist = [name for name in archive.getnames() if not name.startswith("__MACOSX")]
    elif os.path.isfile(source):
        await convertToTiff(source, "")
    else:
        logging.warning("Invalid file")

    # if input was a zip file, and zip consisted of files, namelist will be > 0
    if len(namelist) > 0:
        # create an "extractions" directory and extract all files
        if not os.path.exists("extractions"):
            os.makedirs("extractions")
        archive.extractall("extractions")
        # convert each file in zip
        # TODO: Folders inside zip
        for name in namelist:
            try:
                if not name.startswith("__MACOSX") or not name.startswith(".DS_Store"):
                    await convertToTiff("extractions/"+name)
                    os.remove("extractions/"+name)
                    print(len(os.listdir('extractions')))
            except Exception as e:
                logging.warning('Error in Converting Source: {}'.format(e))

async def convertDirectory(dirPath):
    fileList = os.listdir(dirPath)
    try:
        for file in fileList:
            await convertToTiff(file, dirPath+"/")
            print("Directory Conversion Complete")
    except Exception as e:
        logging.warning('Error in Converting Directory: {}'.format(e))

async def convertToTiff(inputFile, dirPath=""):
    if not os.path.exists("conversions"):
        os.makedirs("conversions")
    try:
        print("***FileName: %s, Directory: %s***" % (inputFile, dirPath))
        filePath = dirPath+inputFile
        basename = os.path.basename(filePath)
        print("Processing")
        filename, file_extension = os.path.splitext(basename)
        if file_extension.lower() == '.pdf':
            pages = convert_from_path(filePath)
            total_pages = len(pages)
            for i, page in enumerate(pages):
                page.save('conversions/%s_%d_of_%d.tiff' %(filename, i+1, total_pages), 'tiff')
        else:
            im = Image.open(filePath)
            im.save('conversions/%s.tiff' %filename, 'tiff')

        print("**File Translation complete**\n")
    except Exception as e:
        logging.warning('Error in Coverting File: {}'.format(e))


if __name__ == '__main__':
     loop = asyncio.get_event_loop()
     loop.run_until_complete(main())
