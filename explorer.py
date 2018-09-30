import flickr_api
from multiprocessing.pool import ThreadPool
import flickr_api.flickrerrors
import threading
import sys
import logging


class Photo:
    def __init__(self, photo):
        self.data = photo
        # sends request to flickr api
        self.exif = {}

        try:
            logging.info('Retrieving EXIF data of {}'.format(photo.id))
            self.exif = self._exifToDict(photo.getExif())
        except:
            logging.error('Failed to retrieve EXIF data of photo {}, | Error: {}'.format(photo.id, sys.exc_info()[0]))


    def hasGpsData(self):
        return 'GPSLatitude' in self.exif or 'GPS GPSLatitude' in self.exif

    def _exifToDict(self, exif):
        return {
            x.tag : x.raw
            for x in exif
        }

class FlickrUserExplorer:

    # url: url to user's profile
    def __init__(self, url, threads = 4):
        logging.info('Loading user: {}'.format(url))
        self.user = flickr_api.Person.findByUrl(url)
        logging.info('User loaded')

        self.discovered_photos = []
        self.discovered_photos_lock = threading.RLock()

        self.MAX_THREADS = threads

    # a target function for threads spawned by findPhotos method
    def _retrievePhotosFromPage(self, page_number):
        return self.user.getPhotos(page_number= page_number)


    # Find all photos in the user's page
    # if end_page is not provided, all pages will be explored, starting from start_page
    def findPhotos(self, start_page, end_page):
        if start_page > end_page:
            raise ValueError('Invalid page numbers')

        # Used to detect if the last page has already been reached
        all_photos = []

        thread_pool = ThreadPool(processes= self.MAX_THREADS)
        results = thread_pool.map(self._retrievePhotosFromPage, range(start_page, end_page+1))
        thread_pool.close()
        thread_pool.join()

        for x in results:
            all_photos.extend(x)

        # loop until the last photo page is found
        for page_no in range(start_page, end_page+1):
            photos = self.user.getPhotos(page=page_no)
            logging.info('Explored page {}, Photos found: {}'.format(page_no, len(photos)))

            page_no += 1


        logging.info('Total {} photos found'.format(len(all_photos)))

        return all_photos

    # Find all photos in the user's page
    # if end_page is not provided, all pages will be explored, starting from start_page
    def findPhotosWithGeoTag(self, start_page, end_page):
        photos = self.findPhotos(start_page, end_page)
        photos = photos[:50] # todo remove, added only for debugging

        logging.info('Retrieving exif data of found photos')

        thread_pool = ThreadPool(processes= self.MAX_THREADS)

        # maps all photo objects to Photo objects, with exif data
        photos = thread_pool.map(Photo, photos)
        thread_pool.close()
        thread_pool.join()

        filtered = []

        for photo in photos:
            if photo.hasGpsData():
                filtered.append(photo)
            else:
                logging.info('Filtering out photo {}, for not having GPS data'.format(photo.data.id))

        logging.info('Photos with GPS data found: {}'.format(len(filtered)))

        return filtered

    # Retrieves EXIF of given photo object
    # return empty dict if it fails to retrieve data
    def _retrieveExifData(self, photo):
        logging.error('Retrieving EXIF data of photo {}'.format(photo.id))

        exif = {}

        try:
            exif = photo.getExif()
            exif = self._exifToDict(exif)
        except flickr_api.flickrerrors.FlickrAPIError as e:
            logging.error('Failed to retrieve EXIF data of photo {}, | Error: {}'.format(photo.id,  e.message))

        return exif

    # Expects a dictionary containing exif data

    def _hasGPSData(self, exif):
        return 'GPSLatitude' in exif or 'GPS GPSLatitude' in exif

    def _exifToDict(self, exif):
        return {
            x.tag : x.raw
            for x in exif
        }