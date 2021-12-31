import numpy as np
from numpy.core.fromnumeric import var
from scipy import stats
from scipy.stats import norm
from sklearn.mixture import GaussianMixture

# TODO: Test this for 128 * 128.
EXACT_PDF_CUTOFF = 64 * 64 # Use exact pdf for lvls with more elemets than this
APPROX_PDF_CUTOFF = 16 * 16 # Use approx pdf for lvls with more elements than this, and uniform under this.
TOP_LEVEL_N = 128 # Top levels ranges from -128 to 127
N = 64 # Other levels range from -64 to 63

# In bytes
# One float32 per value in range(-n, n)
EXACT_PDF_PAYLOAD_SIZE = 4 * 2 * N
EXACT_PDF_TOP_LVL_PAYLOAD_SIZE = 4 * 2 * TOP_LEVEL_N

# In bytes
# 5 float32s - one for the 2 weights, 2 for the means, 2 for the variances.
APPROX_PDF_PAYLOAD_SIZE = 4 * 5

# TODO: Update this
# Currently the model assumes that the underlying distribution is a mixture of two Gaussians
# One (ussualy) with a small variance, and another with a large variance, both centered (ussualy close to) 0.
# This does not capture the underlying distribution that well - perhaps a better distribution would be
# a mixture of a dirchlet distribution + a Gaussian or a Laplacian?
# Perhaps one should directly work with discrete distributions instead of discretizing?
# The current method used is one out of convience, since sklearn is capable of learning a gaussian mixture model.

def create_gm(lvl):    
    gm = GaussianMixture(
        n_components=2,
        means_init=[[0.0],[0.0]],
        precisions_init=[[[1.0]], [[1.0/50.0]]], 
        weights_init=[0.6, 0.4]
    )
    
    gm.fit(lvl.reshape(-1, 1))
    
    return gm

def gm_pdf(gm, X):
    return model_pdf(gm.weights_, gm.means_, gm.covariances_, X)

def model_pdf(weights, means, variances, X):
    result = np.array([0] * len(X), dtype=np.float64)

    weights = weights.astype(np.float32)
    means = means.astype(np.float32)
    variances = variances.astype(np.float32)

    payload = np.concatenate((np.array([weights[0]]), means.flatten(), variances.flatten()))

    for weight, mean, variance in zip(weights, means, variances):
        result += weight * norm(mean, np.sqrt(variance)).pdf(X).flatten()
    return result, payload

def discretized_gm_pdf(gm, top_level):
    if top_level:
        X = range(-TOP_LEVEL_N, TOP_LEVEL_N)
    else:
        X = range(-N, N)
    
    result, payload = gm_pdf(gm, X)
    result /= result.sum()
    
    return result.flatten(), payload

def create_approx_pdf(lvl, top_level):
    gm = create_gm(lvl)
    return discretized_gm_pdf(gm, top_level)

def approx_pdf_from_params(payload, n):
    X = range(-n, n)
    weights = []

    weights.append(payload[0])
    weights.append(1 - payload[0])
    weights = np.array(weights, dtype=np.float32)

    means = payload[1:3]
    variances = payload[3:5]

    pdf, _ = model_pdf(weights, means, variances, X)

    return pdf / pdf.sum()

def create_model(lvl, lvl_index):
    top_level = lvl_index == 0
    if top_level:
        n = TOP_LEVEL_N
    else:
        n = N
    
    if lvl.size > EXACT_PDF_CUTOFF:
        square_values = np.array([var.x + n for var in lvl.flatten()], dtype=np.int16)
        bins = np.bincount(square_values, minlength=n)
        pdf = bins.astype(np.float32) / lvl.size
        payload = pdf
    elif lvl.size > APPROX_PDF_CUTOFF:
        pdf, payload = create_approx_pdf(lvl, top_level)
    else:
        pdf = np.array([1.0 / float(2 * n)] * (2 * n), dtype=np.float32) 
        payload = []        

    return pdf, payload

def get_pdf_payload_size(lvl_size, top_level):
    if lvl_size > EXACT_PDF_CUTOFF:
        if top_level:
            return EXACT_PDF_TOP_LVL_PAYLOAD_SIZE
        else:
            return EXACT_PDF_PAYLOAD_SIZE
    elif lvl_size > APPROX_PDF_CUTOFF:
        return APPROX_PDF_PAYLOAD_SIZE
    else:
        return 0

def decode_pdf_payload(lvl_size, top_level, payload):
    if top_level:
        n = TOP_LEVEL_N
    else:
        n = N

    if lvl_size > EXACT_PDF_CUTOFF:
        pdf = np.frombuffer(payload, np.float32)
    elif lvl_size > APPROX_PDF_CUTOFF:
        pdf_parameters = np.frombuffer(payload, np.float32)
        pdf = approx_pdf_from_params(pdf_parameters, n)
    else:
        pdf = np.array([1.0 / float(2 * n)] * (2 * n), dtype=np.float32) 

    return pdf
