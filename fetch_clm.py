from f1_23_telemetry.listener import TelemetryListener
from f1_23_telemetry.packets import *
from datetime import datetime, timedelta
import tabulate

# FIXME reorder to add PB at the right place ?
# Also provide circuit country/name and format the Discord messages directly
# TODO Maybe filter based on google sheet to only print pilots from current champ

def format_time(obj:timedelta):
    if obj == timedelta(0):
        return '--:--.---'
    minutes = obj.seconds//60
    minutes_str = f'{obj.seconds//60}:' if minutes > 0 else ''
    seconds = obj.seconds%60
    seconds_str = str(seconds).zfill(2) if minutes > 0 else seconds
    return f'{minutes_str}{seconds_str}.{str(obj.microseconds//1000).zfill(3)}'

def print_clm(l: list):
    rnks = sorted(l, key=lambda x: datetime.strptime(x[1], '%M:%S.%f').replace(year=2023).timestamp())
    ranking = [
        (i+1, rnks[i][0], rnks[i][1])
        for i in range(len(rnks))
    ]
    print('```')
    print(tabulate.tabulate(ranking, tablefmt='simple_grid'))
    print('```')

listener = TelemetryListener(port=20777, host='192.168.1.52')

try:
    pb_key = 'Xionhearts'
    best_laps = {pb_key: None}

    current_rival_name = None
    last_insertion_datetime = datetime.now()
    while True:
        packet = listener.get()
        if isinstance(packet,PacketParticipantsData):
            rival_name = packet.participants[3].name
            rival_name = rival_name.decode('utf-8') if isinstance(rival_name, bytes) else rival_name
            if not current_rival_name or current_rival_name != rival_name:
                current_rival_name = rival_name
                if current_rival_name not in best_laps:
                    best_laps[current_rival_name] = None
        elif isinstance(packet,PacketLapData):
            if not best_laps[pb_key]:
                perso_time = timedelta(seconds=packet.lap_data[packet.time_trial_pb_car_idx].last_lap_time_in_ms/1000)
                best_laps[pb_key] = format_time(perso_time)
                print(f'Added {pb_key}: {best_laps[pb_key]}')
                last_insertion_datetime = datetime.now()
                notified = False
            if current_rival_name and current_rival_name in best_laps and not best_laps[current_rival_name]:
                rival_time = timedelta(seconds=packet.lap_data[packet.time_trial_rival_car_idx].last_lap_time_in_ms/1000)
                best_laps[current_rival_name] = format_time(rival_time)
                print(f'Added {current_rival_name}: {best_laps[current_rival_name]}, move to another rival')
                last_insertion_datetime = datetime.now()
                notified = False
        delta = datetime.now() - last_insertion_datetime
        if delta.seconds > 6:
            break
        elif delta.seconds > 4 and not notified:
            notified = True
            print('Make sure to select a new rival in maximum 2 seconds or program will exit')

    print_clm([(key,value) for key,value in best_laps.items() if key != pb_key] + [(pb_key, best_laps[pb_key])])

except KeyboardInterrupt:
    print_clm([(key,value) for key,value in best_laps.items() if key != pb_key] + [(pb_key, best_laps[pb_key])])


