
Nodes should be able to specify components



simulator_protocol = InteractionProtocol(
        description="""\

Interface to be implemented by a simulator.


```python

language="(in:image ; out:image_out)*"
components={
    'sub1': filter1,
    'sub2': filter1,
}
inputs={

}
connections=[
    '(image) -> |sub1| -> |sub2| -> (image_out)'
]
```



def on_image_received(self, context, data):
    context.send('sub1', 'image', data)
    context.send('sub2', 'image', data)
    


inputs={
    "pwm_commands": PWMCommands,
    # Seed random number generator
    "seed": int,
    # Reset request
    "reset": type(None),
    # Render request - produces image
    "render_image": type(None),
    # Step physics
    "step_physics": float,
    # Dump state information
    "dump_state": float,
},
outputs={
    "image": JPGImage,
    "state_dump": Any,
    "reset_ack": type(None),
    "step_physics_ack": type(None),
    "episode_start": EpisodeStart,
}
```
