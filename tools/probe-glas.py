#!/usr/bin/env python3
"""Read-only local probe for a Johnson Controls GLAS thermostat.

Sends BACnet Who-Is and, only if the device answers with I-Am, reads
standard Device-object properties. Never writes.
"""

from __future__ import annotations

import argparse
import socket
import struct
import sys
import time

BACNET_PORT = 47808

# ASHRAE 135 property identifiers used on the Device object.
PROP_DESCRIPTION = 28
PROP_FIRMWARE_REVISION = 44
PROP_MODEL_NAME = 70
PROP_OBJECT_LIST = 76
PROP_OBJECT_NAME = 77
PROP_VENDOR_NAME = 121

DEVICE_OBJECT_TYPE = 8
READ_PROPERTY = 12


def whois_unicast() -> bytes:
    # BVLC original-unicast, NPDU v1 with no reply-expected bit,
    # unconfirmed Who-Is.
    return bytes.fromhex("810a000801001008")


def whois_broadcast() -> bytes:
    return bytes.fromhex("810b000c0120ffff00ff1008")


def object_identifier(object_type: int, instance: int) -> int:
    return ((object_type & 0x3FF) << 22) | (instance & 0x3FFFFF)


def read_property_request(device_instance: int, property_id: int, invoke_id: int) -> bytes:
    obj_id = object_identifier(DEVICE_OBJECT_TYPE, device_instance)
    apdu = bytes(
        [
            0x00,  # confirmed request, unsegmented
            0x05,  # max APDU: 1476
            invoke_id & 0xFF,
            READ_PROPERTY,
            0x0C,  # SD context tag 0, length 4: object-identifier
            (obj_id >> 24) & 0xFF,
            (obj_id >> 16) & 0xFF,
            (obj_id >> 8) & 0xFF,
            obj_id & 0xFF,
            0x19,  # SD context tag 1, length 1: property-identifier
            property_id & 0xFF,
        ]
    )
    npdu = bytes([0x01, 0x04])  # version, expecting reply
    payload = npdu + apdu
    length = 4 + len(payload)
    return bytes([0x81, 0x0A, (length >> 8) & 0xFF, length & 0xFF]) + payload


def _decode_object_id(raw: bytes) -> str:
    if len(raw) != 4:
        return raw.hex()
    value = struct.unpack(">I", raw)[0]
    obj_type = value >> 22
    instance = value & 0x3FFFFF
    return f"type={obj_type} instance={instance}"


def decode_application_tags(data: bytes) -> list:
    """Decode a flat sequence of BACnet application tags. Stops if the stream ends."""
    values = []
    i = 0
    while i < len(data):
        tag = data[i]
        i += 1
        tag_number = tag >> 4
        length = tag & 0x07
        if tag & 0x08 and length == 5:
            # opening/closing tag — application encoding doesn't use this;
            # treat as context and stop so we don't desync.
            break
        if length == 5:
            if i >= len(data):
                break
            ext = data[i]
            i += 1
            if ext == 254:
                if i + 1 >= len(data):
                    break
                length = struct.unpack_from(">H", data, i)[0]
                i += 2
            elif ext == 255:
                if i + 3 >= len(data):
                    break
                length = struct.unpack_from(">I", data, i)[0]
                i += 4
            else:
                length = ext
        if i + length > len(data):
            break
        raw = data[i : i + length]
        i += length
        if tag_number == 7:  # character string
            if raw:
                charset = raw[0]
                text = raw[1:]
                values.append(text.decode("utf-8" if charset == 0 else "latin1", "replace"))
            else:
                values.append("")
        elif tag_number == 2:  # unsigned
            values.append(int.from_bytes(raw or b"\x00", "big"))
        elif tag_number == 1:  # boolean
            values.append(bool(raw[:1] == b"\x01") if length == 0 else bool(raw and raw[-1]))
        elif tag_number == 4:  # real
            if len(raw) == 4:
                values.append(struct.unpack(">f", raw)[0])
            else:
                values.append(raw.hex())
        elif tag_number == 9:  # enumerated
            values.append(int.from_bytes(raw or b"\x00", "big"))
        elif tag_number == 12:  # object identifier
            values.append(_decode_object_id(raw))
        else:
            values.append(f"tag{tag_number}:{raw.hex()}")
    return values


def parse_npdu(packet: bytes):
    if len(packet) < 6 or packet[0] != 0x81:
        return None
    bvlc_len = struct.unpack(">H", packet[2:4])[0]
    body = packet[4:bvlc_len]
    if len(body) < 2:
        return None
    control = body[1]
    offset = 2
    if control & 0x20:
        if offset >= len(body):
            return None
        dlen = body[offset]
        offset += 1 + dlen + 1
    if control & 0x08:
        if offset >= len(body):
            return None
        slen = body[offset]
        offset += 1 + slen + 1
    return body[offset:]


def parse_iam(apdu: bytes):
    # Unconfirmed-Request (0x10), service I-Am (0).
    if len(apdu) < 6 or apdu[0] != 0x10 or apdu[1] != 0x00:
        return None
    if apdu[2] >> 4 != 12:
        return None
    length = apdu[2] & 0x07
    if length != 4 or len(apdu) < 3 + 4:
        return None
    value = struct.unpack(">I", apdu[3:7])[0]
    return {"object_type": value >> 22, "instance": value & 0x3FFFFF, "raw": apdu.hex()}


