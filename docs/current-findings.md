# Current findings

This is one residential SiO2-10000, looked at on 2026-10-11. Wi-Fi MAC `00:10:8d:06:9f:ee`. After a factory reset the DHCP hostname was `GLAS-108D069FEE` and the vendor class was `MSFT 5.0`.

It joins 2.4 GHz Wi-Fi, takes a lease, and answers ARP. It does not accept TCP connections on any port we tried, and it does not answer BACnet Who-Is.

The phone side is `GLAS by JCI` 1.2.76. Sensor reads and HVAC commands in that app go to Johnson Controls' cloud, not to the thermostat. `myglas.io` and `glas.johnsoncontrols.com` did not resolve. `api.digitalvault.cloud` did, and `https://api.digitalvault.cloud/idm/ims` returned 404. How the app was taken apart is in `android-app.md`.

The thermostat's own boot, decrypted after it reassociated, is a different picture. About every 10 seconds it looks up `datap-iothub.azure-devices.net` and gets NXDOMAIN. When that name was answered on the LAN, it opened TLS 1.2 to port 8883. A certificate we signed for the same name was rejected with `unknown_ca`, and no MQTT login followed. Alongside that it keeps a real TLS session to `api.digitalvault.cloud` (certificate `*.digitalvault.cloud`, Johnson Controls, Inc.). A few minutes after boot it also pulled a Windows update in the background, User-Agent `Microsoft BITS/7.8`, for about five minutes, with no update screen left on the panel. It never looked up `myglas.io`.

BACnet is in the firmware even so. About 30 seconds after DHCP it sent two UDP/47808 frames, both to `192.255.255.254` instead of the subnet broadcast. One was What-Is-Network-Number. The other was an unconfirmed COV notification for device instance 1, with `system-status` set to `download-required`. A unicast Who-Is we could see on the air got no reply. Settings, General, BACNet is not on this panel. Johnson Controls' own BACnet conformance statement lists the commercial models `SiO2-01000`, `SiO2-01100`, and `SiO2-00100`, not this `SiO2-10000`. The phone schema still carries the enable flag for every model it knows, with no model check. Detail is in `bacnet.md`.

Ports that timed out, errno 11 and no RST: 22, 80, 135, 139, 443, 445, 1883, 3389, 5671, 5985, 5986, 8080, 8081, 8443, 8883. The micro USB jack produced no USB attach on a Linux host, including across boot.
