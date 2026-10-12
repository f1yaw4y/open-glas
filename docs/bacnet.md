# BACnet

On the SiO2-10000 that was tested, the stack is in the firmware and it does not answer on the LAN. The panel has no Settings, General, BACNet page, which matches Johnson Controls' residential documentation. The phone app still has the page in its settings schema, then hides it.

That schema is about 271 rows, taken from a UTF-16 blob in `jci.glas.common.remote` (`SettingsDataHelper.GetSettingsOptions`). The BACnet controls are ordinary rows in it, not a separate commercial object.

The enable toggle is key `b5a2e9c0-a034-43c9-8c50-48bf4b80e0ed`, text key `settings-bacnet-on`, boolean, schema default `"False"`. Its parent page is `15f69972-77e1-431a-9221-f0a3a5e7928f` (`BACNet`), under General `a84238d5-dc48-4303-bc43-673278884990`. Port is `a824369c-00be-43bf-bb8b-c0f9f5c55745` and instance is `e10394da-c144-4eba-97cb-996c5697ac2f`, both integers with a numeric keyboard and no default. Name is `f70e43c5-0497-4ccd-96cf-82809ebb66f7`, plain text, no default.

On the toggle, `devicePermission` is read. Mobile and web permissions are empty, while settings the phone is meant to edit are create/read/update. `CloudService.ApplyPendingChangesToSettingsDataHelper` finds the menu page GUID and blanks its mobile permission, so the running phone drops the page.

`DataTypeStrings` also has getters returning `BacnetEnabled`, `BacnetMenuEnabled`, `BacnetDeviceId`, `BacnetPort`, and `BacnetName`. Nothing calls them. `GeneralSettings.BACnet` is a constant equal to the menu page GUID, not the toggle, and nothing else reads it.

None of the extracted assemblies contain the protocol itself. No `Who-Is`, `I-Am`, `ReadProperty`, `WriteProperty`, `ReadPropertyMultiple`, `Object_List`, `Present_Value`, `BVLC`, `NPDU`, `APDU`, `47808`, or `0xBAC0`.

The old way to change the flag was the generic device update, not a BACnet write and not SignalR. `PUT https://myglas.io/api/device/{id}?api-version=3.0` with a `DeviceDetailsDto`. PascalCase, nulls omitted, and booleans as the strings `True` and `False`. The flag sits in `DeviceState.Settings` as that GUID and `"True"`. The app's matching read is GET on the same URL. `myglas.io` does not resolve, the thermostat does not query it, and the unit is not listening on TCP 80, 443, 8080, or 47808, so the body cannot be posted at the device.

What the thermostat did send was two BACnet/IP datagrams, about 30 seconds after DHCP on a factory-reset boot. Both were UDP 47808, BVLC original-broadcast (`81 0b`), and both were aimed at `192.255.255.254` via the gateway rather than the subnet broadcast.

At 20:20:25 UTC, 7 bytes: network message `0x12`, What-Is-Network-Number.

At 20:20:27 UTC, 52 bytes: an unconfirmed COV notification. Process id 0. Initiating device and monitored object are both device instance 1. Time remaining 0. Property 112, `system-status`, enumerated value 2, `download-required`. Properties 203 and 196 are in the same list.

Nothing came back. The enable GUID is not in the cleartext, and there is no I-Am. A later unicast Who-Is (`810a000801001008`) was visible on the air, addressed to the thermostat, and still got no reply. `download-required` lines up with a Windows BITS transfer that started a few minutes later and then finished. Who-Is after the download was quiet too.

Johnson Controls' GLAS BACnet PICS, dated 10 Sep 2019, names models `SiO2-01000`, `SiO2-01100`, and `SiO2-00100`. Application software `1.1.2019.07.23.0.1`, firmware revision `1.1.879.9`, protocol revision 15. Those are the commercial model numbers. The PICS describes the usual server behavior for them, including ReadProperty and Who-Is. `SiO2-10000` is not on the list. This residential unit still has enough of the stack to emit the two frames above. In the configuration we tested, it does not answer.
