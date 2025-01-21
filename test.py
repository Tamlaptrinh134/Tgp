import matplotlib.pyplot as plt
import numpy as np
import threading
import queue
import time

data_queue = queue.Queue()

# Hàm vẽ biểu đồ
def plot_chart():
    plt.ion()
    fig, ax = plt.subplots()
    x_data, y_data = [], []

    line, = ax.plot(x_data, y_data, 'b-')

    while True:
        if not data_queue.empty():
            new_data = data_queue.get()
            x_data.append(len(x_data))
            y_data.append(new_data)

            line.set_xdata(x_data)
            line.set_ydata(y_data)
            ax.relim()
            ax.autoscale_view()

            plt.draw()
            plt.pause(0.1)

# Hàm cập nhật dữ liệu
def update_data():
    while True:
        data_queue.put(np.random.randint(0, 10))
        time.sleep(0.5)

if __name__ == "__main__":
    # Tạo các luồng
    chart_thread = threading.Thread(target=plot_chart)
    data_thread = threading.Thread(target=update_data)

    # Khởi chạy các luồng
    chart_thread.start()
    data_thread.start()
