import os
import os.path
import PIL.Image as img
import PIL.ExifTags



def getEXIF(file_path):
    file = img.open(file_path)
    data = file._getexif()


    return {
        PIL.ExifTags.TAGS[k]: v
        for k, v in data.items()
        if k in PIL.ExifTags.TAGS
    }

path = r'H:\ThesisData\Sajek_2k18\Converted'
l = list(os.walk(path))

for x in l[0][2]:
    f = getEXIF(os.path.join(path, x))
    break

