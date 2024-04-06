import gradio as gr
from main import routine
from osm2csv import process_address
import logging

logging.basicConfig(level=logging.CRITICAL)


def proc(input1):
    process_address(input1)
    W = routine(noexec=True)
    return gr.Image("out/anim_network0.gif")


iface = gr.Interface(
    fn=proc,
    inputs=[gr.Textbox(label="Enter the Location")],
    outputs="image",
    title="Landru",
    description="Advaned Geospatial Traffic Optimization Simulator",
)

iface.launch(share=True)
