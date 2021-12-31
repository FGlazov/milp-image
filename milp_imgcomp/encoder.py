import rans.rANSCoder as rANS
import numpy as np
import distr_model
import math

def encode_to_file(levels, output_file):
    ransCoder = rANS.Encoder()
    
    pdf_payloads = []

    for i, level in enumerate(levels):
        payload = encode_level(level, i, ransCoder)
        pdf_payloads.append(payload)

    encoded = ransCoder.get_encoded()

    write_to_file(encoded, pdf_payloads, levels[0].shape, output_file)

def encode_level(level, i, ransCoder):
    pdf, payload = distr_model.create_model(level, i)

    offset = distr_model.TOP_LEVEL_N if i == 0 else distr_model.N
    square_values = np.array([var.x + offset for var in level.flatten()], dtype=np.int16)

    for square_value in square_values:
        ransCoder.encode_symbol(pdf, square_value)

    return payload

def write_to_file(encoded, pdf_payloads, image_shape, output_file):
    with open(output_file, 'wb') as f:
        row_bytes = image_shape[0].to_bytes(4, byteorder='big')
        f.write(row_bytes)
        # Currenlty don't save column bytes, since image is assumed to be square.

        for payload in pdf_payloads:
            # The size of the payloads are a function of image_shape, so there is no need for seperators.
            if len(payload) > 0:
                f.write(payload.tobytes())

        for word in encoded:
            f.write(word.to_bytes(4, byteorder='big'))


def extract_file_contents(encoded):
    # Currenlty don't save column bytes, since image is assumed to be square.
    row_bytes = encoded.read(4)
    rows = int.from_bytes(row_bytes, 'big')

    lvl_rows = rows
    top_lvl = True

    pdfs = []
    while lvl_rows > 0:
        lvl_size = lvl_rows * lvl_rows
        payload_size = distr_model.get_pdf_payload_size(lvl_size, top_lvl)
        pdf_payload = encoded.read(payload_size)
        pdf = distr_model.decode_pdf_payload(lvl_size, top_lvl, pdf_payload)
        pdfs.append(pdf)

        lvl_rows //= 2
        top_lvl = False
 
        print(len(pdf), pdf.sum())


    image_payload = []
    while word := encoded.read(4):
        image_payload.append(int.from_bytes(word, 'big'))
    rANSDecoder = rANS.Decoder(image_payload)

    return pdfs, rANSDecoder, rows

def reconstruct_image(pdfs, rANSDecoder, rows):
    nr_square_levels = round(math.log(rows, 2)) + 1

    i = 0
    lvl_rows = 1
    image = np.zeros([rows, rows], dtype=np.int16)    
    
    # Reverse order here - since rans decoder works in reverse order.
    while lvl_rows <= rows:
        j = nr_square_levels - i
        
        print("lvl_rows", lvl_rows, "j", j)

        lvl = np.empty([lvl_rows, lvl_rows], dtype=np.int16)
        
        offset = distr_model.N # A value in 0-127 means to add -64 to 63 to the pixel.
        if lvl_rows == rows:
            offset = 0 # Bottom most level is encoded as 0-255 already, no need to offset.

        pdf = pdfs[-(i+1)]
        for x in reversed(range(0, lvl_rows)):
            for y in reversed(range(0, lvl_rows)):
                lvl[x][y] = rANSDecoder.decode_symbol(pdf) - offset

        for x in range(0, rows):
            for y in range(0, rows):
                image[x][y] += lvl[x // (2 ** j) ][y // (2 ** j)]

        lvl_rows *= 2
        i += 1
    
    return image