# Prior art

The project started from reports that a GLAS on the local network could be controlled with a UDP socket protocol aimed at HVAC points. That description matches BACnet/IP on UDP 47808. The phone app taken apart here does not implement it. The thermostat firmware does contain a BACnet stack. See `../docs/bacnet.md`.

The citations are thin. A link, the model number, the firmware version, and whether that unit answered Who-Is are what keep a commercial unit with the BACNet page from being mixed up with this residential one. Johnson Controls documented BACnet for the `SiO2-01000`, `SiO2-01100`, and `SiO2-00100`. The `SiO2-10000` tested here does not show the page.

The app notes come from `GLAS by JCI` 1.2.76, package `com.johnsoncontrols.glas`. The hosts and the BACnet settings schema in `../docs/android-app.md` were taken from that build.

Teardowns of other thermostats show UART pads and SPI flash. Those pinouts are not this board. Use the `OEJGLASWIFI` internal photos, or a picture of the board in front of you. See `fcc.md`.
