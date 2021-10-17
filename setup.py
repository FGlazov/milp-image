import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ilp_image_compressor",
    version="0.0.1",
    author="Fedor Glazov",
    author_email="fedorglazov@gmail.com",
    description="A lossless image compressor which is based on an integer linear program.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FGlazov/ILP_ImageCompressor",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-2.0 License",
        "Operating System :: OS Independent",
    ],
)