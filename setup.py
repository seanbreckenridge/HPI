from typing import Iterator
from setuptools import setup, find_namespace_packages  # type: ignore[import]


def subpackages() -> Iterator[str]:
    # make sure subpackages are only in the my/ folder (not in tests or other folders here)
    for p in find_namespace_packages("."):
        if p.startswith("my"):
            yield p


if __name__ == "__main__":
    setup(packages=list(subpackages()))
