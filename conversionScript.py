from pathlib import os
# from wand.image import Image as wi
import sys, json, asyncio
import logging
import zipfile
import tarfile
from pdf2image import convert_from_path
from PIL import Image

async def main():
    source = sys.argv[1]
    namelist = []
    if zipfile.is_zipfile(source):
        print("Input is a zip file")
        archive = zipfile.ZipFile(source, "r")
        print(archive.infolist())
        namelist = [name for name in archive.namelist() if not name.startswith("__MACOSX")]
    elif tarfile.is_tarfile(source):
        print("Input is a tar file")
        archive = tarfile.TarFile(source, "r")
        namelist = [name for name in archive.getnames() if not name.startswith("__MACOSX")]

    if len(namelist) < 1:
        if os.path.isdir(sys.argv[1]):
            await convertDirectory(sys.argv[1])
        elif os.path.isfile(sys.argv[1]):
            await convertToTiff(sys.argv[1])
        else:
            logging.warning("Invalid file")
    else:
        for content in namelist:
            if os.path.isdir(content):
                await convertDirectory(content)
            elif os.path.isfile(content):
                await convertToTiff(content)
            else:
                logging.warning("Invalid file")


async def convertDirectory(dirPath,):
    fileList = os.listdir(dirPath)
    try:
        for file in fileList:
            await convertToTiff(file)
            print("Directory Conversion Complete")
    except Exception as e:
        logging.warning('Error in Converting Directory: {}'.format(e))


async def convertToTiff(inputFile):
    try:
        print("***FileName: %s***" % open(inputFile).name)
        # with wi(filename="UAN-PAN-error.pdf", resolution=200) as wiFile:
        #     print('pages = ', len(wiFile.sequence))
        #     imageList = wiFile.convert("tiff")
        #     imageList.save(filename="sample.tiff")

        #     for (img, i) in enumerate(imageList.sequence):
        #         with wi(image=img) as page:
        #             page.save(filename=i+".tiff")
        basename = os.path.basename(inputFile)
        filename, file_extension = os.path.splitext(basename)
        if file_extension.lower() == '.pdf':
            pages = convert_from_path(inputFile)
            total_pages = len(pages)
            for i, page in enumerate(pages):
                page.save('conversions/%s_%d_of_%d.tiff' %(filename, i+1, total_pages), 'tiff')
        else:
            im = Image.open(inputFile)
            im.save('conversions/%s.tiff' %filename, 'tiff')

        print("**File Translation complete**\n")
    except Exception as e:
        logging.warning('Error in Coverting File: {}'.format(e))


if __name__ == '__main__':
     loop = asyncio.get_event_loop()
     loop.run_until_complete(main())
