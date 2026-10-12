# Tools

`probe_glas.py` is read-only. For each address it tries TCP 80, 443, 8080, and 47808, then sends one unicast BACnet Who-Is. If an I-Am names a Device object, it reads object-name, model-name, firmware-revision, vendor-name, description, and object-list. It never sends WriteProperty.

```
python3 probe_glas.py 192.168.8.114
python3 probe_glas.py 192.168.8.114 <second-unit-ip>
```

Exit status 2 means at least one host did not send an I-Am. That is what happened on the SiO2-10000 tested in October 2026. The stack can transmit, and it does not answer Who-Is while the enable flag is still at the schema default.

The probe cannot see the version strings. Those are on the panel under Support, software update.
