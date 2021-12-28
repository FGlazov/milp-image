import rans.rANSCoder as rANS
import numpy as np

def encode_to_file(levels, output_file):
    encoder = rANS.Encoder()
    for level in levels:
        encode_level(level)

    encoded = encoder.get_encoded()
    # TODO: Write encoded to file
    print("Payload size: " + str(len(encoded) * 4) + " bytes")

def encode_level(level):
    square_values = level.flatten()
    return None