


## Time representation


* Reference clock

frame: "epoch", "simulation episode"
clock: hostname



## Uncertainty

Optionally you can specify a second time instant,  
successive to the first, which defines the upper bound of the time.

## Type of timing info

For sensor data:

* "Last acquisition time": timestamp of the last acquired data 

* "Computed time": when this data was computed.

* "Received"

## Wire representation


```json

{
    "topic": "topic",
    "data": "data",
    "timing": {
        "acquired": {
          "obstopic1": {},
          "obstopic2": {},
        }, 
        "computed": {
          "node1": {},
          "node2": {},
          "node3": {},
        },
        "received": {
          "frame": "sim",
          "time": {'s': 0, 'us': 1111},
          "clock": "host1"
        },
    }
}



```

## API


In Python:

```python
from typing import *

class Timestamp:
    s: int
    us: int
    
class TimeSpec:
    time: Timestamp
    time2: Optional[Timestamp]
    frame: str
    clock: str
    
class TimingInfo:
    acquired: Optional[Dict[str, TimeSpec]]
    processed: Optional[Dict[str, TimeSpec]]
    received: Optional[TimeSpec]
    

def on_received_topicname(self, context, data, timing: TimingInfo):
    pass

```
