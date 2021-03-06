import multiprocessing
import os
import requests
import json
from time import time
from time import sleep
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import numpy as np

STATION_ID = 72502  # station near new york with lots of data
API_KEY = 'E3vYb9YXFRM7pJ0yvd57UJP2YtkJgVR5'
START_YEAR = 1920  # change to 1920 when done testing
END_YEAR = 2020  # change to 2020 when done testing
TOTAL_YEARS = END_YEAR - START_YEAR


# gets daily data for 'year' and averages
def get_daily_data_and_avg(year):
    # containers to store per year avg min/max temps
    yearly_min_avg = {}
    yearly_max_avg = {}

    while True:
        # initialize data for request
        start = f'{year}-01-01'
        end = f'{year}-12-31'
        headers = {'x-api-key': API_KEY}
        ploads = {'station': STATION_ID, 'start': start, 'end': end}

        try:
            # make request and store response
            r = requests.get('https://api.meteostat.net/v2/stations/daily', params=ploads, headers=headers)

            if r.status_code != 429:
                pass
            else:
                # if API says too many requests, sleep and go back to start of loop
                sleep(1)
                continue

            # convert response to dictionary
            r_dictionary = r.json()
            data = r_dictionary['data']
            daily_min_temps_sum = 0
            daily_max_temps_sum = 0
            num_missing_min_values = 0
            num_missing_max_values = 0

            # pull out data for daily min/max temps and sum
            for daily_data in data:
                if daily_data['tmin']:
                    daily_min_temps_sum += daily_data['tmin']
                else:
                    num_missing_min_values += 1
                if daily_data['tmax']:
                    daily_max_temps_sum += daily_data['tmax']
                else:
                    num_missing_max_values += 1

            # find avg yearly min/max temps
            num_good_min = len(data) - num_missing_min_values
            num_good_max = len(data) - num_missing_max_values
            if num_good_min > 0:
                yearly_avg_min_temp = daily_min_temps_sum / (len(data) - num_missing_min_values)
                yearly_min_avg[f'{year}'] = yearly_avg_min_temp
            if num_good_max > 0:
                yearly_avg_max_temp = daily_max_temps_sum / (len(data) - num_missing_max_values)
                yearly_max_avg[f'{year}'] = yearly_avg_max_temp

        # catch errors
        except ZeroDivisionError as e:
            print(f'Error: {e.args} when getting data for {year}')
        except TypeError as e:
            print(f'Error: {e.args} when getting data for {year}')
        except json.decoder.JSONDecodeError as e:
            print(f'Error: {e.args} when getting data for {year}')
        break

    # return yearly avg temp data
    return yearly_min_avg, yearly_max_avg


# generate list of 'start_year's to pass to processes
def generate_task_list():
    start_year = START_YEAR
    task_list = []
    while start_year < END_YEAR:
        task_list.append(start_year)
        start_year += 1

    return task_list


# for assigning tasks to processes
def worker(process_name, tasks, results):
    print(f'[{process_name}] evaluation routine starts')

    while True:
        # grab new task
        new_value = tasks.get()

        if new_value < 0:
            print(f'[{process_name}] evaluation routine quits')

            # indicate process finished
            results.put(-1)
            break
        else:
            # get temp data for task
            result = get_daily_data_and_avg(new_value)

            # output processes results
            print(f'[{process_name}] was tasked with getting and averaging temp data for {new_value}')
            print(f'[{process_name}] calculated data: {result}')

            # return temp data
            results.put(result)

    return


def get_data_parallel():
    # calculate number of processes based on number of cores
    num_workers = os.cpu_count()

    # generate task list for workers
    task_list = generate_task_list()

    # create queues for task assignment and result return
    manager = multiprocessing.Manager()
    tasks = manager.Queue()
    results = manager.Queue()
    pool = multiprocessing.Pool(processes=num_workers)
    processes = []

    # create as many processes as possible and start them
    for i in range(num_workers):
        process_name = f'P{i}'

        new_process = multiprocessing.Process(target=worker, args=(process_name, tasks, results))

        processes.append(new_process)

        new_process.start()

    # assign tasks to processes
    for task in task_list:
        tasks.put(task)

    # quit processes
    for i in range(num_workers):
        tasks.put(-1)

    # print and return process results
    all_avg_min_temps = {}
    all_avg_max_temps = {}
    num_finished_processes = 0
    while True:
        new_result = results.get()

        if new_result == -1:
            num_finished_processes += 1

            if num_finished_processes == num_workers:
                break

        else:
            print(f'Result: {new_result}')
            all_avg_min_temps.update(new_result[0])
            all_avg_max_temps.update(new_result[1])

    return all_avg_min_temps, all_avg_max_temps


# plot temperature data gathered and averaged
def plot_temp_data(min_temp_data, max_temp_data):
    # initialize plot to draw on
    fig, ax = plt.subplots()

    # format min temp data and plot
    x = np.fromiter(min_temp_data.keys(), dtype=int)
    y = np.fromiter(min_temp_data.values(), dtype=float)
    ax.scatter(x=x, y=y, color='r', label='Yearly Avg. Min. Temps')
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    label = f"$y={z[0]:0.3f}\;x{z[1]:+0.3f}$"
    plt.plot(x, p(x), 'r--', label=label)

    # predict avg min temp for 2020
    predicted_min_temp = z[0]*2020 + z[1]
    print()
    print(f'Predicted avg. min. temp for 2020 = {predicted_min_temp} C')

    # format max temp data and plot
    x = np.fromiter(max_temp_data.keys(), dtype=int)
    y = np.fromiter(max_temp_data.values(), dtype=float)
    ax.scatter(x=x, y=y, color='b', label='Yearly Avg. Max. Temps')
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    label = f"$y={z[0]:0.3f}\;x{z[1]:+0.3f}$"
    plt.plot(x, p(x), 'b--', label=label)

    # predict avg max temp for 2020
    predicted_max_temp = z[0] * 2020 + z[1]
    print(f'Predicted avg. max. temp for 2020 = {predicted_max_temp} C')

    # make figure look good
    ax.legend()
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.0f}'))
    ax.xaxis.set_major_formatter(StrMethodFormatter('{x:.0f}'))
    plt.ylabel('Temp (C)')
    plt.xlabel('Years')

    # save figure
    plt.savefig('temp_data.png')


if __name__ == '__main__':
    print('Start sequential:')
    start_timer = time()
    for i in range(START_YEAR, END_YEAR):
        get_daily_data_and_avg(i)
    stop_timer = time()
    print(f'\nTime to receive and average temp data sequentially: {stop_timer - start_timer}\n')

    print('Start parallel:')
    start_timer = time()
    min_temps, max_temps = get_data_parallel()
    stop_timer = time()
    print(f'\nTime to receive and average temp data in parallel: {stop_timer-start_timer}\n')

    plot_temp_data(min_temps, max_temps)
