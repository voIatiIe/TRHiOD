"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline

from .pipeline import create_pipeline


def register_pipelines() -> Dict[str, Pipeline]:
    pipeline = create_pipeline()

    return {
        "fit": pipeline,
        "__default__": pipeline,
    }
