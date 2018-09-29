import sys
import flickr_api
import itertools
import json
import os.path
import csv
import logging
import PIL.Image
import flickr_api.flickrerrors
import piexif

def getLocationExif(photo):
    return photo.getExif()

class FlickLoader:

    def getUniqueFileName(self):
        self._unique_number+= 1

        return str(self._unique_number)+'.jpg'

    def __init__(self, user_name, export_to, api_key, api_secret):

        flickr_api.set_keys(api_key=api_key, api_secret=api_secret)

        self._unique_number = 0
        self.user = flickr_api.Person.findByUserName(user_name)
        self.export_directory = export_to

        logging.info('User has been loaded')


        csv_file = open(os.path.join(self.export_directory, 'exif.csv'), 'wb')
        self.csv = csv.DictWriter(csv_file, ('#', 'ID', 'FileName', 'EXIF'))

    def collectAllPhotos(self, start_from = 1, end_at= None):
        """
        :param start_from: from which photo should the loader continue
        """
        # to ensure previous ly downloaded files don't get over written
        self._unique_number = start_from-1
        self.resume_from = start_from
        self.end_at = end_at

        # needed to detect if the last page of the user's photos has been reached
        last_page_photo_id = -1

        all_photos = []

        page_no = 1
        # loop until the last photo page is found
        while True:
            photos = self.user.getPhotos(page= page_no)

            if last_page_photo_id == photos[0].id:
                break

            logging.info('Visiting page {}'.format(page_no))
            last_page_photo_id= photos[0].id

            all_photos.extend(photos)
            page_no+= 1

        if end_at is None:
            self.end_at = len(all_photos)


        logging.info('Total {} photos discovered, proceeding to download photos {} to {}'.format(len(all_photos), self.resume_from, self.end_at))
        self.savePhotos(all_photos, self.export_directory)

    def createPhotoFileName(self, id, title):
        title = title.encode('ascii', 'ignore')
        title = ''.join(x for x in title if x.isalnum() or x ==' ' or x.isalnum())

        return '{}-{}.jpg'.format(str(id), title)

    def savePhotos(self, photos, export_to):
        photo_number = self.resume_from

        for photo in itertools.islice(photos, self.resume_from-1, self.end_at):
            file_name = self.createPhotoFileName(photo.id, photo.title)
            file_path = os.path.join(export_to, file_name)

            logging.info('Downloading photo #{} name:{}'.format(photo_number, file_name))

            # save the exif as json in the csv file

            try:
                exif = photo.getExif()
            except flickr_api.flickrerrors.FlickrAPIError as e:
                logging.error('Failed to get EXIF dat aof photo #{} name:{} | Error: {}'.format(photo_number, file_name, e.message))
                continue

            exif_data = {
                x.tag: x.raw
                for x in exif
            }

            if not self.hasGPSData(exif_data):
                # if the photo does not have GPS skip downloading it
                logging.info('Skipping photo #{}, {} because GPS data is unavailable'.format(photo_number, file_name))
                continue

            try:
                photo.save(file_path)
            except Exception as e:
                logging.error('Failed to download {} : Error {}'.format(file_name, e.message))
            else:
                logging.info('Download finished, photo {} saved to {}'.format(photo.id, file_path))

            # write to csv after downloading
            self.csv.writerow({
                '#' : photo_number,
                'ID' : photo.id,
                'FileName' : file_name,
                'EXIF' : json.dumps(exif_data)
            })

            photo_number+= 1

    def hasGPSData(self, exif):
        return 'GPSLatitude' in exif



def retrieveParams():
    # export path, start from, end at,
    return sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]),

if __name__ == '__main__':
    user_name, export_path, start, end = retrieveParams()

    # end should be < 0 if the user wats to download all photos
    if end < 0:
        end = None

    print user_name, export_path, start, end

    api_key = 'f5fc9ccc5de725609c3696947fef7413'
    api_secret = '7845ccc1869642ca'

    # Logs will be sent to console and a file
    log_file_path = os.path.join(export_path, 'app.log')
    logging.basicConfig(filename= log_file_path, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler())

    loader = FlickLoader(user_name, export_path, api_key, api_secret)
    loader.collectAllPhotos(start, end)