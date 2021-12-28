import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="milp_imgcomp",
    version="0.0.1",
    author="Fedor Glazov",
    author_email="fedorglazov@gmail.com",
    description="A lossless image compressor which is based on a mixed integer linear program.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FGlazov/milp-image",
    # TODO: Fix packages here.
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'opencv-python',
        'py_rans',
        'pip',
        'mip',
        'numpy'
    ],
)
