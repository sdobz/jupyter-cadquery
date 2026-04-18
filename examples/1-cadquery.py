import marimo

__generated_with = "0.23.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import cadquery as cq
    from jupyter_cadquery import (
        AnimationTrack,
        close_viewers,
        get_default_viewer,
        open_viewer,
        reset_defaults,
        set_default_viewer,
        set_defaults,
        show_all,
        versions,
        workspace_config,
        get_pick,
        Collapse,
        Color,
    )
    from jupyter_cadquery.show import show
    from jupyter_cadquery.replay import replay, enable_replay, disable_replay

    versions()
    return (
        AnimationTrack,
        Collapse,
        Color,
        close_viewers,
        cq,
        disable_replay,
        enable_replay,
        get_default_viewer,
        get_pick,
        open_viewer,
        replay,
        reset_defaults,
        set_default_viewer,
        set_defaults,
        show,
        show_all,
        versions,
        workspace_config,
    )


# ---------------------------------------------------------------------------
# Basic shape
# ---------------------------------------------------------------------------

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CAD Viewer

    ## Basic box
    """)
    return


@app.cell
def _(cq, mo, set_defaults, show):
    set_defaults(axes=True, grid=(True, False, False), center_grid=True)
    box = cq.Workplane("XY").box(1, 2, 3).edges().fillet(0.1)
    cv_box = show(box, up="Y", viewer="")
    mo.ui.anywidget(cv_box.widget)
    return box, cv_box


# ---------------------------------------------------------------------------
# Assemblies
# ---------------------------------------------------------------------------

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Assemblies

    ## CadQuery assembly

    Three boxes cut from a larger one, shown as a named assembly with colours.
    """)
    return


@app.cell
def _(cq):
    _box1 = cq.Workplane("XY").box(10, 20, 30).edges(">X or <X").chamfer(2)
    _box1.name = "box1"
    _box2 = cq.Workplane("XY").box(8, 18, 28).edges(">X or <X").chamfer(2)
    _box2.name = "box2"
    _box3 = cq.Workplane("XY").transformed(offset=(0, 15, 7)).box(30, 20, 6).edges(">Z").fillet(3)
    _box3.name = "box3"
    _box4 = _box3.mirror("XY").translate((0, -5, 0))
    _box4.name = "box4"
    box1 = _box1.cut(_box2).cut(_box3).cut(_box4)
    box2 = _box2
    box3 = _box3
    box4 = _box4
    return box1, box2, box3, box4


@app.cell
def _(box1, box3, box4, cq, mo, show):
    a1 = (
        cq.Assembly(name="ensemble")
        .add(box1, name="red box", color="#d7191c80")
        .add(box3, name="green box", color="#abdda4")
        .add(box4, name="blue box", color=(43, 131, 186, 0.3))
    )
    cv_a1 = show(a1, axes=True, grid=[True, False, False], ortho=True, axes0=True, viewer="")
    mo.ui.anywidget(cv_a1.widget)
    return a1, cv_a1

@app.cell
def _(mo, show):
    try:
        from build123d import Box, Axis, chamfer, fillet, Pos, mirror, Plane, Compound, Color as b123Color
        _b1 = Box(10, 20, 30)
        _b1 = chamfer(_b1.edges().group_by(Axis.X)[0] + _b1.edges().group_by(Axis.X)[-1], 2)
        _b1.label = "b123d red box"
        _b1.color = "#d7191c80"
        _b2 = Box(8, 18, 28)
        _b2 = chamfer(_b2.edges().group_by(Axis.X)[0] + _b2.edges().group_by(Axis.X)[-1], 2)
        _b3 = Pos(0, 15, 7) * Box(30, 20, 6)
        _b3 = fillet(_b3.edges().group_by()[-1], 3)
        _b3.label = "b123d green box"
        _b3.color = "#abdda4"
        _b4 = Pos(0, -5, 0) * mirror(_b3, Plane.XY)
        _b4.label = "b123d blue box"
        _b4.color = b123Color(43 / 255, 131 / 255, 186 / 255, 0.3)
        b123_box1 = _b1 - _b2 - _b3 - _b4
        b123_a1 = Compound(label="b123d ensemble", children=[b123_box1, _b3, _b4])
        cv_b123 = show(b123_a1, viewer="")
        _result = mo.ui.anywidget(cv_b123.widget)
    except ImportError:
        import marimo as _mo
        _result = _mo.md("*build123d not installed — skipping.*")
    _result
    return


