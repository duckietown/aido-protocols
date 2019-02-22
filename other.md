
Experience shows that we would like to enforce the following:

* It should be possible to understand whether the container has read the data on the pipe.
* It should be possible to understand how many messages a container will send in response. In general a node replies with 0 or more messages for each message it receives.
* It should be possible to transmit the information "Between the last message and time t there were no other messages to consider".

We thus define the following messages.

Input messages to the aidonode:

* `DATA(time:Time, channel:str, data:object)`: a new message for the channel.
* `SILENCE(time:Time, channel:str)`: There was no message on the channel until time `time`.

Output messages of the aidonode:

* `READ(hash:Hash)`: acknowledgement of having *read* a message (but not necessarily having processed it.)
* `PROCESSED(hash:Hash, tofollow:int)`: Acknoweledgement that the processing in response to the message identified by `hash` will produce `tofollow` `DATA` messages, which will come directly after this message. 

Timestamps will be defined isomorphic to ROS.

## JSON encoding for low-level messaging interface

This is how the messages are encoded:





`SILENCE`:

```json
{"aidonode": "SILENCE", "time": ![time], "channel": ![channel name]}
```

`READ`:

```json
{"aidonode": "READ", "hash": ![hash]}
```

`PROCESSED`:

```json
{"aidonode": "PROCESSED", "hash": ![hash], "tofollow": ![number of packets]}
```
