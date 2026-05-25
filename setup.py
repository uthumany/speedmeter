"""Setup script for SpeedMeter."""
from setuptools import find_packages, setup

setup(
    name="speedmeter",
    version="1.0.0",
    description="Terminal-based interactive internet speed meter with real-time UI",
    long_description=open("README.md").read() if __import__("os").path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="SpeedMeter Team",
    author_email="dev@speedmeter.io",
    url="https://github.com/uthumany/speedmeter",
    license="MIT",
    packages=find_packages(include=["speedmeter", "speedmeter.*"]),
    python_requires=">=3.10",
    install_requires=[
        "speedtest-cli>=2.1.3",
        "rich>=13.7.0",
        "textual>=0.52.0",
        "psutil>=5.9.8",
        "platformdirs>=4.2.0",
    ],
    extras_require={
        "dev": ["pytest>=8.0", "pytest-asyncio>=0.23.0"],
    },
    entry_points={
        "console_scripts": [
            "speedmeter = speedmeter.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Utilities",
    ],
)