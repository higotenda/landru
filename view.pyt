import gradio as gr
from main import routine
from osm2csv import process_address
import osm2csv as ocv
from inout import gen_csv

# import logging

# logging.basicConfig(level=logging.CRITICAL)


# def proc(input1):
#     loc = process_address(input1)
#     gen_csv(loc, "raw_demands.csv", place_type="any")
#     routine(loc)
#     return gr.Image("out/anim_network0.gif")


# iface = gr.Interface(
#     fn=proc,
#     inputs=[gr.Textbox(label="Enter the Location")],
#     outputs="image",
#     title="Landru",
#     description="Landru Tate - Advaned Geospatial Traffic Optimization Simulator",
# )

# iface.launch()

import logging

logging.basicConfig(level=logging.CRITICAL)


def proc(
    input1,
    rad_dist,
    global_mean_jam_density,
    jam_density_variance,
    freeflow_speed_variance,
    freeflow_mean_shiftcoef,
):
    ocv.global_warming(
        rad_dist,
        global_mean_jam_density,
        jam_density_variance,
        freeflow_speed_variance,
        freeflow_mean_shiftcoef,
    )
    loc = process_address(input1)
    gen_csv(loc, "raw_demands.csv", place_type="any")
    routine(loc)

    return gr.Image("out/anim_network0.gif")


iface = gr.Interface(
    fn=proc,
    inputs=[
        gr.Textbox(label="Enter the Location"),
        gr.Slider(minimum=0.1, maximum=5.0, value=1.5, label="Radius Distance"),
        gr.Slider(
            minimum=0.05, maximum=0.25, value=0.16, label="Global Mean Jam Density"
        ),
        gr.Slider(minimum=0.01, maximum=0.05, value=0.02, label="Jam Density Variance"),
        gr.Slider(
            minimum=0.01, maximum=0.1, value=0.05, label="Free Flow Speed Variance"
        ),
        gr.Slider(
            minimum=0.0001,
            maximum=0.01,
            value=0.0025,
            label="Free Flow Mean Shift Coefficient",
        ),
    ],
    outputs="image",
    title="Landru",
    description="Advanced Geospatial Traffic Optimization Simulator",
)

iface.launch()
