from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gcp-data-pipeline",
    version="0.1.0",
    author="GCP Data Pipeline Team",
    description="A data pipeline application for Google Cloud Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "google-cloud-pubsub>=2.18.0",
        "google-cloud-bigquery>=3.11.0",
        "google-cloud-storage>=2.10.0",
        "google-cloud-dataflow-client>=0.8.3",
        "pandas>=2.0.0",
        "apache-beam[gcp]>=2.50.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "mock>=5.1.0",
            "flake8>=6.1.0",
            "black>=23.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
