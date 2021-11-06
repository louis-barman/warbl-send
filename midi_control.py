import mido, time
import threading, queue


# runs in a different thread
def read_midi_events(in_port, q):
    while True:
        msg = in_port.receive()
        msg.time = time.perf_counter()
        q.put(msg)


class MidiControl:

    def __init__(self):
        self._in_port = None
        self._out_port = None
        self._queue = queue.Queue()

    def open_midi_port(self, auto_name):

        port_in_names = mido.get_input_names()
        for in_name in port_in_names:
            if auto_name in in_name:
                self._in_port = mido.open_input(in_name)

                if self._in_port is not None:
                    print("Opened MIDI port:" + in_name)
                    with self._queue.mutex:
                        self._queue.queue.clear()
                    # turn-on the worker thread
                    threading.Thread(target=read_midi_events, args=(self._in_port, self._queue), daemon=True).start()

                    port_out_names = mido.get_output_names()
                    for out_name in port_out_names:
                        if auto_name in out_name:
                            self._out_port = mido.open_output(out_name)
                            return True

        print("cannot open MIDI port:" + auto_name)
        print("MIDI ports available: {}".format(port_in_names))
        return False

    def send(self, msg):
        self._out_port.send(msg)
