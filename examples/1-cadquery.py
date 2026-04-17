import marimo

__generated_with = "0.23.1"
app = marimo.App()


@app.cell
def _():
    import cadquery as cq
    from jupyter_cadquery import set_defaults, show, versions

    versions()
    set_defaults(axes=True, grid=(True, False, False), center_grid=True)

    box = cq.Workplane("XY").box(1, 2, 3).edges().fillet(0.1)
    viewer = show(box, up="Y")
    return box, viewer


if __name__ == "__main__":
    app.run()
