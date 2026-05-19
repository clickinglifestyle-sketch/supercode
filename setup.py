from setuptools import setup, find_packages

setup(
    name="finally-solved",
    version="0.1.0",
    packages=find_packages(),
    py_modules=["main", "config", "fs_entry"],
    install_requires=[
        "anthropic>=0.40.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "fs=fs_entry:main",
        ],
    },
)
