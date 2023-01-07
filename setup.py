import re
import toml
import codecs
import os.path
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
with open('README.md', 'r', encoding='utf-8') as fh:
    long_desc = fh.read()


def read(*parts):
    """
    Reads file parts.
    :param parts:
    :return:
    """
    return codecs.open(os.path.join(HERE, *parts), 'r').read()


def find_version(*file_paths) -> str:
    """
    Locates the version parameters specified in an arbitrary file
    :param file_paths: List of file paths to locate the __version__
    :return: String semantic version
    """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)

    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def get_install_requirements() -> list:
    """
    Installs and reads direct dependencies specified within the Pipfile. This ensures all dependencies are managed through
    pipenv and there is no need for a requirements.txt file or multiple files to manage project dependencies.
    :return:
    """
    try:
        with open('Pipfile', 'r') as fh:
            pipfile = fh.read()
            # TODO refactor to not require TOML
            pipfile_toml = toml.loads(pipfile)
    except Exception as e:
        print(f'Failed to read or parse Pipfile. Error = {str(e)}')
        return []
    try:
        required_packages = pipfile_toml['packages'].items()
    except KeyError:
        return []

    # If a version or range is specified in the Pipfile then honor it
    # otherwise just list the package
    final_pkg_list = []
    for pkg, ver in required_packages:
        if isinstance(ver, dict):
            # Assuming this package is from a VCS like Github
            final_pkg_list.append(f"{pkg}@git+{ver['git']}#egg={pkg}")
        else:
            final_pkg_list.append("{0}{1}".format(pkg, ver) if ver != "*" else pkg)
    return final_pkg_list


setup(
    name='rs-content-creator',
    version=find_version('rs_content', "__init__.py"),
    description="Automatically collects reddit data from r/2007scape subreddit for analysis and content suggestion.",
    url="https://github.com/cbartram/RuneScape-Content-Creation",
    scripts=[],
    python_requires=">=3.10",
    author="Christian Bartram",
    long_description=long_desc,
    long_description_type="text/markdown",
    author_email="runewraith.yt@gmail.com",
    packages=find_packages(exclude=["test", '*.tests', '*.tests.*', 'tests.*', 'tests/*']),
    keywords="runescape content creation youtube video idea suggest "
             "kmeans cluster machine learning python osrs oldschool reddit 2007scape",
    include_package_data=True,
    install_requires=get_install_requirements(),
    entry_points={
        'console-scripts': ['rs-content = rs_content.__init__:main']
    },
    tests_require=['coverage'],
    zip_safe=False
)
