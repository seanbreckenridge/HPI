#!/usr/bin/env python3
# see https://github.com/karlicoss/pymplate for up-to-date reference

from pathlib import Path
from setuptools import setup, find_namespace_packages  # type: ignore[import]


def subpackages():
    # make sure subpackages are only in the my/ folder (not in tests or other folders here)
    for p in find_namespace_packages(".", include=("my.*",)):
        if p.startswith("my."):
            yield p


reqs = Path("requirements.txt").read_text().strip().splitlines()


setup(
    name="HPI-additions",  # use a different name from karlicoss/HPI, for confusion regarding egg-link reasons
    use_scm_version={
        # TODO eh? not sure if I should just rely on proper tag naming and use use_scm_version=True
        # 'version_scheme': 'python-simplified-semver',
        "local_scheme": "dirty-tag",
    },
    zip_safe=False,
    packages=list(subpackages()),
    url="https://github.com/seanbreckenridge/HPI",
    author="Sean Breckenridge Gerasimov",
    author_email="seanbrecke@gmail.com",
    description="A Python interface to my life",
    python_requires=">=3.6",
    install_requires=reqs
)
