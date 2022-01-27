import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyEmpatica",
    version="0.5.6",
    author="Walker Arce",
    author_email="walker.arce@unmc.edu",
    description="Communicate with your Empatica E4 in your Python scripts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Munroe-Meyer-Institute-VR-Laboratory/pyEmpatica",
    project_urls={
        "Bug Tracker": "https://github.com/Munroe-Meyer-Institute-VR-Laboratory/pyEmpatica/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
