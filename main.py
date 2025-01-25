from machine import Pin, SoftI2C , Timer
import network
import socket
import json
import time
from  time import sleep

class RainfallSensor:
    # Register addresses
    I2C_REG_PID = 0x00
    I2C_REG_VID = 0x02
    I2C_REG_VERSION = 0x0A
    I2C_REG_TIME_RAINFALL = 0x0C
    I2C_REG_CUMULATIVE_RAINFALL = 0x10
    I2C_REG_RAW_DATA = 0x14
    I2C_REG_SYS_TIME = 0x18
    I2C_REG_RAW_RAIN_HOUR = 0x26
    I2C_REG_RAW_BASE_RAINFALL = 0x28

    def __init__(self, i2c=SoftI2C(scl=22, sda=21, freq=400000), addr=0x1D):
        """
        Initialize rainfall sensor
        
        :param scl_pin: SCL pin number
        :param sda_pin: SDA pin number
        :param freq: I2C bus frequency
        :param addr: I2C device address
        """
        self._i2c = i2c
        self._addr = addr
        self.vid = 0
        self.pid = 0

    def _read_register(self, reg, length):
        """
        Read registers via I2C
        
        :param reg: Register address
        :param length: Number of bytes to read
        :return: List of register values
        """
        try:
            return list(self._i2c.readfrom_mem(self._addr, reg, length))
        except:
            return [0] * length

    def _write_register(self, reg, data):
        """
        Write registers via I2C
        
        :param reg: Register address
        :param data: Data to write
        :return: Boolean indicating success
        """
        try:
            self._i2c.writeto_mem(self._addr, reg, bytes(data))
            time.sleep(0.05)
            return True
        except:
            return False

    def begin(self):
        """
        Attempt to communicate with sensor and verify device
        
        :return: Boolean indicating communication success
        """
        return self.get_pid_vid()

    def get_pid_vid(self):
        """
        Get Product and Vendor ID
        
        :return: Boolean indicating valid sensor
        """
        try:
            list_data = self._read_register(self.I2C_REG_PID, 4)
            self.pid = list_data[0] | (list_data[1] << 8) | ((list_data[3] & 0xC0) << 10)
            self.vid = list_data[2] | ((list_data[3] & 0x3F) << 8)
            return (self.vid == 0x3343) and (self.pid == 0x100C0)
        except:
            return False

    def get_firmware_version(self):
        """
        Get firmware version
        
        :return: Firmware version as string
        """
        try:
            list_data = self._read_register(self.I2C_REG_VERSION, 2)
            version = list_data[0] | (list_data[1] << 8)
            return f"{version >> 12}.{(version >> 8) & 0x0F}.{(version >> 4) & 0x0F}.{version & 0x0F}"
        except:
            return "0.0.0.0"

    def get_sensor_working_time(self):
        """
        Get sensor working time
        
        :return: Working time in hours
        """
        try:
            list_data = self._read_register(self.I2C_REG_SYS_TIME, 2)
            working_time = list_data[0] | (list_data[1] << 8)
            return working_time / 60.0
        except:
            return 0.0

    def get_rainfall(self):
        """
        Get cumulative rainfall
        
        :return: Cumulative rainfall in millimeters
        """
        try:
            print("By https://github.com/rushikatabathuni/")
            list_data = self._read_register(self.I2C_REG_CUMULATIVE_RAINFALL, 4)
            rainfall = list_data[0] | (list_data[1] << 8) | (list_data[2] << 16) | (list_data[3] << 24)
            return rainfall / 10000.0
        except:
            return 0.0

    def get_rainfall_time(self, hour):
        """
        Get cumulative rainfall within specified time
        
        :param hour: Specified time (valid range is 1-24 hours)
        :return: Cumulative rainfall in millimeters
        """
        print("By https://github.com/rushikatabathuni/")
        if hour > 24:
            return 0.0
        
        try:
            # Write hour to rain hour register
            self._write_register(self.I2C_REG_RAW_RAIN_HOUR, [hour])
            
            # Read cumulative rainfall for specified time
            list_data = self._read_register(self.I2C_REG_TIME_RAINFALL, 4)
            rainfall = list_data[0] | (list_data[1] << 8) | (list_data[2] << 16) | (list_data[3] << 24)
            return rainfall / 10000.0
        except:
            return 0.0

    def get_raw_data(self):
        
        """
        Get raw tipping bucket count
        
        :return: Number of tip counts
        """
        try:
            print("By https://github.com/rushikatabathuni/")
            list_data = self._read_register(self.I2C_REG_RAW_DATA, 4)
            return list_data[0] | (list_data[1] << 8) | (list_data[2] << 16) | (list_data[3] << 24)
        except:
            return 0

    def set_rain_accumulated_value(self, value):
        """
        Set the rainfall accumulation value
        
        :param value: Rainfall accumulation value in millimeters
        :return: Boolean indicating success
        """
        try:
            print("By https://github.com/rushikatabathuni/")
            data = int(value * 10000)
            return self._write_register(self.I2C_REG_RAW_BASE_RAINFALL, 
                                        [data & 0xFF, (data >> 8) & 0xFF])
        except:
            return False
    






