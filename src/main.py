import flickr_api
import logging
import json
import os
import csv

import explorer
import downloader

def initializeFlickrAPI():
    api_key = 'f5fc9ccc5de725609c3696947fef7413'
    api_secret = '7845ccc1869642ca'
    flickr_api.set_keys(api_key=api_key, api_secret=api_secret)

def configureLogging(export_path):
    # Logs will be sent to console and a file
    log_file_path = os.path.join(export_path, 'flick_loader.log')
    logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler())


# Takes a path to a folder which will contain the csv file
# and a list of Photo objects
def exportPhotoDataToCsv(export_path, photos):
    file_path = os.path.join(export_path, 'data.csv')

    csv_fields = ('ID','FileName','EXIF')
    with open(file_path, 'wb') as f:
        writer = csv.DictWriter(f, csv_fields)

        for photo in photos:
            writer.writerow({
                "ID": photo.data.id,
                "FileName" : downloader.generateFileName(photo),
                "EXIF" : json.dumps(photo.exif)
            })

# create a directory if it does not exist already
def createDirectory(path):
    if not os.path.isdir(path):
        os.mkdir(path)

if __name__ == '__main__':
    url = 'https://www.flickr.com/photos/mrkotek/'

    folder_name = 'TEST'
    export_path = r'G:\Flickr'
    export_path = os.path.join(export_path, folder_name)
    createDirectory(export_path)

    initializeFlickrAPI()
    configureLogging(export_path)

    # 90
    start_page = 1
    end_page   = 1

    logging.info('-------------------Start-------------------')
    logging.info('Attempting to download photos from page {} to {}'.format(start_page, end_page))

    explorer = explorer.FlickrUserExplorer(url, 20)
    photos = explorer.findPhotosWithGeoTag(start_page, end_page)


    exportPhotoDataToCsv(export_path, photos)

    photo_path = os.path.join(export_path, 'photos')
    createDirectory(photo_path)

    download = downloader.PhotoDownloader(photo_path, 8)
    download.downloadPhotos(photos)



