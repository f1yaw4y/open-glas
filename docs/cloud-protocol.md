# Cloud protocol

The phone and the thermostat do not call the same place.

The app's API is `https://myglas.io/api`, with SignalR at `https://myglas.io/notification` and identity at `https://api.digitalvault.cloud/idm/ims`. Tokens come from `{ims}/connect/token`. A settings change, BACnet included, is an HTTP PUT of a `DeviceDetailsDto` to `/device/{id}?api-version=3.0`. SignalR then pushes the result on the device hubs. There is no BACnet-specific hub. On 2026-10-11 `myglas.io` and `glas.johnsoncontrols.com` did not resolve. The identity URL did, and returned HTTP 404.

The app ships `Microsoft.Azure.Devices.Client` and a `glasdevice` OAuth client, but no GLAS method opens an IoT Hub session. The phone is not speaking MQTT.

The thermostat, on a factory-reset boot, never looked up `myglas.io`. The name it repeats is `datap-iothub.azure-devices.net`, about every 10 seconds. Public DNS is NXDOMAIN, so in normal use no TCP connection starts.

Giving that name a LAN answer changed that immediately. The thermostat opened TLS 1.2 to port 8883 within about a second and kept retrying. That port is MQTT over TLS. The ClientHello was 186 bytes, SNI `datap-iothub.azure-devices.net`, and it carried no client certificate. The first test stopped there, so there was no MQTT CONNECT to read.

A second test completed the server side of the handshake with a certificate whose name was the hub, signed by a CA created for the test. The thermostat closed it with TLS alert `unknown_ca`. It is checking the chain against the trust store it already has. A public CA will not issue a certificate for Azure's name, so the MQTT login, if the device has one, stays behind that check.

`api.digitalvault.cloud` is the session that did stay up. The thermostat resolved it to `40.67.159.146` and kept TLS 1.2 on port 443, cipher `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`. The certificate is `CN=*.digitalvault.cloud`, Johnson Controls, Inc., also covering `digitalvault.cloud`, expiring 2027-01-19. The client offered HTTP/2 and HTTP/1.1. Application data continued about every 30 seconds early on. The HTTP inside the session was not visible. This is the same host the phone uses for identity.

A few other names from that boot did not resolve: `glasudeviceuilogs.blob.core.windows.net`, `gate.hockeyapp.net`, and `v10.vortex-win.data.microsoft.com`. The bulk of the bytes were not GLAS at all. They were a Windows update over cleartext HTTP, User-Agent `Microsoft BITS/7.8`, plus `login.live.com` and the usual Microsoft update and notification hosts. That ran about five minutes and stopped.

Answering `myglas.io` locally would only matter to the phone. Answering the IoT Hub name gets the thermostat as far as port 8883, and then a certificate we can sign is refused. Intercepting `api.digitalvault.cloud` would mean breaking a session that already has a Johnson Controls certificate. The BACnet switch is still the GUID in `bacnet.md`, and on this firmware both ways of delivering it stop on a certificate the device already trusts.
