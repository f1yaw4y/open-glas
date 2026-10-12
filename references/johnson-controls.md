# Johnson Controls documents

GLAS is discontinued. The support page says the SIO2-10000 and the GLAS by JCI app no longer get feature updates, and that the thermostat itself keeps working as a local thermostat. The cloud shutdown this project is about is March 2026, which is when `myglas.io` stopped resolving.

Technical bulletin LIT-12012959 covers the SiO2-10000 and the SiO2-00000. Power is 3.5 VA at 24 VAC, from a C-wire or the included adapter. The battery is 160 mAh at 3.7 V. Wi-Fi is 802.11b/g/n, 2.4 GHz, 20 MHz. Bluetooth is 4.0 in the bulletin; a 2018 product sheet says Bluetooth 4.1 BLE. The display is a translucent OLED, about 5.9 inches, 16:9. The setpoint range is 40 to 100 F (4 to 38 C).

Bulletin: https://docs.johnsoncontrols.com/bas/r/Johnson-Controls/en-US/GLAS-Smart-Thermostat-Technical-Bulletin

2018 sheet: https://glas.johnsoncontrols.com/wp-content/uploads/2018/01/GLAS_technical_specs.pdf

Support: https://glas.johnsoncontrols.com/support/

The BACnet PICS is dated 10 Sep 2019. Product name GLAS Thermostat. Models `SiO2-01000`, `SiO2-01100`, and `SiO2-00100`. Application software `1.1.2019.07.23.0.1`. Firmware revision `1.1.879.9`. BACnet version 1, revision 15.

`SiO2-10000` is not on that list. The PICS is still the public description of what the commercial firmware was willing to expose. The residential unit tested here transmitted BACnet/IP and did not answer Who-Is. See `../docs/bacnet.md`.
