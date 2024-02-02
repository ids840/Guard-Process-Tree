import csv
from datetime import datetime
from random import random


def create_csv_file(headlines, data, csv_name):
    with open(csv_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(headlines)

        for row in data:
            writer.writerow(row)


def year_plus_one(year):
    int_year = int(year)
    int_year = int_year + 1
    if len(str(int_year)) == 1:
        return "0" + str(int_year)
    return str(int_year)


def add_one_year(timestamp):
    day = timestamp[8:10]
    month = timestamp[5:7]
    year = timestamp[:4]
    if int(day) == 28 and int(month) == 12:
        day = "01"
        month = "01"
        year = year_plus_one(year)
    if int(day) == 28:
        day = "01"
        month = year_plus_one(month)
    else:
        day = year_plus_one(day)
    return year + "-" + month + "-" + day



def create_csv_event_log(log, csv_name):
    timestamp = ''
    last_case_id = 0
    list_of_events_for_log = []
    for event in log:
        case_id = event.get("case_id")[5:]
        activity = event.get("activity")
        if int(case_id) != last_case_id:
            timestamp = '1700-12-01'
            last_case_id = int(case_id)
        else:
            timestamp = add_one_year(timestamp)
        event_for_log = []
        event_for_log.append(case_id)
        event_for_log.append(activity)
        event_for_log.append(timestamp)
        list_of_events_for_log.append(event_for_log)
    create_csv_file(['case ID', 'activity', 'timestamp'], list_of_events_for_log, csv_name)


def build_events(trace, case_id):
    case_id_str = f"Case_{case_id}"
    trace_log = []
    for activity in trace:
        event = {
            "case_id": case_id_str,
            "activity": activity,
            "timestamp": datetime.now().isoformat(),
        }
        trace_log.append(event)
    return trace_log

def build_log(traces):
    log = []
    for i in range(len(traces)):
        trace_log = build_events(traces[i], i + 1)
        log.extend(trace_log)
    return log

def build_traces_log(traces, length):
    traces_copy = traces.copy()
    traces_built = []
    for index in range(length):
        random_trace = random.choice(traces_copy)
        traces_built.append(random_trace)
        traces_copy.remove(random_trace)
    return traces_built

def split_csv_to_train_test(csv):
    traces = build_traces_from_csv(csv)
    train_length = int(0.8 * len(traces))
    train_log = build_log(traces[0:train_length + 1])
    test_log = build_log(traces[train_length + 1:])
    create_csv_event_log(train_log, "train_log.csv")
    create_csv_event_log(test_log, "test_log.csv")


def build_traces_from_csv(csv):
    traces = []
    last_case_id = ""
    trace = []
    for row in csv.iterrows():
        case_id = row[1]["case ID"]
        activity = row[1]["activity"]
        if case_id != "UNKNOWN":
            if case_id == last_case_id:
                trace.append(activity)
            else:
                traces.append(trace.copy())
                trace = [activity]
                last_case_id = case_id

    return traces[1:]