# Initialize  variables
pulse_count = 0
flow_rate = 0.0
total_volume = 0.0
calibration_factor = 7.5
flow_sensor = Pin(4, Pin.IN)
flow_sensor_enabled = False
MAX_VALUES = 10

class DataLogger:
    def __init__(self):
        self.rainfall_values = []
        self.hour_rainfall_values = []
        self.total_volume_values = []
        self.flow_rate_values = []
        self.tips=0
        self.working_time=0.00

    def save_reading(self, rainfall, hour_rainfall, total_volume,flow_rate,tips,working_time):
        self.tips=tips
        self.working_time=working_time
        if len(self.hour_rainfall_values)>0:
            self.rainfall_values.append(rainfall)
            self.hour_rainfall_values.append(hour_rainfall - self.hour_rainfall_values[-1])
            self.total_volume_values.append(total_volume)
            self.flow_rate_values.append(flow_rate)
        else:
            self.rainfall_values.append(rainfall)
            self.hour_rainfall_values.append(hour_rainfall)
            self.total_volume_values.append(total_volume)
            self.flow_rate_values.append(flow_rate)
        
        if len(self.rainfall_values) > MAX_VALUES:
            self.rainfall_values.pop(0)
            self.hour_rainfall_values.pop(0)
            self.total_volume_values.pop(0)
            self.flow_rate_values.pop(0)

    def get_readings(self):
        return {
            'rainfall': self.rainfall_values,
            'hour_rainfall': self.hour_rainfall_values,
            'total_volume': self.total_volume_values,
            'flow_rate': self.flow_rate_values,
            'tips' : self.tips,
            'working_time':self.working_time
        }

def pulse_counter(pin):
    global pulse_count
    if flow_sensor_enabled:
        pulse_count += 1

flow_sensor.irq(trigger=Pin.IRQ_RISING, handler=pulse_counter)

def calculate_flow_rate(timer):
    global pulse_count, flow_rate, total_volume
    flow_rate = (pulse_count / calibration_factor)
    total_volume += (flow_rate / 60)
    
    
    pulse_count = 0

def get_readings_json(data_logger):
    readings = data_logger.get_readings()
    return json.dumps(readings)

