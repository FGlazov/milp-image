import rans.rANSCoder as rANS
import numpy as np
import distr_model

def encode_to_file(levels, output_file):
    ransCoder = rANS.Encoder()
    
    pdfs = []
    first_level = True
    for level in levels:
        pdf = encode_level(ransCoder, level, first_level)
        pdfs.append(pdf)
        first_level = False

    encoded = ransCoder.get_encoded()
    # TODO: Write encoded, model parameters, and meta data to file

    print("Payload size: " + str(len(encoded) * 4) + " bytes")

def encode_level(ransCoder, level, first_level):
    # Values either range from -128 to 127 or -64 to 63.
    # The rest of this function works better on strictly positive values.
    # TODO: Get rid of these magic numbers.
    offset = 128 if first_level else 64

    square_values = np.array([var.x + offset for var in level.flatten()], dtype=np.int16)

    if len(level) > 1:
        pdf = distr_model.create_approx_pdf(level, first_level)
    else:
        the_value = int(level.flatten()[0].x)
        pdf = [0] * 128 
        pdf[the_value + offset] = 1

    for square_value in square_values:
        ransCoder.encode_symbol(pdf, square_value)

    return pdf