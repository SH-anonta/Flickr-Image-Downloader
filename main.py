import flickr_api
import logging
import os
import explorer


def initializeFlickrAPI():
    api_key = 'f5fc9ccc5de725609c3696947fef7413'
    api_secret = '7845ccc1869642ca'
    flickr_api.set_keys(api_key=api_key, api_secret=api_secret)

def configureLogging(export_path):
    # Logs will be sent to console and a file
    log_file_path = os.path.join(export_path, 'flick_loader.log')
    logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler())

if __name__ == '__main__':
    initializeFlickrAPI()
    configureLogging('logs')

    url = 'https://www.flickr.com/photos/mrkotek/'

    hunter = explorer.FlickrUserExplorer(url)

    photos = hunter.findPhotosWithGeoTag(1, 1)



