# Open GLAS

Johnson Controls discontinued GLAS cloud services in March 2026, disabling remote functionality on otherwise functional hardware. This project aims to restore fully local control of the GLAS SiO2-10000, ideally including HVAC control, temperature, humidity, VOC, CO2 and occupancy data, with eventual Home Assistant support.

The residential firmware exposes no known LAN control service. However, the original GLAS software contains configuration for BACnet/IP, including an enable flag, port, instance ID and device name. Historical reports indicate at least one residential GLAS was successfully controlled over the LAN using a UDP object/property protocol consistent with BACnet.

So far this is notes from one SiO2-10000. The phone app never talks to the thermostat on the LAN. The firmware does contain a BACnet stack: after a factory reset it sent two BACnet frames, then ignored Who-Is. There is no BACNet page on the panel. The cloud call that used to set the enable flag is dead. The host the thermostat still looks up, `datap-iothub.azure-devices.net`, is MQTT over TLS on port 8883, and a certificate signed here was rejected with TLS alert `unknown_ca`.

The write-up is split up under `docs/`. `tools/probe_glas.py` is a read-only Who-Is; it only reads the Device object after an I-Am. `hardware/` is the USB jack, connector notes, and a place for board photos. `references/` is the FCC filing, Johnson Controls docs, and the earlier LAN-control reports. Packet captures from the test network will be included in the near future once I capture again on an isolated network