def listen(sock: socket.socket, seconds: float, accept_ip: str | None):
    packets = []
    end = time.time() + seconds
    while time.time() < end:
        sock.settimeout(max(0.05, end - time.time()))
        try:
            data, addr = sock.recvfrom(2048)
        except socket.timeout:
            break
        if accept_ip and addr[0] != accept_ip:
            continue
        packets.append((addr, data))
    return packets


def discover(host: str, timeout: float):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("0.0.0.0", 0))
    print(f"probing {host} from udp {sock.getsockname()[1]}")
    sock.sendto(whois_unicast(), (host, BACNET_PORT))
    broadcast = ".".join(host.split(".")[:3] + ["255"])
    try:
        sock.sendto(whois_broadcast(), (broadcast, BACNET_PORT))
    except OSError as exc:
        print(f"broadcast skipped: {exc}")
    packets = listen(sock, timeout, host)
    found = []
    for addr, data in packets:
        apdu = parse_npdu(data)
        iam = parse_iam(apdu) if apdu else None
        print(f"reply {addr} {data.hex()}")
        if iam and iam["object_type"] == DEVICE_OBJECT_TYPE:
            found.append((addr, iam))
            print(f"I-Am device instance {iam['instance']}")
    if not found:
        print("no I-Am from the thermostat")
    return sock, found


def read_device_properties(sock: socket.socket, host: str, instance: int, timeout: float):
    names = [
        (PROP_OBJECT_NAME, "object-name"),
        (PROP_MODEL_NAME, "model-name"),
        (PROP_FIRMWARE_REVISION, "firmware-revision"),
        (PROP_VENDOR_NAME, "vendor-name"),
        (PROP_DESCRIPTION, "description"),
        (PROP_OBJECT_LIST, "object-list"),
    ]
    for index, (prop, label) in enumerate(names, start=1):
        packet = read_property_request(instance, prop, index)
        sock.sendto(packet, (host, BACNET_PORT))
        replies = listen(sock, timeout, host)
        if not replies:
            print(f"{label}: no reply")
            continue
        for addr, data in replies:
            apdu = parse_npdu(data) or b""
            print(f"{label}: {decode_application_tags(apdu) or apdu.hex()}")


def tcp_timeout(host: str, port: int, timeout: float) -> str:
    sock = socket.socket()
    sock.settimeout(timeout)
    started = time.time()
    try:
        rc = sock.connect_ex((host, port))
    except OSError as exc:
        return str(exc)
    finally:
        sock.close()
    elapsed = time.time() - started
    if rc == 0:
        return "open"
    return f"closed-or-filtered errno={rc} after {elapsed:.2f}s"


SAMPLE_PORTS = (80, 443, 8080, BACNET_PORT)


def probe_host(host: str, timeout: float) -> dict:
    """Read-only TCP samples plus a unicast BACnet Who-Is. No writes."""
    print(f"\n== {host}")
    ports = {}
    for port in SAMPLE_PORTS:
        state = tcp_timeout(host, port, min(timeout, 1.0))
        ports[port] = state
        print(f"  tcp {port}: {state}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 0))
    print(f"  who-is from udp {sock.getsockname()[1]} to {host}:{BACNET_PORT}")
    sock.sendto(whois_unicast(), (host, BACNET_PORT))
    packets = listen(sock, timeout, host)
    instance = None
    for addr, data in packets:
        apdu = parse_npdu(data)
        iam = parse_iam(apdu) if apdu else None
        print(f"  reply {addr} {data.hex()}")
        if iam and iam["object_type"] == DEVICE_OBJECT_TYPE:
            instance = iam["instance"]
            print(f"  I-Am device instance {instance}")
    properties = {}
    if instance is not None:
        read_device_properties(sock, host, instance, timeout)
    else:
        print("  no I-Am (POSSIBLE / CURRENTLY DISABLED, not disproven)")
    sock.close()
    open_ports = [str(port) for port, state in ports.items() if state == "open"]
    return {
        "host": host,
        "bacnet": "yes" if instance is not None else "no",
        "instance": "" if instance is None else str(instance),
        "listening_ports": ",".join(open_ports) if open_ports else "none of 80,443,8080,47808",
        "model": "not exposed on LAN",
        "system_image": "not exposed on LAN",
        "ui_version": "not exposed on LAN",
        "control_engine": "not exposed on LAN",
        "device_management": "not exposed on LAN",
        "outbound_hosts": "not observed (probe does not sniff)",
    }


def print_comparison(rows: list[dict]) -> None:
    headers = [
        ("host", "host"),
        ("model", "exact model"),
        ("system_image", "system image"),
        ("ui_version", "UI version"),
        ("control_engine", "control engine"),
        ("device_management", "device management"),
        ("bacnet", "BACnet I-Am"),
        ("listening_ports", "listening ports"),
        ("outbound_hosts", "outbound hosts"),
    ]
    print("\n| " + " | ".join(label for _, label in headers) + " |")
    print("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        print("| " + " | ".join(row[key] for key, _ in headers) + " |")
    print(
        "\nVersion strings are on the thermostat under Support → software update "
        "(software version, ore version, ocp version, dm version). "
        "This probe cannot read them until the unit answers a local protocol."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only GLAS / BACnet probe")
    parser.add_argument(
        "hosts",
        nargs="*",
        default=["192.168.8.114"],
        help="one or more thermostat IPs; same checks run against each",
    )
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args()

    rows = [probe_host(host, args.timeout) for host in args.hosts]
    print_comparison(rows)
    if any(row["bacnet"] == "no" for row in rows):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
