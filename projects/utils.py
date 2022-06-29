

# Author: Pablo Gomez
# Some functions to utilize in the views of Projecto Color Backend

from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

def doc_valid(doc):
    try:
        FileExtensionValidator(allowed_extensions=['docx', 'pdf', 'odt'])(doc)
        return True
    except ValidationError:
        return False

def img_valid(image):
    try:
        # Image.init()
        # print([ext.lower()[1:] for ext in Image.EXTENSION])
        FileExtensionValidator(allowed_extensions=['png', 'bmp', 'apng', 'jpg', 'jpeg', 'webp'])(image)
        return True
    except ValidationError:
        return False

def edit_model_data(instance, data):
    instance_keys = list(instance.__dict__)
    keys = data.keys()
    print(instance_keys)

    for key in keys:
        if key not in instance_keys:
            print(f'ERROR: \'{key}\' attribute is not valid.')
            continue
            # raise KeyError(f'ERROR: \'{key}\' attribute is not valid.', key)
        try:
            if data.get(key) != '':
                print(data.get(key))
                setattr(instance, key, data.get(key))
            else:
                print(f'ERROR: \'{key}\' field is empty.')
        except TypeError:
            continue

    return instance

def edit_model_files(instance, files):
    instance_keys = list(instance.__dict__)

    for key in files:
        if key not in instance_keys:
            print(f'ERROR: {key} attribute is not valid.')
            continue
            # raise KeyError(f'ERROR: {key} attribute is not valid.')
        if img_valid(files[key]) or doc_valid(files[key]):
            setattr(instance, key, files[key])
            print(f'value: {files[key]}')
        else:
            print(f'ERROR: {files[key]} is not an Image or Doc file.')
            # raise ValidationError(f'ERROR: {files[key]} is not an Image file.')

    return instance