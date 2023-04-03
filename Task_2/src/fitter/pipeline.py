from kedro.pipeline import Pipeline, node

from .nodes import load_data, fit, collect, report
from settings import N_PARALLEL

# kedro run --params start:'01.01.2021',end:'01.05.2021' --parallel

def create_pipeline(**kwargs):
    par_nodes = [
        node(
            fit,
            inputs=f'data{i}',
            outputs=f'res{i}',
        ) for i in range(N_PARALLEL)
    ]

    return Pipeline(
        [
            node(   
                load_data,
                inputs=['raw_data', 'params:start', 'params:end'],
                outputs=[f'data{i}' for i in range(N_PARALLEL)],
            ),
            *par_nodes,
            node(
                collect,
                inputs=[f'res{i}' for i in range(N_PARALLEL)],
                outputs='best',
                name='collect',
            ),
            node(
                report,
                inputs=['best', 'data0'],
                outputs=None,
                name='report',
            ),
        ]
    )