# ---------------------------------------------------------------------------
# Faces, Edges, Vertices
# ---------------------------------------------------------------------------

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Faces, Edges, Vertices

    Use the buttons to cycle through sub-shape types on the same viewer.
    """)
    return


@app.cell
def _(box1, mo, set_defaults, show):
    set_defaults(show_parent=True)
    cv_fev = show(box1, viewer="")
    mo.ui.anywidget(cv_fev.widget)
    return (cv_fev,)


@app.cell
def _(box1, cv_fev, mo, show):
    show_faces_btn = mo.ui.button(
        label="Show diagonal faces",
        on_click=lambda _: show(box1, box1.faces("not(|Z or |X or |Y)"), show_parent=False, viewer=cv_fev.widget.id),
    )
    show_edges_btn = mo.ui.button(
        label="Show diagonal edges",
        on_click=lambda _: show(box1, box1.edges("not(|X or |Y or |Z)"), show_parent=False, viewer=cv_fev.widget.id),
    )
    show_vertices_btn = mo.ui.button(
        label="Show vertices",
        on_click=lambda _: show(box1, box1.vertices(), show_parent=False, viewer=cv_fev.widget.id),
    )
    show_all_sub_btn = mo.ui.button(
        label="Show all sub-shapes",
        on_click=lambda _: show(
            box1,
            box1.faces("not(|Z or |X or |Y)"),
            box1.edges("not(|X or |Y or |Z)"),
            box1.vertices(),
            show_parent=False,
            viewer=cv_fev.widget.id,
        ),
    )
    mo.hstack([show_faces_btn, show_edges_btn, show_vertices_btn, show_all_sub_btn])
    return show_all_sub_btn, show_edges_btn, show_faces_btn, show_vertices_btn


# ---------------------------------------------------------------------------
# Replay
# ---------------------------------------------------------------------------

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Replay

    Records each intermediate CadQuery step. Press the button to record the
    construction and step through the history in the viewer.
    """)
    return


@app.cell
def _(cq, disable_replay, enable_replay, mo, replay, set_defaults):
    def _start_replay(_):
        enable_replay(True)
        set_defaults(transparent=True)
        _b1 = cq.Workplane("XY").box(10, 20, 30).edges(">X or <X").chamfer(2)
        _b1.name = "box1"
        _b2 = cq.Workplane("XY").box(8, 18, 28).edges(">X or <X").chamfer(2)
        _b2.name = "box2"
        _b3 = cq.Workplane("XY").transformed(offset=(0, 15, 7)).box(30, 20, 6).edges(">Z").fillet(3)
        _b3.name = "box3"
        _b4 = _b3.mirror("XY").translate((0, -5, 0))
        _b4.name = "box4"
        _b1 = _b1.cut(_b2).cut(_b3).cut(_b4)
        replay(_b1, show_result=False, show_bbox=True)
        disable_replay()

    replay_btn = mo.ui.button(label="Replay construction steps", on_click=_start_replay)
    replay_btn
    return (replay_btn,)


# ---------------------------------------------------------------------------
# Camera position control
# ---------------------------------------------------------------------------

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Camera position control

    `position`, `quaternion`, `target`, and `zoom` can be read and written from Python.
    """)
    return


@app.cell
def _(a1, mo, open_viewer, show):
    cv_cam = open_viewer("Assembly", cad_width=800, height=600, default=False)
    show(a1, orbit_control=True, viewer="Assembly")
    mo.ui.anywidget(cv_cam.widget)
    return (cv_cam,)


@app.cell
def _(cv_cam, mo):
    _saved = {}

    def _save(_):
        _saved["position"]   = cv_cam.position
        _saved["target"]     = cv_cam.target
        _saved["quaternion"] = cv_cam.quaternion
        _saved["zoom"]       = cv_cam.zoom
        print("Saved:", _saved)

    def _restore(_):
        if not _saved:
            print("Nothing saved yet — press Save first")
            return
        cv_cam.position = _saved["position"]
        cv_cam.target   = _saved["target"]
        if cv_cam.control == "trackball":
            cv_cam.quaternion = _saved["quaternion"]
        cv_cam.zoom = _saved["zoom"]

    def _preset(_):
        cv_cam.position   = (135.3, 79.2, 29.6)
        cv_cam.target     = (-4.8, 17.1, 7.9)
        cv_cam.quaternion = (0.399, 0.518, 0.643, 0.396)
        cv_cam.zoom       = 1.45

    save_cam_btn    = mo.ui.button(label="Save camera",    on_click=_save)
    restore_cam_btn = mo.ui.button(label="Restore camera", on_click=_restore)
    preset_cam_btn  = mo.ui.button(label="Preset view",    on_click=_preset)
    close_cam_btn   = mo.ui.button(label="Close viewer",   on_click=lambda _: cv_cam.close())
    mo.hstack([save_cam_btn, restore_cam_btn, preset_cam_btn, close_cam_btn])
    return close_cam_btn, preset_cam_btn, restore_cam_btn, save_cam_btn


# ---------------------------------------------------------------------------
# Widget interaction
# ---------------------------------------------------------------------------

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Widget interaction

    Toggle visibility, collapse state, and lighting from Python.
    """)
    return


@app.cell
def _(Collapse, a1, mo, show):
    cv_interact = show(a1, collapse=Collapse.NONE, axes=True, viewer="")
    mo.ui.anywidget(cv_interact.widget)
    return (cv_interact,)


