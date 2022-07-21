import argparse
import base64
from io import BytesIO
from pyrtcm.rtcmreader import RTCMReader


class ReadWriteStream():
    def __init__(self, max_size: int = 10 * 2 ** 20):
        self.buffer = BytesIO()
        self.read_pos = 0
        self.write_pos = 0
        self.max_size = max_size

    def read(self, n: int = 1) -> bytes:
        self.buffer.seek(self.read_pos)
        data = self.buffer.read(n)
        self.read_pos = self.buffer.tell()
        return data

    def readline(self) -> bytes:
        self.buffer.seek(self.read_pos)
        data = self.buffer.readline()
        self.read_pos = self.buffer.tell()
        return data

    def shrink(self) -> None:
        old_buffer = self.buffer
        self.buffer = BytesIO(old_buffer.getvalue()[self.read_pos:])
        self.write_pos -= self.read_pos
        self.read_pos = 0

    def write(self, data: bytearray) -> int:
        self.buffer.seek(self.write_pos)
        n = self.buffer.write(data)
        self.write_pos = self.buffer.tell()
        if len(self.buffer.getvalue()) > self.max_size:
            self.shrink()
        return n


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_msg", help="enter b64 encoded rtcm message",
                        type=str)
    args = parser.parse_args()
    raw_msg = args.raw_msg
    raw_data = base64.b64decode(raw_msg)
    message_stream = ReadWriteStream()
    rtcmReader = RTCMReader(message_stream)
    message_stream.write(raw_data)
    _, parsed_data = rtcmReader.read()
    print(parsed_data)


if __name__ == '__main__':
    main()
