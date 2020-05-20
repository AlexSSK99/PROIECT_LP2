import psutil
import time
import csv
import ctypes
from datetime import datetime

mega = 1024 * 1024
header_written = False


def div(a, b):
    if b == 0:
        return 0
    return a / b


def to_mbps(value, time):
    return (value / mega) * div(1, time)


def warn_limit(rw, value, limit):
    global header_written  # don't frown!
    if value > limit:
        if rw == 'r':
            current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            field_names_r = ['warn_time', 'read_speed', 'write_speed', 'exceed_value']
            with open('log.csv', 'a', newline='') as log:
                writer = csv.DictWriter(log, fieldnames=field_names_r)
                if not header_written:
                    writer.writeheader()
                    header_written = True
                writer.writerow({'warn_time': current_time,
                                 'read_speed': round(value, 2),
                                 'write_speed': 0.00,
                                 'exceed_value': round(value - limit, 2)})
            # writer.writerow('{0} -- Viteza citire: {1}MBps -- Valoare depasire: {2}MBps'.format(current_time,
            #                                                                             round(value,2),
            #                                                                             round(value-limit,2)))
        if rw == 'w':
            current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            field_names_w = ['warn_time', 'read_speed', 'write_speed', 'exceed_value']
            with open('log.csv', 'a', newline='') as log:
                writer = csv.DictWriter(log, fieldnames=field_names_w)
                if not header_written:
                    writer.writeheader()
                    header_written = True
                writer.writerow({'warn_time': current_time,
                                 'read_speed': 0.00,
                                 'write_speed': round(value, 2),
                                 'exceed_value': round(value - limit, 2)})
                # writer.writerow(
                #    '{0} -- Viteza scriere: {1}MBps -- Valoare depasire: {2}MBps'.format(current_time,
                #                                                                 round(value,2),
                #                                                                 round(value-limit,2)))


if __name__ == '__main__':
    try:
        while True:
            disk_io_info_as_dict = psutil.disk_io_counters(perdisk=True)
            time.sleep(0.5)
            second_disk_io_info_as_dict = psutil.disk_io_counters(perdisk=True)
            for partitie in disk_io_info_as_dict:
                read_mbps = to_mbps(second_disk_io_info_as_dict[partitie].read_bytes
                                    - disk_io_info_as_dict[partitie].read_bytes, 0.5)
                write_mbps = to_mbps(second_disk_io_info_as_dict[partitie].write_bytes
                                     - disk_io_info_as_dict[partitie].write_bytes, 0.5)
                warn_limit('r', read_mbps, 50)
                warn_limit('w', write_mbps, 25)
    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0, "{}".format(e), "A apărut o problemă!", 0)
