# Network

One residential SiO2-10000, on 2026-10-11. No BACnet WriteProperty, and no other message that would change state. Wi-Fi passphrases are not written down here.

`tools/probe_glas.py` tries TCP 80, 443, 8080, and 47808, then sends one unicast Who-Is to UDP 47808. If an I-Am names a Device object, it reads object-name, model-name, firmware-revision, vendor-name, description, and object-list. It does not write.

On this unit every TCP connect timed out: errno 11, about a second, no RST. Who-Is got no I-Am. The same Who-Is was sent again after the factory reset while a monitor-mode capture was running. The frame was on the air, addressed to the thermostat, and there was still no BACnet reply. A wider connect sweep timed out the same way for 22, 135, 139, 445, 1883, 3389, 5671, 5985, 5986, 8081, and 8443. ARP does work. The OUI `00:10:8D` is Johnson Controls.

Hearing the thermostat's own traffic took a second radio. A promiscuous capture on the laptop that is already associated only sees that laptop. The extra adapter was a TP-Link Archer T2U Nano (`2357:011e`). Kernel 6.12 has no in-tree driver for it, so `88XXau` from aircrack-ng/rtl8812au was built and loaded. It was left unmanaged, in monitor mode, on channel 6 (2437 MHz), which is where this unit sits. tcpdump ran from a small container because the host could not open a raw socket. The built-in radio stayed associated the whole time.

About 10 minutes of idle, before the factory reset, was a few small encrypted frames a minute toward the gateway, plus an 802.11 null about every 30 seconds. That file had no handshake, so the payloads stayed encrypted. A search of what was in the clear found no `myglas`, `azure`, `BACNet`, or the enable GUID.

The factory-reset restart was captured from before association through the following minutes. The thermostat probed, associated, and did the 4-way handshake. airdecap-ng decrypted the data frames as WPA2-CCMP. The hosts and the two BACnet frames are written up in `cloud-protocol.md` and `bacnet.md`. Most of the file's size is the Windows BITS download, not the GLAS service. The pcaps themselves are not in this repo. See `../captures/README.md`.

After that download stopped, a 90 second listen looked like the earlier idle capture. The two DNS tests of `datap-iothub.azure-devices.net` came after that. Both put the thermostat's gateway ARP entry back, and removed the temporary DNS answer, when they finished.
