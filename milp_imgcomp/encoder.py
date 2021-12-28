import rans.rANSCoder as rANS
import numpy as np

def encode_to_file(levels, output_file):
    ransCoder = rANS.Encoder()
    
    pdfs = []
    first_level = True
    for level in levels:
        pdf = encode_level(ransCoder, level, first_level)
        pdfs.append(pdf)
        first_level = False

    encoded = ransCoder.get_encoded()
    # TODO: Write encoded to file
    print("Payload size: " + str(len(encoded) * 4) + " bytes")

def encode_level(ransCoder, level, first_level):
    # Values either range from -128 to 127 or -64 to 63.
    # THe rest of this function works better on strictly positive values.
    offset = 128 if first_level else 64

    square_values = np.array([var.x + offset for var in level.flatten()], dtype=np.int16)

    # TODO: Test this using a mixture of a discritized gaussian + other prob instead.
    # This mixture could reduce model size from ~1KB per level to ~8 bytes instead probably without much loss in accuracy.
    bins = np.bincount(square_values, minlength=256 if first_level else 128)
    pdf = bins.astype(np.float32) / float(len(square_values))

    for square_value in square_values:
        ransCoder.encode_symbol(pdf, square_value)

    return pdf