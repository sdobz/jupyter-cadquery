#
# Copyright 2025 Bernhard Walter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import base64
from threading import RLock

from ocp_vscode.backend import ViewerBackend
from ocp_vscode.comms import MessageType
from ocp_tessellate.ocp_utils import loc_to_tq, serialize

BACKENDS = {}
_LOCK = RLock()


def _normalize_model_locations(model):
    """Normalize model `loc` values to (translation, quaternion) tuples."""

    def encode_shape_obj(shape):
        if shape is None or isinstance(shape, str):
            return shape
        return base64.b64encode(serialize(shape)).decode("utf-8")

    def walk(node):
        if not isinstance(node, dict):
            return

        loc = node.get("loc")
        if loc is not None and not isinstance(loc, (tuple, list)):
            try:
                node["loc"] = loc_to_tq(loc)
            except Exception:
                # Keep original payload if conversion is not applicable.
                pass

        shape = node.get("shape")
        if isinstance(shape, dict) and "obj" in shape:
            shape["obj"] = encode_shape_obj(shape.get("obj"))
        elif isinstance(shape, list):
            node["shape"] = [encode_shape_obj(s) for s in shape]

        parts = node.get("parts")
        if isinstance(parts, list):
            for part in parts:
                walk(part)

    walk(model)
    return model


def register_backend(viewer_id, model):
    """Register or replace the in-process backend model for a viewer."""
    backend = ViewerBackend(port=0, jcv_id=viewer_id)
    backend.load_model(_normalize_model_locations(model))
    with _LOCK:
        BACKENDS[viewer_id] = backend
    return backend


def get_backend(viewer_id):
    with _LOCK:
        return BACKENDS.get(viewer_id)


def handle_measure_request(viewer_id, message):
    """Handle a measurement request through the in-process backend."""
    backend = get_backend(viewer_id)
    if backend is None:
        raise KeyError(f"Unknown viewer '{viewer_id}'")
    return backend.handle_event(message, MessageType.UPDATES)


def reset_backends():
    """Clear all registered backends."""
    with _LOCK:
        BACKENDS.clear()
