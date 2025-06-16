import codecs
import re

from setuptools import find_packages, setup


def get_version(filename):
    with codecs.open(filename, "r", "utf-8") as fp:
        contents = fp.read()

    v = re.search(r"__version__ = ['\"]([^'\"]+)['\"]", contents)

    if v is None:
        raise Exception(
            "No match. Create/Update version.py to include line of __version__ = 'X.Y.Z'"
        )
    else:
        return v.group(1)


version = get_version("src/grf/version.py")


with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="godaddy-records-finder",
    version=version,
    description=("GoDaddy Records Finder"),
    long_description=readme,
    long_description_content_type="text/markdown",
    author="whoDoneItAgain",
    author_email="12127434+whoDoneItAgain@users.noreply.github.com",
    package_dir={"": "src"},
    packages=find_packages("src"),
    zip_safe=False,
    install_requires=["requests==2.32.4"],
    python_requires=">=3.12, <=4.0, !=4.0",
    entry_points={"console_scripts": ["grf = grf.__main__:main"]},
    url="https://github.com/whodoneitagain/godaddy-records-finder",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: Internet",
    ],
)
