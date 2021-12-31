import cv2
import glob

import encoder
import milp_model

def compress_image(path_to_image, output_file = 'out.mipi'):
    img = cv2.imread(path_to_image, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return False

    model, levels = milp_model.create_model_for_image(img)
    model.optimize()
    encoder.encode_to_file(levels, output_file)

    return True

def decode_image(path_to_image, output_file = 'out.png'):
    try:
        with open(path_to_image, 'rb') as encoded:
            pdfs, rANSDecoder = encoder.extract_file_contents(encoded)
        return True
    except FileNotFoundError:
        return False



# TODO: Write decoder.

## TODO : Remove testing code.

#print(compress_image("/home/fedor/lena_small.png"))
print(decode_image('/home/fedor/milp-image/out.mipi'))