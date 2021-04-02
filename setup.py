from setuptools import setup, find_namespace_packages  # type: ignore[import]


def subpackages():
    # make sure subpackages are only in the my/ folder (not in tests or other folders here)
    for p in find_namespace_packages(".", include=("my.*",)):
        if p.startswith("my."):
            yield p


username = "seanbreckenridge"
if __name__ == "__main__":
    setup(
        name=f"HPI-{username}",  # use a different name from karlicoss/HPI, for confusion regarding egg-link reasons
        use_scm_version={
            "local_scheme": "dirty-tag",
        },
        zip_safe=False,
        packages=list(subpackages()),
        url=f"https://github.com/{username}/HPI",
        author="Sean Breckenridge",
        author_email="seanbrecke@gmail.com",
        description="A Python interface to my life",
        python_requires=">=3.8",
    )
