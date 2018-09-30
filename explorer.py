import math
import flickr_api
import flickr_api.flickrerrors
import logging


class Photo:
    def __init__(self, photo, exif):
        self.data = photo
        self.exif = exif

    def hasGpsData(self):
        return 'GPSLatitude' in self.exif or 'GPS GPSLatitude' in self.exif

class FlickrUserExplorer:

    # url: url to user's profile
    def __init__(self, url):
        self.user = flickr_api.Person.findByUrl(url)
        self.discovered_photos = []

    # Find all photos in the user's page
    # if end_page is not provided, all pages will be explored, starting from start_page
    def findPhotos(self, start_page= 1, end_page= 99999):
        # Used to detect if the last page has already been reached
        last_page_photo_id = -1
        all_photos = []

        page_no = start_page

        # loop until the last photo page is found
        while True:
            photos = self.user.getPhotos(page=page_no)

            if last_page_photo_id == photos[0].id or page_no > end_page:
                break

            logging.info('Exploring page {}, Photos found: {}'.format(page_no, len(photos)))

            last_page_photo_id = photos[0].id
            all_photos.extend(photos)
            page_no += 1

        logging.info('Total {} photos found'.format(len(all_photos)))

        return all_photos

    # Find all photos in the user's page
    # if end_page is not provided, all pages will be explored, starting from start_page
    def findPhotosWithGeoTag(self, start_page=1, end_page=9999):
        photos = self.findPhotos(start_page, end_page)
        photos = photos[:5] # todo remove, added only for debugging

        logging.info('Retrieving exif data of found photos')
        exifs = [self._retrieveExifData(x) for x in photos]

        filtered = []

        for item in zip(photos, exifs):
            photo = Photo(item[0], item[1])

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