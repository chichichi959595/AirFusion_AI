# Arduino Uno Serial Firmware

Arduino Uno does not have built-in Wi-Fi, so it cannot use the ESP32 `HTTPClient.h`
firmware. This version reads PMS5003T data and prints JSON over USB Serial.
A Python bridge on the laptop forwards that JSON to AirFusion AI.

## Wiring

```text
PMS5003T VCC -> Uno 5V
PMS5003T GND -> Uno GND
PMS5003T TX  -> Uno D10
PMS5003T RX  -> leave disconnected
```

## Upload

Open this sketch in Arduino IDE:

```text
firmware/arduino_uno_serial/AirFusionUnoSerial/AirFusionUnoSerial.ino
```

Select:

```text
Tools -> Board -> Arduino Uno
Tools -> Port  -> your COM port
```

Upload, then open Serial Monitor at `115200`.

## Forward To Backend

Start the AirFusion backend first:

```powershell
cd "C:\Users\Hayden Ho\Desktop\coding\AirFusion_AI"
& "C:\Users\Hayden Ho\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0
```

In another PowerShell, install pyserial once:

```powershell
& "C:\Users\Hayden Ho\AppData\Local\Programs\Python\Python311\python.exe" -m pip install pyserial
```

Then run the bridge. Replace `COM7` with your Arduino port:

```powershell
cd "C:\Users\Hayden Ho\Desktop\coding\AirFusion_AI"
& "C:\Users\Hayden Ho\AppData\Local\Programs\Python\Python311\python.exe" -m app.serial_bridge --port COM7
```

If you are not sure which port is the Uno:

```powershell
& "C:\Users\Hayden Ho\AppData\Local\Programs\Python\Python311\python.exe" -m app.serial_bridge --list-ports
```

Close Arduino IDE Serial Monitor before running the bridge. Only one program can
open the Uno COM port at a time.

When it works, you will see serial JSON from the Uno and `POST ok` messages.
