import serial
import csv
import time
import matplotlib
matplotlib.use('TkAgg')  # Or try 'Qt5Agg', 'WXAgg' if TkAgg doesn't work
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

ser = serial.Serial('COM6', 9600)  # Replace 'COM6' with your Arduino's COM port
filename = "eeg_data.csv"
attention_data = []
meditation_data = []
time_data = []
start_time = time.time()
header_received = False

# Initialize plot
plt.style.use('seaborn-v0_8-darkgrid')
fig, ax = plt.subplots(2, 1, sharex=True)
line_attention, = ax[0].plot([], [], label='Attention', color='blue')
line_meditation, = ax[1].plot([], [], label='Meditation', color='green')
ax[0].set_ylabel('Attention Level')
ax[1].set_ylabel('Meditation Level')
ax[1].set_xlabel('Time (s)')
ax[0].legend()
ax[1].legend()
fig.suptitle('Live EEG Data')


def update_graph(i):
    global attention_data, meditation_data, time_data, start_time, header_received
    try:
        while ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            print(repr(line))
            if not header_received:
                if "A:" in line and "M:" in line:
                    header_received = True
                    print("Header Received: Found A: and M: in first data line")
                else:
                    print("Waiting for initial data with A: and M:")

            if header_received:
                if "A:" in line and "M:" in line:
                    try:
                        parts = line.split()
                        attention_str = parts[0].split(":")[1]
                        meditation_str = parts[1].split(":")[1]
                        attention = int(attention_str)
                        meditation = int(meditation_str)
                        current_time = time.time() - start_time
                        time_data.append(current_time)
                        attention_data.append(attention)
                        meditation_data.append(meditation)
                        window_size = 50
                        time_data = time_data[-window_size:]
                        attention_data = attention_data[-window_size:]
                        meditation_data = meditation_data[-window_size:]
                        line_attention.set_data(time_data, attention_data)
                        line_meditation.set_data(time_data, meditation_data)
                        ax[0].relim()
                        ax[0].autoscale_view()
                        ax[1].relim()
                        ax[1].autoscale_view()
                    except ValueError:
                        print(f"ValueError: Could not convert data to int: {line}")
                else:
                    print(f"Ignored: {line}")

    except serial.SerialException as e:
        print(f"Serial port error: {e}")
        plt.close()
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        plt.close()
        return


ani = FuncAnimation(fig, update_graph, interval=100)
plt.show()

try:
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Time", "Attention", "Meditation"])
        for t, a, m in zip(time_data, attention_data, meditation_data):
            csvwriter.writerow([t, a, m])
    print(f"Data saved to {filename}")
except Exception as e:
    print(f"Error saving to CSV: {e}")

if ser.is_open:
    ser.close()
