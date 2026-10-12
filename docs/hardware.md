# Hardware

Public specs for the SiO2-10000 are 24 VAC at 3.5 VA, a 160 mAh 3.7 V pack, 2.4 GHz 802.11b/g/n, Bluetooth 4.0, and a translucent OLED. They do not mention a serial console or a USB device port.

The panel is running Windows. The DHCP vendor class on boot was `MSFT 5.0`, and the background download identified itself as `Microsoft BITS/7.8`. A local change to the BACnet flag would have to land in that image. Nothing on the LAN that we probed is a way into it.

The micro USB jack was plugged into a Linux machine with `dmesg` and `udevadm monitor` running. No attach event, including across a boot. Notes on that are in `../hardware/usb.md`.

UART has not been hooked up. The FCC internal photos for `OEJGLASWIFI` are the public picture of the board, and no pinout has been taken off them yet. See `../references/fcc.md` and `../hardware/j13.md`.

If the case is opened, listen before sending anything. A 3.3 V USB-TTL adapter is the right level. A PC serial port is RS-232 and will wreck a 3.3 V pad. Boot text would be the Windows side, and a login prompt is the interesting case. A signal that only moves when the relays click belongs to the HVAC controller and should be left alone.

Photos can go in `../hardware/pcb-photos/`.
