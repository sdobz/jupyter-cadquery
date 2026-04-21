"""Compatibility comms shim for ocp_vscode.

This module avoids importing marimo_cadquery at import time to prevent circular
imports when ocp_vscode imports jupyter_cadquery.comms.
"""

from enum import Enum

from cad_viewer_widget_marimo import show
from cad_viewer_widget_marimo.utils import display_args, viewer_args

__all__ = [
    "set_jupyter_port",
    "get_jupyter_port",
    "init_session",
    "send_data",
    "send_command",
    "send_backend",
    "send_measure_request",
    "send_config",
]

_TRANSPORT_PORT = None


def set_jupyter_port(port):
    global _TRANSPORT_PORT
    _TRANSPORT_PORT = port


def get_jupyter_port():
    return _TRANSPORT_PORT


def init_session(url):
    return None


def send_data(data, port=None, timeit=False):
    collapse_mapping = ["E", "1", "C", "R"]

    config = data["config"]
    type_ = data["type"]
    if type_ != "data":
        raise TypeError(f"Wrong data type {type_}")
    data = data["data"]

    if config.get("collapse") is not None:
        if isinstance(config["collapse"], Enum):
            config["collapse"] = collapse_mapping[config["collapse"].value]
        else:
            config["collapse"] = collapse_mapping[config["collapse"]]

    if config.get("reset_camera") is not None:
        if isinstance(config["reset_camera"], Enum):
            config["reset_camera"] = config["reset_camera"].value

    if config.get("orbit_control") is not None:
        config["control"] = "orbit" if config["orbit_control"] else "trackball"

    all_args = viewer_args(config)
    all_args.update(display_args(config))

    try:
        viewer = show(
            data,
            title=config.get("viewer"),
            anchor=config.get("anchor"),
            **all_args,
        )
    except TypeError as ex:
        if "anchor" not in str(ex):
            raise
        viewer = show(
            data,
            title=config.get("viewer"),
            **all_args,
        )

    return viewer


def send_command(data, port=None, title=None, timeit=False):
    if data == "config":
        return {}
    if data == "status":
        return {}
    raise ValueError("Unknown data for send_data")


def send_backend(data, port=None, jcv_id=None, timeit=False):
    return 200


def send_measure_request(jcv_id, shape_ids):
    return 501, '{"error":"measure backend not configured"}'


def send_config(config, port=None, title=None, timeit=False):
    return None
