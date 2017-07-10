from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO
from django.conf import settings

import sys


def file_size(file):
    image = Image.open(file).convert('RGB')
    output = BytesIO()

    if settings.SUMMERNOTE_MAX_WIDTH:
        max_width = settings.SUMMERNOTE_MAX_WIDTH
    else:
        max_width = 600

    if image.width > max_width:
        t_ratio = round(max_width / image.width, 2)
        image_width = int(image.width * t_ratio)
        image_height = int(image.height * t_ratio)
        image = image.resize((image_width, image_height), Image.ANTIALIAS)

    image.save(output, format='JPEG', quality=60)
    output.seek(0)

    # change the imagefield value to be the newley modifed image value
    file = InMemoryUploadedFile(output, 'ImageField', file.name, 'image/jpeg', sys.getsizeof(output), None)
    return file