@app.cell
def _(Collapse, cv_interact, mo):
    def _hide_parts(_):
        cv_interact.update_states({
            "/ensemble/red box/red box":   (1, 0),
            "/ensemble/blue box/blue box": [0, 1],
        })

    def _show_parts(_):
        cv_interact.update_states({
            "/ensemble/red box/red box":   (1, 1),
            "/ensemble/blue box/blue box": [1, 1],
        })

    def _dim_lights(_):
        cv_interact.ambient_intensity = 0.2
        cv_interact.direct_intensity  = 0.1

    def _normal_lights(_):
        cv_interact.ambient_intensity = 0.5
        cv_interact.direct_intensity  = 0.3

    def _collapse_all(_):
        cv_interact.widget.collapse = Collapse.ALL

    def _expand_all(_):
        cv_interact.widget.collapse = Collapse.NONE

    hide_btn     = mo.ui.button(label="Hide red & show blue transparent", on_click=_hide_parts)
    show_btn     = mo.ui.button(label="Restore visibility",               on_click=_show_parts)
    dim_btn      = mo.ui.button(label="Dim lighting",                     on_click=_dim_lights)
    bright_btn   = mo.ui.button(label="Normal lighting",                  on_click=_normal_lights)
    collapse_btn = mo.ui.button(label="Collapse tree",                    on_click=_collapse_all)
    expand_btn   = mo.ui.button(label="Expand tree",                      on_click=_expand_all)
    mo.vstack([
        mo.hstack([hide_btn, show_btn]),
        mo.hstack([dim_btn, bright_btn]),
        mo.hstack([collapse_btn, expand_btn]),
    ])
    return bright_btn, collapse_btn, dim_btn, expand_btn, hide_btn, show_btn


# ---------------------------------------------------------------------------
# Clipping
# ---------------------------------------------------------------------------

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Clipping

    Enable clipping planes and control them from Python.
    """)
    return


@app.cell
def _(a1, mo, show):
    cv_clip = show(a1, axes=True, grid=[True, False, False], viewer="")
    mo.ui.anywidget(cv_clip.widget)
    return (cv_clip,)


@app.cell
def _(cv_clip, mo):
    def _enable_clip(_):
        cv_clip.tab            = "clip"
        cv_clip.clip_planes    = True
        cv_clip.clip_slider_0  = 0
        cv_clip.clip_slider_1  = -2
        cv_clip.clip_slider_2  = 12

    def _intersect_clip(_):
        cv_clip.clip_intersection = not cv_clip.clip_intersection

    def _disable_clip(_):
        cv_clip.clip_planes       = False
        cv_clip.clip_intersection = False
        cv_clip.tab               = "tree"

    enable_clip_btn    = mo.ui.button(label="Enable clip planes",  on_click=_enable_clip)
    intersect_clip_btn = mo.ui.button(label="Toggle intersection", on_click=_intersect_clip)
    disable_clip_btn   = mo.ui.button(label="Disable clipping",    on_click=_disable_clip)
    close_clip_btn     = mo.ui.button(label="Close viewer",        on_click=lambda _: cv_clip.close())
    mo.hstack([enable_clip_btn, intersect_clip_btn, disable_clip_btn, close_clip_btn])
    return close_clip_btn, disable_clip_btn, enable_clip_btn, intersect_clip_btn


# ---------------------------------------------------------------------------
# Rotations
# ---------------------------------------------------------------------------

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Rotations

    Drive the camera programmatically for a turntable effect.
    """)
    return


@app.cell
def _(a1, mo, show):
    cv_rot = show(a1, orbit_control=False, viewer="")
    mo.ui.anywidget(cv_rot.widget)
    return (cv_rot,)


@app.cell
def _(cv_rot, mo):
    import time as _time

    def _spin_right(_):
        for _ in range(10):
            cv_rot.rotate_x(1)
            cv_rot.rotate_y(3)
            cv_rot.rotate_z(5)
            _time.sleep(0.05)

    def _spin_left(_):
        for _ in range(10):
            cv_rot.rotate_z(-5)
            cv_rot.rotate_y(-3)
            cv_rot.rotate_x(-1)
            _time.sleep(0.05)

    spin_right_btn = mo.ui.button(label="Spin right",   on_click=_spin_right)
    spin_left_btn  = mo.ui.button(label="Spin left",    on_click=_spin_left)
    close_rot_btn  = mo.ui.button(label="Close viewer", on_click=lambda _: cv_rot.close())
    mo.hstack([spin_right_btn, spin_left_btn, close_rot_btn])
    return close_rot_btn, spin_left_btn, spin_right_btn


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Export

    Adjust the view first, then press a button.
    """)
    return


@app.cell
def _(box, mo, show):
    cv_export = show(box, up="Y", axes=True, grid=(True, False, False), viewer="")
    mo.ui.anywidget(cv_export.widget)
    return (cv_export,)


@app.cell
def _(cv_export, mo):
    export_png_btn  = mo.ui.button(
        label="Export PNG",
        on_click=lambda _: cv_export.export_png("cadquery_box.png"),
    )
    export_html_btn = mo.ui.button(
        label="Export HTML",
        on_click=lambda _: cv_export.export_html(),
    )
    pin_png_btn = mo.ui.button(
        label="Pin as PNG",
        on_click=lambda _: cv_export.pin_as_png(),
    )
    mo.hstack([export_png_btn, export_html_btn, pin_png_btn])
    return export_html_btn, export_png_btn, pin_png_btn


if __name__ == "__main__":
    app.run()
