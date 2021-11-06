#!/usr/bin/python3

import signal
import sys
import mido
from midi_control import MidiControl

# Python MIDI channels are zero based.
WARBL_CFG_CHANNEL = 6
WARBL_CFG_FINGERING_ID = 118

MAX_WARBL_FINGER_HOLES = 9
MAX_FINGER_POSITIONS = 20

FINGER_DONT_CARE = 0
FINGER_COVERED = 1
FINGER_OPEN = 2

FINGERING_PACKET_START = 100
FINGERING_PACKET_PATTERN = 101
FINGERING_PACKET_END = 102

REGISTER_BOTH = 0
REGISTER_HIGH_ONLY = 1
REGISTER_LOW_ONLY = 2

midi_control = MidiControl()


def do_exit():
    print('  EXIT')
    sys.exit(1)


def signal_handler(sig, frame):
    do_exit()


signal.signal(signal.SIGINT, signal_handler)


def send_warbl_config(byte):
    msg= mido.Message('control_change', channel=WARBL_CFG_CHANNEL, control=WARBL_CFG_FINGERING_ID, value=byte)
    midi_control.send(msg)
    print( msg )


def send_start_packet():
    # send the two byte fingering start packet
    send_warbl_config(2);
    send_warbl_config(FINGERING_PACKET_START);


def note_name_to_midi(note_name):
    midi_note = 0

    for c in note_name:
        if c == ' ':
            continue
        look_up = {'C': 12, 'D': 14, 'E': 16, 'F': 17, 'G': 19, 'A': 21, 'B': 23}
        if c in look_up.keys():
            midi_note = look_up[c]
        if c == '#':
            midi_note += 1
        if c == 'b':
            midi_note -= 1
        if '0' <= c <= '9':
            octave = ord(c) - ord('0')
            midi_note += octave * 12
    return midi_note


def find_packet_length(fingers):
    length = 0
    for c in fingers:
        if c == ' ':
            continue
        length += 1

    return length


def send_finger_pattern(fingering):
    if fingering.startswith('%'):
        return
    sep = fingering.find(':')
    if sep > 0:
        fingers = fingering[sep + 1:]
        packet_len = find_packet_length(fingers)
        send_warbl_config(packet_len + 2)
        send_warbl_config(FINGERING_PACKET_PATTERN)
        midi_note = note_name_to_midi(fingering[0:sep])
        send_warbl_config(midi_note)
        send_warbl_config(REGISTER_BOTH)

        for c in fingers:
            if c == 'o':
                send_warbl_config(FINGER_COVERED)
            elif c == '-':
                send_warbl_config(FINGER_OPEN)
            elif c == 'x':
                send_warbl_config(FINGER_DONT_CARE)
            elif c == '%':
                return


def send_file(file_name):
    if midi_control.open_midi_port("WARBL"):
        data_in = open(file_name, 'r')

        send_start_packet()

        while True:
            line = data_in.readline()
            if not line:
                break
            send_finger_pattern(line)

        print("Send custom fingering file '{}' to the Wabrl".format(file_name))
if __name__ == "__main__":
    send_file("D_whistle_fingering.txt")
