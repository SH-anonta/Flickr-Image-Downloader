import flickr_api
import itertools
import json
import os.path
import csv
import logging


def getLocationExif(photo):
    return photo.getExif()

class FlickLoader:

    def getUniqueFileName(self):
        self._unique_number+= 1

        return str(self._unique_number)+'.jpg'

    def __init__(self, user_name, export_to, api_key, api_secrect):

        flickr_api.set_keys(api_key=api_key, api_secret=api_secrect)

        self._unique_number = 0
        self.user = flickr_api.Person.findByUserName(user_name)
        self.export_directory = export_to

        logging.info('User has been loaded')


        csv_file = open(os.path.join(self.export_directory, 'exif.csv'), 'ab')
        self.csv = csv.DictWriter(csv_file, ('FileName', 'EXIF'))

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


        logging.info('Total {} photos discovered, proceeding to download'.format(len(all_photos)))
        self.savePhotos(all_photos, self.export_directory)

    def savePhotos(self, photos, export_to):
        for photo in itertools.islice(photos, self.resume_from-1, self.end_at):
            file_name = self.getUniqueFileName()
            file_path = os.path.join(export_to, file_name)

            logging.info('Downloading photo {}'.format(photo.id))
            photo.save(file_path)
            logging.info('Download finished, photo {} saved to {}'.format(photo.id, file_path))


            exif = photo.getExif()
            exif_data = {
                x.tag : x.raw
                for x in exif
            }

            self.csv.writerow({
                'FileName' : file_name,
                'EXIF' : json.dumps(exif_data)
            })


def test():
    pass

if __name__ == '__main__':
    start = 31
    end = 33      # none means download all
    export_path = r'F:\CollectedPhotos/'
    user_name = 'MrKotek'

    api_key = 'f5fc9ccc5de725609c3696947fef7413'
    api_secrect = '7845ccc1869642ca'

    logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    loader = FlickLoader(user_name, export_path, api_key, api_secrect)

    loader.collectAllPhotos(start, end)