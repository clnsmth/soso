"""Configure the test suite."""

import pytest
from soso.strategies.eml import EML
from soso.strategies.iso19115 import ISO19115


@pytest.fixture
def strategy_names():
    """Return the names of available strategies."""
    return ["eml", "iso19115"]


@pytest.fixture(params=[EML, ISO19115])
def strategy_instance(request):
    """Return the strategy instances."""
    return request.param()


@pytest.fixture
def interface_methods():
    """Return the names of strategy methods."""
    return ["set_name", "set_description"]


@pytest.fixture
def soso_properties():
    """Return the names of SOSO properties."""
    return ["name", "description"]
