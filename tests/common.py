import os
from pathlib import Path
from typing import Optional

import pytest

V = "HPI_TESTS_SEANB"

skip_if_not_seanb = pytest.mark.skipif(
    V not in os.environ,
    reason=f"test on runs on @seanbreckenridge data for now. Set envvar {V}=true to override",
)


def data(file: Optional[str]) -> Path:
    d = Path(__file__).absolute().parent / "testdata"
    if file:
        d = d / file
    assert d.exists()
    return d
