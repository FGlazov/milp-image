import numpy as np
from numpy.core.fromnumeric import var
from scipy import stats
from scipy.stats import norm
from sklearn.mixture import GaussianMixture

# TODO: Test this for 64 * 64.
EXACT_PDF_CUTOFF = 64 * 64 # Use exact pdf for lvls with more elemets than this
APPROX_PDF_CUTOFF = 16 * 16 # Use approx pdf for lvls with more elements than this, and uniform under this.
TOP_LEVEL_N = 128 # Top levels ranges from -128 to 127
N = 64 # Other levels range from -64 to 63

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
    #return sum([gm.weights_[i] * norm(gm.means_[i], np.sqrt(gm.covariances_[i])).pdf(X) for i in range(0, gm.n_components)])
    return model_pdf(gm.weights_, gm.means_, gm.covariances_, X)

def model_pdf(weights, means, variances, X):
    result = np.array([0] * len(X), dtype=np.float64)

    weights = weights.astype(np.float32)
    means = means.astype(np.float32)
    variances = variances.astype(np.float32)

    payload = weights.flatten()[:-1] + means.flatten() + variances.flatten()

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
