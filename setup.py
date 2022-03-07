try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os.path

here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, "README.md")
with open(readme_path, "rb") as stream:
    readme = stream.read().decode("utf8")

setup(
    long_description=readme,
    long_description_content_type="text/markdown",
    name="django-smart-register",
    version="0.1.0",
    python_requires="==3.*,>=3.8",
    keywords="django",
    packages=[],
    package_dir={"": "src"},
    package_data={},
    extras_require={},
)
