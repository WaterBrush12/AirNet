## To-Do 

- [ ] **Flask/FastAPI Backend**
  - Create a backend using FastAPI.
  - Add a single endpoint: `POST /air` that accepts JSON requests.
  - For initial development, simply log every received request to the terminal.
  - Example request body:
    ```json
    {
      "uniqueid": "esp32_01",
      "particulateMatter": { "pm2_5": 12.3, "pm10": 25.6 },
      "volatileOrganicCompounds": 123,
      "gases": { "CO": 0.4, "NO2": 0.02, "O3": 0.03 }
    }
    ```

- [ ] **ESP32 Firmware**
  - Hardcode Wi-Fi credentials and backend server URL for development.
  - Every 4 seconds, send a JSON payload to the `/air` endpoint.
  - Initially, use fake sensor data until real sensors are integrated.
  - Make sure the JSON matches the backend’s expected format.

- [ ] **Web Dashboard & Persistent Storage**
  - Once the backend reliably receives requests, implement a simple web dashboard (no authentication needed) to display:
    - A list of currently online ESP32 devices.
    - An ESP is considered offline if it hasn’t sent data in the last 10 seconds.
  - Use SQLite for any persistent storage (e.g., logging historic data).
  - Dashboard should automatically update device statuses in near real-time.




# AirNet

Trying to solve air pollution problems with minimum resources.


## My Background

As someone born in Tehran, the capital city of Iran, I've lived with the health and frustration  
of extreme air pollution. As of June 4, 2025, Tehran is the **4th most air-polluted**  
city in the entire world. I remember times when schools — and even offices — would close  
because of the sheer amount of pollution in the air.


## My Goal

Build a low-cost, scalable, and open-source air quality monitoring system.


## What's Included in This Repository

- Hardware blueprints and schematics  
- Microcontroller code for the sensors, and data logging system  
- Cost breakdown and list of material providers  
- Documentation on my research into air pollution  
- A log documenting the full building process  
- Real photos of prototypes and deployed units

## What Exactly is Air Pollution?

Air pollution is the presence of harmful substances in the atmosphere -- such as particulate matter, gases, or chemichals -- that degrade air quality and pose risks to human health. ecosystems, and the climate.

Click [here](research.md#airnet-research-paper) to see my research on air pollution.

## Current Status

Planning and research phase.

