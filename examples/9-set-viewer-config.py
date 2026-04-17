import marimo

__generated_with = "0.23.1"
app = marimo.App()


@app.cell
def _():
    import cadquery as cq
    from jupyter_cadquery import set_defaults, set_viewer_config, show

    # Keep defaults small in this demo and then override per-viewer options.
    set_defaults(axes=True, grid=(True, False, False), center_grid=True)

    part = (
        cq.Workplane("XY")
        .circle(0.6)
        .extrude(0.4)
        .faces(">Z")
        .workplane()
        .circle(0.2)
        .cutThruAll()
    )

    viewer = show(part, up="Y")
    set_viewer_config(
        viewer,
        ortho=False,
        transparent=False,
        ambient_intensity=1.0,
        direct_intensity=0.4,
    )
    return part, viewer


if __name__ == "__main__":
    app.run()
