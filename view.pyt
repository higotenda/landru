import gradio as gr
from main import routine
from osm2csv import process_address
from inout import gen_csv
import logging

logging.basicConfig(level=logging.CRITICAL)


def proc(input1):
    loc = process_address(input1)
    gen_csv(loc, "raw_demands.csv", place_type="any")
    routine(loc)
    return gr.Image("out/anim_network0.gif")


iface = gr.Interface(
    fn=proc,
    inputs=[gr.Textbox(label="Enter the Location")],
    outputs="image",
    title="Landru",
    description="Landru Tate - Advaned Geospatial Traffic Optimization Simulator",
)

iface.launch()
