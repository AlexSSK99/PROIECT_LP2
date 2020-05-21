import psutil
import time
import csv
import ctypes
import threading
from datetime import datetime

mega = 1024 * 1024
header_written = False


def div(a, b):
    if b == 0:
        return 0
    return a / b


def to_MBps(value, time):
    return (value / mega) * div(1, time)


def to_Mbps(value, time):
    return to_MBps(value, time) * 8


def warn_limit(source, rw_rs, value, limit):
    global header_written  # don't frown!
    if value > limit:
        if rw_rs == 'r' or rw_rs == 'd':
            current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            field_names_r = ['warn_type', 'warn_time', 'read_speed/down_speed', 'write_speed/up_speed', 'exceed_value']
            with open('log.csv', 'a', newline='') as log:
                writer = csv.DictWriter(log, fieldnames=field_names_r)
                if not header_written:
                    writer.writeheader()
                    header_written = True
                if source == 'disk':
                    writer.writerow({'warn_type': 'disk',
                                     'warn_time': current_time,
                                     'read_speed/down_speed': round(value, 2),
                                     'write_speed/up_speed': 0.00,
                                     'exceed_value': round(value - limit, 2)})
                elif source == 'network':
                    writer.writerow({'warn_type': 'network',
                                     'warn_time': current_time,
                                     'read_speed/down_speed': round(value, 2),
                                     'write_speed/up_speed': 0.00,
                                     'exceed_value': round(value - limit, 2)})
        if rw_rs == 'w' or rw_rs == 'u':
            current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            field_names_w = ['warn_type', 'warn_time', 'read_speed/down_speed', 'write_speed/up_speed', 'exceed_value']
            with open('log.csv', 'a', newline='') as log:
                writer = csv.DictWriter(log, fieldnames=field_names_w)
                if not header_written:
                    writer.writeheader()
                    header_written = True
                if source == 'disk':
                    writer.writerow({'warn_type': 'disk',
                                     'warn_time': current_time,
                                     'read_speed/down_speed': 0.00,
                                     'write_speed/up_speed': round(value, 2),
                                     'exceed_value': round(value - limit, 2)})
                elif source == 'network':
                    writer.writerow({'warn_type': 'network',
                                     'warn_time': current_time,
                                     'read_speed/down_speed': 0.00,
                                     'write_speed/up_speed': round(value, 2),
                                     'exceed_value': round(value - limit, 2)})


def disk_monitor():
    while True:
        disk_io_info_as_dict = psutil.disk_io_counters(perdisk=True)
        time.sleep(0.5)
        second_disk_io_info_as_dict = psutil.disk_io_counters(perdisk=True)
        for partitie in disk_io_info_as_dict:
            read_mbps = to_MBps(second_disk_io_info_as_dict[partitie].read_bytes
                                - disk_io_info_as_dict[partitie].read_bytes, 0.5)
            write_mbps = to_MBps(second_disk_io_info_as_dict[partitie].write_bytes
                                 - disk_io_info_as_dict[partitie].write_bytes, 0.5)
            warn_limit('disk', 'r', read_mbps, 50)
            warn_limit('disk', 'w', write_mbps, 25)


def network_monitor():
    while True:
        network_io_info_as_dict = psutil.net_io_counters(pernic=True)
        time.sleep(0.5)
        second_network_io_info_as_dict = psutil.net_io_counters(pernic=True)
        for nic in network_io_info_as_dict:
            up_mbps = to_Mbps(second_network_io_info_as_dict[nic].bytes_sent
                              - network_io_info_as_dict[nic].bytes_sent, 0.5)
            down_mbps = to_Mbps(second_network_io_info_as_dict[nic].bytes_recv
                                - network_io_info_as_dict[nic].bytes_recv, 0.5)
            warn_limit('network', 'u', up_mbps, 5)
            warn_limit('network', 'd', down_mbps, 10)


if __name__ == '__main__':
    try:
        thread_disk = threading.Thread(target=disk_monitor)
        thread_disk.start()
        thread_network = threading.Thread(target=network_monitor)
        thread_network.start()
    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0, "{}".format(e), "A apărut o problemă!", 0)
