# Rainwater Monitoring and Management System

## Project Overview

The Rainwater Monitoring and Management System is an advanced IoT-based solution designed to provide comprehensive, real-time insights into rainfall patterns and water collection processes. By integrating sophisticated sensors, a powerful ESP32 microcontroller, and an intuitive web interface, the system offers precise tracking and analysis of rainwater harvesting parameters.

## System Architecture and Components

### Hardware Components

1. **ESP32 Microcontroller**
   - Dual-core processor (240MHz)
   - Built-in Wi-Fi and Bluetooth capabilities
   - I2C communication support
   - GPIO pins for sensor interfacing

2. **Sensors**
   - **Tipping Bucket Rainfall Sensor (SKU: SEN0575)**
     * Measurement Range: 0-9999mm
     * Resolution: 0.28mm per tip
     * Communication: I2C and UART
     * Operating Temperature: -40°C to 85°C
     * Features: Automatic drainage, high platform compatibility

   - **YFS-201 Water Flow Sensor**
     * Measurement Method: Hall effect sensor
     * Output: Pulse signals proportional to water flow
     * Flow Rate Range: 1–30 L/min
     * Working Voltage: 5–24V

3. **Auxiliary Components**
   - Gravity I2C Communication Module
   - Type-B USB Cable
   - 5V Adapter

### Software Components

#### Key Functionalities
- Real-time data acquisition
- Data processing and calculation
- Web server hosting
- User interface for data visualization

## Technical Implementation

### Sensor Data Acquisition
- **Rainfall Sensor**: Measures rainfall through a tipping bucket mechanism
  * Each sensor tip represents 0.28mm of rainfall
  * Transmits data via I2C communication

- **Water Flow Sensor**: Tracks water flow rate
  * Generates pulses proportional to flow volume
  * Calculates flow rate and total water volume

### Data Processing
The system processes raw sensor data to compute:
- Cumulative rainfall
- Hourly rainfall intensity
- Total water collected
- Instantaneous flow rate

### Web Interface
- Hosted on ESP32 microcontroller
- Accessible via Wi-Fi network
- Real-time metrics display
- Features:
  * Current rainfall information
  * Hourly rainfall trends
  * Total water volume
  * Flow rate visualization
  * Data reset functionality

## Network Configuration
- SSID: `RainfallMonitor`
- Access Point IP: `192.168.4.1:8080`

## Setup and Deployment

### Hardware Setup
1. Connect sensors to ESP32 using specified GPIO pins
2. Ensure proper power supply using 5v adapter and a Type-B USB Cable
3. Mount sensors in appropriate outdoor locations

### Software Setup
1. Flash ESP32 with MicroPython firmware
2. Install required libraries
3. Upload `main.py` script
4. It's ready and visit the IP Address `190.168.4.1:8080` for the webpage.

## Calibration and Accuracy

### Rainfall Sensor
- Preset resolution: 0.28mm per tip
- Manual calibration support through software configuration

### Water Flow Sensor
- Configurable calibration factor
- Default: 7.5 pulses per liter

## Possible Enhancements
1. Cloud Integration
   - Remote data access
   - Trend analysis using platforms like AWS or Google Cloud

2. Advanced Analytics
   - Machine learning for rainfall prediction
   - Water usage trend analysis

3. Mobile Application
   - Real-time monitoring
   - Push notifications
   - Comprehensive data visualization

4. Power Optimization
   - Solar power integration

## Troubleshooting

### Common Issues
- No sensor data
- Web interface not loading
- Inaccurate readings

### Recommended Solutions
- Verify physical connections
- Check power supply
- Recalibrate sensors
- Confirm network settings

## Technical Specifications
- Microcontroller: ESP32 (Dual-core, 240MHz)
- Communication: Wi-Fi, I2C
- Data Storage: Temporary in-memory logging
- Update Frequency: 5-second intervals
- Maximum Logged Readings: 10


## Design
![Design]("images/design.png")


##Block Diagram

!("images/Block-Diagram.png")

##Schematic Diagram

!("images/Schematic-Diagram.png")
