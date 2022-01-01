## Short Description

milp-image is a toy project which implements, to the best of my knowledge, a novel image compressionn technique based upon a mixed inter linear program (milp). It is lossless, and it typically compresses images better than PNG, but it is typically beaten by the webp compression standard. The code has many limitations - see the limitations section - which would prevent it from being used in production.

## Technical Details

The main idea is to partition the image into 2x2 squares, starting from the top left corner. These 2x2 squares then themselves form an image, which one again can recursively partition into more 2x2 squares, until there is only one square left.

So e.g. given a 16x16 image, one ends up with 5 "levels". The 16 * 16 1x1 squares of the image, 8 * 8 2x2 squares above that one, 4 * 4 4x4 squares above that, 2 * 2 8x8 squares above that, and a single 16x16 square above that. The original image is then encoded as the sum of these levels. If, as an extreme example, the 16x16 image was made up of purely o one pixel value, then only the 16x16 square would need to be non-zero.

This seems like a bad idea at first glance - indeed instead of needing to encode just the original image, one additionally needs to encode all of the partitions of it above it. However, the encoding can work nicely if all of the paritions and the image itself are sparse - or low energy, that is, close to the average value of 128. For example, given this 256x256 version of the famous test image of Lena Forsén:

[![lena.png](https://i.postimg.cc/kgyxCPDF/lena.png)](https://postimg.cc/jDLW69HL)

milp-image learns the following representation of the image, into 9 partitions, each a quarter the size of the previous one.

[![grid.png](https://i.postimg.cc/j5fHGwfC/grid.png)](https://postimg.cc/zbJHhf01)

The representantation is learned using a mixed integer linear program. One first centers the pixel values around 0, so that they range from -128 to 127. The program then minimizes the sum of the absolute values of each of the pixel values across all the representations. This means the representation in the end will tend to have many values around 0. 

After the representation is learned, each of the levels of the representation is encoded using an entropy coder with a seperate model for each level. Depending on the size of the level a different representation is used for the statisitcal model for that level. For large levels, the exact underlying probability distribution is used, i.e. the histogram. This has the downside that the entire model must also be saved into the compressed image. For mid sized levels, a learned mixture of two Gaussians (learned via the EM-algorithm) is used. This provides a reasonable approximation to the true pdf, and only 5 parameters need to be stored. For small levels, a uniform pdf is assumed.

The entropy coder used in this project is a rANS-Coder.

## API and Example usage

The API is kept in milp_compressor/milp_comperssor.py. It consists of the functions

```
def compress_image(path_to_image, output_file = 'out.mipi'):

def decode_image(path_to_image, output_file = 'out.png'):
```

Both functions take strings of paths to the image as input. The first function compresses the image, and the second one recovers the image.

Example usage:

```python
import milp_compressor

milp_compressor.compress_image("my_img.png", "my_img.mipi")

# LATER:

milp_compressor.decode_image("my_img.mipi", "decoded.png")

# At this point the image in decoded.png will correspond to the one in my_img.png. 

```

## Limitations / Possible Future Enhancements

milp-image is **not** meant to be used in any production enviroment. It has the following limitations, some of which would be easy to fix, and others more difficult:

- The compressor currently only works on greyscale images. There is nothing stopping the compressor from working on color images. IOne hshould consider how to best incorperate the correlations between the color channels into the compression.
- It currently only works on square images of the form (2^i)x(2^i), e.g. 1024x1024 or 256x256. A simple solution would be to fill in any input image with grey pixels until it is of such a form. One needs to take care to then not encode the grey pixels and to not consider them in the models for the entropy coder.
- The runtime is high for compression. You can expect to take over half an hour to compress a 512x512 image on a modern CPU. There are a few performance wins possible - in particular it is likely that using a milp solver is overkill, since I suspect the underlying constraint matrix to be totally unimodular, although I do not have a proof. Another easy win would be for the milp-solver to actually accept the initial solution it is provided, but there seems to be a bug which is preventing that. There are also several simple heuristics one could use to speed up the milp process.
- Currently the runtime for decompression is also higher than it needs to be - it is done in under a minute for 256x256 images, but it should be feasible to do in under 5 seconds. 
- The compression rate is not optimized - in particular the mixture model of two Gaussians doesn't fit the data well enough. It would likely be better to use a mixture of a dirac distriution centered at zero and one or two Gaussians - that would likely result in better compression for mid-levels. If the fit is good enough, one could use the learned model for bigger levels as well, resulting in even more compression gains. In addition the objective of the mixed integer linear program could be tweaked to provide denser representations of higher levels, and sparaser representations of lower levels (or vice versa), which might result in better compression.
- Currently the compressed and decompressed files are stored as files, there is no option to not go via the file system if you want to e.g. send the file over the internet. However, it would be quick to adapt the compressor to work without files.
- There is currently a bug in python-mip which makes it break on certain Windows installations. In particular, Windows + Python 32 bit does not work.
