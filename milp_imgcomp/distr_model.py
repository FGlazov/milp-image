import numpy as np
from scipy import stats
from scipy.stats import norm
from sklearn.mixture import GaussianMixture

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

    for weight, mean, variance in zip(weights, means, variances):
        result += weight * norm(mean, np.sqrt(variance)).pdf(X).flatten()
    return result

def discretized_gm_pdf(gm, top_level):
    if top_level:
        X = range(-128, 128)
    else:
        X = range(-64, 64)
    
    result = gm_pdf(gm, X)
    result /= result.sum()
    
    return result.flatten()


def create_approx_pdf(lvl, top_level):
    gm = create_gm(lvl)
    return discretized_gm_pdf(gm, top_level)