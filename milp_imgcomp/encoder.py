import rans.rANSCoder as rANS
import numpy as np
import distr_model

def encode_to_file(levels, output_file):
    ransCoder = rANS.Encoder()
    
    pdf_payloads = []

    for i, level in enumerate(levels):
        payload = encode_level(level, i, ransCoder)
        pdf_payloads.append(payload)

    encoded = ransCoder.get_encoded()
    # TODO: Write encoded, model parameters, and meta data to file

    print("Payload size: " + str(len(encoded) * 4) + " bytes" )

def encode_level(level, i, ransCoder):
    pdf, payload = distr_model.create_model(level, i)

    offset = distr_model.TOP_LEVEL_N if i == 0 else distr_model.N
    square_values = np.array([var.x + offset for var in level.flatten()], dtype=np.int16)

    for square_value in square_values:
        ransCoder.encode_symbol(pdf, square_value)

    return payload