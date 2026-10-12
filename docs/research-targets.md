# Research targets

The aim is local control of a residential SiO2-10000: HVAC, temperature, humidity, VOC, CO2, occupancy, and eventually Home Assistant. The old LAN reports fit BACnet/IP. This firmware has the stack and does not answer Who-Is.

The flag, port, instance, and name are in `bacnet.md`. This panel does not show the page. The phone cannot write the flag over the LAN. `myglas.io` is gone, and the IoT Hub name the thermostat still calls will not take a certificate we can sign.

Another unit would move this faster than another probe of this one. A commercial `SiO2-01000`, `SiO2-01100`, or `SiO2-00100`, or an older residential firmware, if anyone has one. Useful things off it: whether Settings, General, BACNet exists; the enabled, port, instance, and name values if it does; the model number under Support, device info; and under Support, software update, the software version, ore version, ocp version, and dm version. A Who-Is / I-Am from a unit that answers, plus the Device object-list, is the actual map. That list is not in the phone app.

`tools/probe_glas.py` will read those Device properties after an I-Am. It will not write.

On the hardware side, a listen-only capture from a 3.3 V pad during boot would show whether Windows prints a console. Don't transmit until the pad is identified, and don't drive anything that follows the relays. Photos of silkscreen, including anything marked J13, belong in `../hardware/`.

The USB jack still has two easy checks, written up in `../hardware/usb.md`: a known data cable, and an OTG adapter with a peripheral plugged into the thermostat rather than the other way around.

Home Assistant waits on an I-Am. After that it is an ordinary BACnet client, object list first. The two frames we already have used device instance 1 and an unconfirmed COV notification. That is a hint, not the point list.

Repeating the DNS answer for `datap-iothub.azure-devices.net` will reproduce the port 8883 ClientHello and then `unknown_ca`. Another Who-Is, with the flag still at its default, should stay quiet.
