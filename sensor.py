from flask import Flask, request, render_template_string
import os
import time
from datetime import datetime

app = Flask(__name__)
sensor_data_dir = "sensor-data"

# Ensure the sensor-data directory exists
os.makedirs(sensor_data_dir, exist_ok=True)

@app.route('/store-sensor-data', methods=['POST'])
def store_sensor_data():
    number = request.data.decode()
    epoch_time = int(time.time() * 1000)  # milliseconds since epoch
    current_time = datetime.now()
    filename = f"{sensor_data_dir}/{current_time.strftime('%Y-%m-%d-%H')}.txt"
    
    with open(filename, 'a') as file:
        file.write(f"{epoch_time},{number}\n")
    
    return "Data stored successfully", 200

@app.route('/')
def index():
    files = sorted(os.listdir(sensor_data_dir), reverse=True)[:10]  # Sort and get the latest 10 files
    timestamps, values = [], []

    for filename in files:
        with open(f"{sensor_data_dir}/{filename}", 'r') as file:
            for line in file:
                epoch, value = line.strip().split(',')
                # Convert epoch to datetime string in a format ApexCharts can easily parse
                timestamp = datetime.fromtimestamp(int(epoch)/1000).strftime('%Y-%m-%d %H:%M:%S')
                timestamps.append(timestamp)
                values.append(int(value))
    
    # ApexCharts data preparation
    series_data = list(zip(timestamps, values))

    # Serving an HTML page with the sensor data and an ApexChart
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sensor Data</title>
        <!-- Include ApexCharts -->
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    </head>
    <body>
        <h1>Sensor Data Chart</h1>
        <div id="chart"></div>
        <script>
            var options = {{
                series: [{
                    name: 'Sensor Value',
                    data: {series_data}
                }],
                chart: {{
                    type: 'line',
                    height: 350
                }},
                xaxis: {{
                    type: 'datetime',
                    // No need for categories here as we're providing datetime values directly in data
                }},
                stroke: {{
                    curve: 'smooth'
                }},
                title: {{
                    text: 'Sensor Data Over Time',
                    align: 'left'
                }},
                tooltip: {{
                    x: {{
                        format: 'dd MMM yyyy HH:mm:ss'
                    }}
                }}
            }};

            var chart = new ApexCharts(document.querySelector("#chart"), options);
            chart.render();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)


if __name__ == '__main__':
    app.run(debug=True)
