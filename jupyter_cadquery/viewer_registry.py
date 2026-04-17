"""Host-agnostic viewer registry used by jupyter_cadquery."""

_VIEWERS = {}
_DEFAULT_VIEWER = None


def register_viewer(title, viewer, default=True):
    """Register a viewer instance with an optional title key."""
    global _DEFAULT_VIEWER
    key = title if title not in (None, "") else viewer.widget.id
    _VIEWERS[key] = viewer
    if default or _DEFAULT_VIEWER is None:
        _DEFAULT_VIEWER = key
    return key


def get_viewer(title):
    return _VIEWERS.get(title)


def get_viewers():
    return dict(_VIEWERS)


def close_viewer(title):
    viewer = _VIEWERS.pop(title, None)
    if viewer is None:
        return False
    try:
        viewer.dispose()
    except Exception:
        pass
    return True


def close_viewers():
    keys = list(_VIEWERS.keys())
    for key in keys:
        close_viewer(key)


def get_default_viewer():
    return _DEFAULT_VIEWER


def set_default_viewer(title):
    global _DEFAULT_VIEWER
    if title in _VIEWERS:
        _DEFAULT_VIEWER = title

