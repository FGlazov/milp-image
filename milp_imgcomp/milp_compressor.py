import cv2
import glob
import milp_model


def compress_image(path_to_image):
    img = cv2.imread(path_to_image, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return False

    model = milp_model.create_model_for_image(img)
    model.optimize()
    return True


## TODO : Remove testing code.

print(glob.glob("../../*"))
print(compress_image("/home/fedor/lena_small.png"))
