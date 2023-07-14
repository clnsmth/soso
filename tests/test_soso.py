import pytest
from src.soso.soso import hello_world


def test_test():
    assert 1 == 1


def test_hello_world():
    assert hello_world("Hello world", False) == "Hello world"
