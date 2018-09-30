from multiprocessing.pool import ThreadPool
import logging
import os.path
import sys


def generateFileName(photo):
    # title = photo.data.title
    # title = ''.join(x for x in title if x.isalnum() or x == ' ')
    # return '{}-{}.jpg'.format(photo.data.id, title)
    return '{}.jpg'.format(photo.data.id)

class PhotoDownloader:

    def __init__(self, export_path, max_threads= 4):
        self.export_path = export_path
        self.MAX_THREADS = max_threads

        self.total_downloaded = 0
        self.total_download_fails = 0

    # takes a lit of Photo objects and downloads them concurrently
    def downloadPhotos(self, photos):
        logging.info('Downloading photos, total: {}'.format(len(photos)))

        thread_pool = ThreadPool(processes=self.MAX_THREADS)
        thread_pool.map(self.downloadPhoto, photos)
        thread_pool.close()
        thread_pool.join()

        # process summary
        logging.info('Download finished!')
        logging.info('Total downloaded: {}'.format(self.total_downloaded))
        logging.info('Total downloaded fails: {}'.format(self.total_download_fails))


    def downloadPhoto(self, photo):
        name = generateFileName(photo)
        save_to = os.path.join(self.export_path, name)

        if os.path.isdir(save_to):
            logging.warn('Attempting to overwrite file: {}'.format(save_to))

        try:
            logging.info('Downloading: photo {}'.format(photo.data.id))
            photo.data.save(save_to)
            self.total_downloaded+= 1
            logging.info('Download finished: photo {}'.format(photo.data.id))
        except:
            self.total_download_fails+= 1
            logging.error('Failed to save photo {} to file: {}'.format(photo.data.id, sys.exc_info()[0]))


