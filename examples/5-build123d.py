import marimo

__generated_with = "0.23.1"
app = marimo.App()


@app.cell
def _():
    from build123d import Box, BuildPart, CounterBoreHole, Mode
    from jupyter_cadquery import set_defaults, show

    set_defaults(edge_accuracy=0.0001)

    with BuildPart() as part_builder:
        Box(1, 1, 1)
        CounterBoreHole(0.2, 0.3, 0.1)
        Box(1, 0.2, 1, mode=Mode.SUBTRACT)

    viewer = show(part_builder.part)
    return part_builder, viewer


if __name__ == "__main__":
    app.run()
