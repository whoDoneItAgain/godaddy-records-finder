import codecs
import re

from setuptools import find_packages, setup


def get_version(filename):
    with codecs.open(filename, "r", "utf-8") as fp:
        contents = fp.read()
    return re.search(r"__version__ = ['\"]([^'\"]+)['\"]", contents).group(1)


version = get_version("src/grf/version.py")


with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="grf",
    version=version,
    description=("GoDaddy Record Finder"),
    long_description=readme,
    long_description_content_type="text/markdown",
    author="whodoneitagain",
    author_email="12127434+whoDoneItAgain@users.noreply.github.com",
    package_dir={"": "src"},
    packages=find_packages("src"),
    zip_safe=False,
    install_requires=["requests==2.31.0"],
    python_requires=">=3.12, <=4.0, !=4.0",
    entry_points={"console_scripts": ["grf = grf.__main__:main"]},
    test_suite="unittest",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
)
