import argparse
import re
import serial
import time
from datetime import datetime

PORT = "COM3"          # Change this on Windows, e.g. COM3
# PORT = "/dev/ttyUSB0"  # Use this on Linux
BAUD = 9600
TIMEOUT = 0.2

SAFE_PROBES = [
    b"\r",
    b"\n",
    b"P\r",
    b"P\n",
    b"PRINT\r",
    b"S\r",
    b"SI\r",
]

def ts() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def printable(data: bytes) -> str:
    return "".join(chr(b) if 32 <= b <= 126 else "." for b in data)

def hexify(data: bytes) -> str:
    return " ".join(f"{b:02X}" for b in data)

_CONTINUOUS_WEIGHT_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\d+)\s+g\s*$")

def is_continuous_weight_line(text: str) -> bool:
    t = text.strip()
    return bool(t) and bool(_CONTINUOUS_WEIGHT_RE.match(t))

def emit_rx(label: str, data: bytes) -> None:
    print(f"[{ts()}] {label}  ASCII: {printable(data)}")
    print(f"[{ts()}] {label}   HEX : {hexify(data)}")

def read_for(
    ser: serial.Serial,
    seconds: float | None,
    label: str = "RX",
    *,
    filter_continuous: bool = False,
    line_buf: bytearray | None = None,
) -> None:
    end = None if seconds is None else time.time() + seconds
    if not filter_continuous:
        while True:
            if end is not None and time.time() >= end:
                break
            data = ser.read(256)
            if data:
                emit_rx(label, data)
        return

    buf = line_buf if line_buf is not None else bytearray()
    while True:
        if end is not None and time.time() >= end:
            break
        data = ser.read(256)
        if not data:
            continue
        buf.extend(data)
        while True:
            nl = buf.find(b"\n")
            if nl < 0:
                break
            line = bytes(buf[: nl + 1])
            del buf[: nl + 1]
            core = line.rstrip(b"\r\n")
            text = core.decode("ascii", errors="replace")
            t = text.strip()
            if not t or is_continuous_weight_line(t):
                continue
            emit_rx(label, line)

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Serial monitor / probe helper for the scale.")
    p.add_argument(
        "--cont",
        action="store_true",
        help="After scripted phases, keep the serial port open and keep printing RX (Ctrl+C to exit).",
    )
    p.add_argument(
        "--filter-continuous",
        action="store_true",
        dest="filter_continuous",
        help=(
            "Suppress RX lines that look like continuous weight updates "
            '(e.g. "01 g", "-0000.001 g", "+0000.008 g", "+0000000. g"); other traffic is still shown. Uses line buffering.'
        ),
    )
    return p.parse_args()

def main() -> None:
    args = parse_args()
    print(f"Opening {PORT} at {BAUD} 8N1...")
    with serial.Serial(
        port=PORT,
        baudrate=BAUD,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=TIMEOUT,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False,
    ) as ser:
        # Clear any stale bytes
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        line_buf = bytearray() if args.filter_continuous else None

        print("\nPhase 1: passive listening for 15 seconds")
        print("Put the scale in hAnd, AUto, or Contin and watch output.\n")
        read_for(
            ser,
            15.0,
            label="PASSIVE",
            filter_continuous=args.filter_continuous,
            line_buf=line_buf,
        )

        print("\nPhase 2: safe probe commands")
        for probe in SAFE_PROBES:
            print(f"\n[{ts()}] TX  ASCII: {printable(probe)}")
            print(f"[{ts()}] TX   HEX : {hexify(probe)}")
            ser.write(probe)
            ser.flush()
            read_for(
                ser,
                1.0,
                label="RESP",
                filter_continuous=args.filter_continuous,
                line_buf=line_buf,
            )

        print("\nDone.")
        if args.cont:
            print("\n--cont: keeping channel open (Ctrl+C to exit).\n")
            try:
                read_for(
                    ser,
                    None,
                    label="RX",
                    filter_continuous=args.filter_continuous,
                    line_buf=line_buf,
                )
            except KeyboardInterrupt:
                print("\nStopped.")

if __name__ == "__main__":
    main()