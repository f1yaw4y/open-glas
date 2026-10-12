# Android app

`GLAS by JCI` 1.2.76, package `com.johnsoncontrols.glas`, is a Xamarin app. The C# is not in the dex file. It is zlib-compressed .NET assemblies packed into `libmonodroid_bundle_app.so` by Mono's mkbundle.

Those assemblies were extracted and read with dnfile and dncil. Method bodies were pulled from the PE at each method's RVA and scanned for string loads and calls. User strings came from the `#US` heap. That is what connects a hostname or a settings GUID to a specific method, instead of a loose string somewhere in the binary.

`classes.dex` was only checked for sockets. `Bluetooth` and `NsdManager` show up there because `Mono.Android` wraps the whole Android API. The GLAS assemblies themselves do not reference `Bluetooth`, `NsdManager`, `UdpClient`, or `System.Net.Sockets`. The manifest asks for internet, camera, storage, network state, wifi state, vibrate, and package install. No Bluetooth permission and no location permission.

The production URLs live in `CloudEnvironmentExtensions`. The API is `https://myglas.io/api`. SignalR is `https://myglas.io/notification`. Identity is `https://api.digitalvault.cloud/idm/ims`.

REST goes through `GlasRestClient` / `CloudConnector`. The path pieces, recovered from string loads in the async methods and followed by `?api-version=3.0`, are `user`, `user/forgotPassword`, `user/resetPassword`, password update, `location`, `device`, `pair`, `account`, `role`, `mpc`, invitation invite and resend, `DealerInfo` + `locations`, and `weather` + `device`.

SignalR hub names in `jci.glas.common.contracts` are `SensorHub`/`SensorUpdate`, `DeviceHub`/`DeviceUpdate`, `DeviceHubV2`/`DeviceUpdateV2`, `UserHub`/`UserUpdate`, and `DeviceConnectionStatusHub`/`ConnectionStatusChanged`. The hub URI has to be https. The access token is passed as `access_token`.

Login is OAuth2 against `{ims}/connect/token`. `TokenOptionsSupplier` has three client ids: `pairing.device`, `pairing.user.local`, and `glasdevice`. Client secrets are compiled in next to them and are not copied here. Pairing collects a 6-digit key and sends it to the cloud. There is no handshake with the thermostat.

`Microsoft.Azure.Devices.Client` is in the bundle, and no GLAS method calls it. `PrimaryAzureIotHubKey` is only a field the connector can hold. `jci.be.glas.device.messages` is an Azure Storage queue DTO (`DeviceUpdated` / `DeviceUpdatedV2`), not something the phone sends to the stat. Models are Newtonsoft.Json. There is no protobuf schema and no device certificate in the APK. The bundled assets are fonts.

`192.168.1.230` appears in `VirginDevicePropertyValues` next to stub data (`GlasAlpha1`, a documentation IPv6 address, zip `00000`). It is not a discovery address.

The names the app uses for sensors and commands are the strings returned by `DataTypeStrings` getters. Reads and writes go through `ReadReportedValue`, `WriteReportedValue`, `GetDeviceStatus`, and `UpdateDeviceStatus`. These are cloud fields, not BACnet object numbers: `TemperatureF`, `RelativeHumidty` (spelled that way on the device property; some DTOs say `RelativeHumidity` or `Humidity`), `OccupancyState`, `OccupancySensorEnabled`, `UserSetOccupancy`, `CurrentVoc`, `VocAirQuality`, `CurrentCO2`, `CO2AirQuality`, `CurrentIndoorAirQuality`, `OutdoorTemperature`, `OutdoorHumidity`, `HeatingOn`, `CoolingOn`, `FanOn`, `OverallSystemState`, `HoldOn`. Outdoor temperature and humidity come from the weather service, not the onboard sensor.

`ModelNumberParser` in `jci.glas.common.util` expects `SiO2`, one hyphen, and a suffix. More than two pieces returns null. A suffix shorter than five digits is replaced with the literal `10000`. Digit 2 is ignored. Digit 0 is residential (`SiO2-10000`) or commercial (`SiO2-00000` and the others). Digit 1 is split system or fan coil. Digit 3 is the screen. Digit 4 is region. The only callers use this to set an FCU flag. They do not look at BACnet, and the BACnet rows in the settings schema have no model, SKU, or firmware check of their own.

The version strings that exist in the schema are under Support, software update: software version, ore version, ocp version, and dm version. "System image", "UI version", and "control engine" do not appear. The phone leaves that page's mobile permission empty, so those strings have to be read off the panel.