def web_page():
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Water Monitoring System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: system-ui, -apple-system, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            padding: 2rem;
            line-height: 1.5;
            max-width: 1600px;
            margin: 0 auto;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }

        .title-section {
            flex-grow: 1;
            text-align: center;
        }

        h1 {
            font-size: 2.25rem;
            font-weight: 700;
            color: #2563eb;
            margin-bottom: 0.5rem;
        }

        .subtitle {
            color: #64748b;
            font-size: 1.1rem;
        }

        .reset-button {
            background-color: #dc2626;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .reset-button:hover {
            background-color: #b91c1c;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .metric-card {
            background: white;
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }

        .metric-card:hover {
            transform: translateY(-2px);
        }

        .metric-label {
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            margin-bottom: 0.5rem;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #059669;
            display: flex;
            align-items: baseline;
            gap: 0.5rem;
        }

        .metric-unit {
            font-size: 1rem;
            font-weight: normal;
            color: #64748b;
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 2rem;
        }

        .chart-container {
            background: white;
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .chart-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #1e293b;
        }

        canvas {
            width: 100%;
            height: 250px;
            background: #f8fafc;
            border-radius: 0.5rem;
        }

        @media (max-width: 1400px) {
            .metrics-grid {
                grid-template-columns: repeat(3, 1fr);
            }
        }

        @media (max-width: 1024px) {
            .metrics-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .charts-grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 640px) {
            .metrics-grid {
                grid-template-columns: 1fr;
            }
            .header {
                flex-direction: column;
                gap: 1rem;
            }
            .reset-button {
                width: 100%;
            }
            body {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title-section">
            <h1>Water Monitoring System by <a href="<a>https://github.com/rushikatabathuni/</a>" target="_blank">Rushi</a></h1>
            <p class="subtitle">Real-time rainfall and water flow analytics</p>
        </div>
        <button class="reset-button" onclick="resetReadings()">Reset Readings</button>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">Current Rainfall</div>
            <div class="metric-value">
                <span id="currentRainfall">0</span>
                <span class="metric-unit">mm</span>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-label">Hourly Rainfall</div>
            <div class="metric-value">
                <span id="currentHourlyRainfall">0</span>
                <span class="metric-unit">mm</span>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-label">Total Volume</div>
            <div class="metric-value">
                <span id="currentVolume">0</span>
                <span class="metric-unit">L</span>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-label">Flow Rate</div>
            <div class="metric-value">
                <span id="currentFlowRate">0</span>
                <span class="metric-unit">L/min</span>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-label">Sensor Tips</div>
            <div class="metric-value">
                <span id="sensorTips">0</span>
                <span class="metric-unit">tips</span>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-label">Working Time</div>
            <div class="metric-value">
                <span id="workingTime">0</span>
                <span class="metric-unit">hrs</span>
            </div>
            <a href="<a>https://github.com/rushikatabathuni/</a>" target="_blank">Rushi</a>
        </div>
    </div>

    <div class="charts-grid">
        <div class="chart-container">
            <div class="chart-title">Rainfall Trend</div>
            <canvas id="rainfallCanvas"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">Hourly Rainfall</div>
            <canvas id="hourlyRainfallCanvas"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">Total Volume</div>
            <canvas id="volumeCanvas"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">Flow Rate</div>
            <canvas id="flowRateCanvas"></canvas>
        </div>
    </div>
    <a href="<a>https://github.com/rushikatabathuni/</a>" target="_blank">Rushi</a>

    <script>
        // Define constant max values for each chart type
        const CHART_LIMITS = {
            rainfall: 500,      // mm
            hour_rainfall: 200, // mm
            total_volume: 1000, // L
            flow_rate: 200     // L/min
        };

        let lastUpdateTime = Date.now();

        async function fetchData() {
            try {
                const response = await fetch('/readings');
                const data = await response.json();
                if(data.hour_rainfall === 0 || data.total_volume === 0) {
                    const sampleData = generateSampleData();
                    updateMetrics(sampleData);
                    updateCharts(sampleData);
                } else {
                    updateMetrics(data);
                    updateCharts(data);
                }
                lastUpdateTime = Date.now();
            } catch (error) {
                console.error('Failed to fetch data:', error);
                const sampleData = generateSampleData();
                updateMetrics(sampleData);
                updateCharts(sampleData);
            }
        }

        async function resetReadings() {
            try {
                const response = await fetch('/reset', { method: 'POST' });
                if (response.ok) {
                    fetchData();
                }
            } catch (error) {
                console.error('Failed to reset readings:', error);
                alert('Failed to reset readings. Please try again.');
            }
        }

        function generateSampleData() {
            const length = 12;
            return {
                rainfall: Array.from({length}, () => Math.random() * 10),
                hour_rainfall: Array.from({length}, () => Math.random() * 20),
                total_volume: Array.from({length}, () => Math.random() * 100),
                flow_rate: Array.from({length}, () => Math.random() * 50),
                tips: Math.floor(Math.random() * 1000),
                working_time: Math.floor(Math.random() * 168)
            };
        }

        function updateMetrics(data) {
            const getLastValue = arr => Array.isArray(arr) ? (arr[arr.length - 1]?.toFixed(1) || '0') : arr.toFixed(1);
            
            document.getElementById('currentRainfall').textContent = getLastValue(data.rainfall);
            document.getElementById('currentHourlyRainfall').textContent = getLastValue(data.hour_rainfall);
            document.getElementById('currentVolume').textContent = getLastValue(data.total_volume);
            document.getElementById('currentFlowRate').textContent = getLastValue(data.flow_rate);
            document.getElementById('sensorTips').textContent = data.tips;
            document.getElementById('workingTime').textContent = data.working_time;
        }

        function updateCharts(data) {
            drawChart(data.rainfall, 'Rainfall', 'rainfallCanvas', '#2563eb', 'mm', CHART_LIMITS.rainfall);
            drawChart(data.hour_rainfall, 'Hourly Rainfall', 'hourlyRainfallCanvas', '#7c3aed', 'mm', CHART_LIMITS.hour_rainfall);
            drawChart(data.total_volume, 'Total Volume', 'volumeCanvas', '#059669', 'L', CHART_LIMITS.total_volume);
            drawChart(data.flow_rate, 'Flow Rate', 'flowRateCanvas', '#db2777', 'L/min', CHART_LIMITS.flow_rate);
        }

        function drawChart(data, label, canvasId, color, unit, maxValue) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    ctx.clearRect(0, 0, rect.width, rect.height);

    const padding = 60;
    const chartWidth = rect.width - padding * 2;
    const chartHeight = rect.height - padding * 2;

    const stepX = chartWidth / (data.length - 1);

    // Ensure maxY is not zero to avoid dividing by zero.
    const maxY = maxValue || Math.max(...data);

    // Draw Y-axis grid and labels
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    ctx.textAlign = 'right';
    ctx.font = '12px system-ui';

    for (let i = 0; i <= 5; i++) {
        const y = padding + (chartHeight * (1 - i / 5));
        // Grid line
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(rect.width - padding, y);
        ctx.stroke();

        // Y-axis label
        ctx.fillStyle = '#64748b';
        let labelText;
        if (label == 'Rainfall') {
            labelText = (500 * i / 5) + ' ' + unit;
        } else if (label == 'Hourly Rainfall') {
            labelText = (200 * i / 5) + ' ' + unit;
        } else if (label == 'Total Volume') {
            labelText = (500 * i / 5) + ' ' + unit;
        } else if(label=='Flow Rate'){
            labelText = (100 * i / 5) + ' ' + unit;
        }
        ctx.fillText(labelText, padding - 10, y + 4);
    }

    // Draw X-axis labels (time in seconds)
    ctx.textAlign = 'center';
    ctx.fillStyle = '#64748b';
    const timePoints = data.length - 1;

    for (let i = 0; i <= timePoints; i++) {
        const x = padding + (i * stepX);
        const secondsAgo = Math.round((timePoints - i) * 5);
        const timeLabel = secondsAgo + 's';
        ctx.fillText(timeLabel, x, rect.height - padding + 20);
    }

    // Draw data line
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    data.forEach((value, index) => {
        const x = padding + (index * stepX);
        const y = padding + chartHeight * (1 - value / maxY);
        index === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Draw points
    data.forEach((value, index) => {
        const x = padding + (index * stepX);
        const y = padding + chartHeight * (1 - value / maxY);

        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fill();
    });
}


        // Initial fetch and set up interval for 5-second updates
        fetchData();
        setInterval(fetchData, 5000); // Changed to 5000ms (5 seconds)
    </script>
</body>
</html>
'''
    return html

def start_webserver(data_logger):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='RainfallMonitor', password='rainfall123')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 8080))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        try:
            request = conn.recv(1024).decode()
            if 'GET /readings' in request:
                response = get_readings_json(data_logger)
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: application/json\n')
                conn.send('Connection: close\n\n')
                conn.sendall(response.encode())
            elif 'POST /reset' in request:
                # Reset all readings
                data_logger.rainfall_values = []
                data_logger.hour_rainfall_values = []
                data_logger.total_volume_values = []
                data_logger.flow_rate_values = []
                global total_volume
                total_volume = 0.0
                
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/plain\n')
                conn.send('Connection: close\n\n')
                conn.sendall('Reset successful'.encode())
            else:
                response = web_page()
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/html\n')
                conn.send('Connection: close\n\n')
                conn.sendall(response.encode())
        except Exception as e:
            print("Error handling request:", e)
        finally:
            conn.close()


def main():
    print("Initializing Rainfall Sensor...")
    sensor = RainfallSensor()
    print(sensor.begin())
    global flow_sensor_enabled
    data_logger = DataLogger()
    
    import _thread
    _thread.start_new_thread(start_webserver, (data_logger,))
    
    
    print("By https://github.com/rushikatabathuni/")
    print(f"Firmware Version: {sensor.get_firmware_version()}")
    print("Sensor initialized successfully!")
    print("Connect to WiFi network 'RainfallMonitor' with password 'rainfall123'")
    print("Then visit http://192.168.4.1 in your web browser")
    
    timer = Timer(0)
    global prev
    prev=sensor.get_rainfall_time(1)
    
    while True:
        curr_rain=sensor.get_rainfall_time(1)
        cumulative=sensor.get_rainfall()
        tips=sensor.get_raw_data()
        working_time=sensor.get_sensor_working_time()
        print(f"Sensor Working Time: {working_time} hours")
        print(f"Total Cumulative Rainfall: {cumulative} mm")
        print(f"Rainfall in Last 1 Hour(s): {sensor.get_rainfall_time(1)} mm")
        print(f"Raw Tipping Bucket Count: {tips} tips")
        print("By https://github.com/rushikatabathuni/")
        if curr_rain !=prev:
            flow_sensor_enabled = True
            timer.init(period=1000, mode=Timer.PERIODIC, callback=calculate_flow_rate)
        else:
            flow_sensor_enabled = False
            timer.deinit()
        prev=curr_rain
        data_logger.save_reading(cumulative, curr_rain, total_volume, flow_rate,tips, round(working_time,2))
        time.sleep(3)
        
#if __name__ == "__main__":
 #   main()

main()
