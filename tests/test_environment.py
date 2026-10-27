import pandas as pd
import requests


def test_environment():
    assert pd.__version__
    assert requests.__version__