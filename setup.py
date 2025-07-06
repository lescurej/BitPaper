from setuptools import setup, find_packages

setup(
    name="bitpaper",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "reportlab>=4.0.4",
        "Pillow>=10.0.1", 
        "numpy>=1.24.3",
        "reedsolo>=1.7.0",
        "cryptography>=41.0.7",
        "qrcode>=7.4.2",
        "opencv-python>=4.8.1.78",
    ],
    extras_require={
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "psutil>=5.8.0",
        ],
        "secure": [
            "reedsolo>=1.7.0",
            "cryptography>=41.0.7",
        ]
    },
    entry_points={
        'console_scripts': [
            'bitpaper=main:main',
            'bitpaper-test=test.run_tests:main',
            'bitpaper-generate-keys=generate_keys:generate_key_pair',
        ],
    },
    python_requires=">=3.8",
    description="Secure data encoding to printable patterns with encryption and error correction",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="BitPaper Team",
    author_email="",
    url="",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    keywords="security, encryption, data-encoding, paper-storage, error-correction",
) 