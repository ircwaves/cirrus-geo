from copy import deepcopy

from cirrus.core.components import Feeder
from cirrus.core.components import Function
from cirrus.core.components import Task


def get_lambda_handler(Component, name):
    try:
        component = Component[name]
    except KeyError:
        raise Exception(f"Unknown {component.type} '{name}'")

    return component.import_handler()


def run_feeder(name, event):
    return get_lambda_handler(Feeder, name)(deepcopy(event), {})


def run_function(name, event):
    return get_lambda_handler(Function, name)(deepcopy(event), {})


def run_task(name, event):
    return get_lambda_handler(Task, name)(deepcopy(event), {})