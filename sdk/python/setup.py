from setuptools import setup, find_packages

setup(
    name="bheem-dataviz",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["httpx>=0.26.0"],
    author="Bheem Platform",
    description="Python SDK for Bheem DataViz",
)
