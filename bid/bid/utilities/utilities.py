import secrets
import os
from PIL import Image

from bid import app


def save_picture(form_picture):
    """
    Save picture to directory created in location 'static/pics'
    :param form_picture:
    :return:
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
