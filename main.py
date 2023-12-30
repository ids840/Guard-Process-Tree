# This is a sample Python script.
import csv
import operator

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pm4py

import pandas

from datetime import datetime

from pm4py.algo.conformance.tokenreplay.variants import token_replay
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator

from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator

from pm4py.objects.petri_net.obj import PetriNet, Marking

from pm4py.objects.petri_net.utils import petri_utils

import random

import datetime

import Decision_Tree_To_Guards
import build_bank_net
import build_ski_net
import build_tv_net


def simulate_execution(petri_net, initial_marking, final_marking, num_cases=10):
    event_log = []

    for _ in range(num_cases):
        case_id = f"Case_{_ + 1}"
        current_marking = initial_marking.copy()
        trace = []

        while current_marking not in final_marking:
            enabled_transitions = pm4py.objects.petri_net.semantics.enabled_transitions(petri_net, current_marking)
            if not enabled_transitions:
                break

            # Choose a random enabled transition
            random_number = random.randint(0, len(enabled_transitions) - 1)
            chosen_transition = list(enabled_transitions)[random_number]

            # Simulate the execution of the transition
            event = {
                "case_id": case_id,
                "activity": chosen_transition.label,
                "timestamp": datetime.datetime.now().isoformat(),
            }
            if chosen_transition.label is not None:
                trace.append(event)

            current_marking = pm4py.objects.petri_net.semantics.execute(chosen_transition, petri_net, current_marking)

        event_log.extend(trace)

    return event_log


def import_csv(file_path):
    event_log = pandas.read_csv(file_path, sep=',')
    event_log['case ID'] = event_log['case ID'].astype(str)
    event_log['activity'] = event_log['activity'].astype(str)
    event_log['timestamp'] = pandas.to_datetime(event_log['timestamp'],format='mixed')
    return event_log
    # event_log = pandas.read_csv(file_path)
    # event_log['case ID'] = event_log['case ID'].astype(str)
    # event_log['activity'] = event_log['activity'].astype(str)
    # event_log['timestamp'] = pandas.to_datetime(event_log['timestamp'])
    # return event_log


def petri_net_by_inductive(log):
    net, initial_marking, final_marking = pm4py.discovery.discover_petri_net_inductive(log, False, 0.0, "activity",
                                                                                       "timestamp", "case ID")
    return net, initial_marking, final_marking


def petri_net_by_alpha(log):
    net, initial_marking, final_marking = pm4py.discovery.discover_petri_net_alpha(log, "activity", "timestamp",
                                                                                   "case ID")
    return net, initial_marking, final_marking


def petri_net_by_heuristics(log):
    net, initial_marking, final_marking = pm4py.discovery.discover_petri_net_heuristics(log, 0.5, 0.65, 0.5, "activity",
                                                                                        "timestamp", "case ID")
    return net, initial_marking, final_marking


def petri_net_by_ilp(log):
    net, initial_marking, final_marking = pm4py.discovery.discover_petri_net_ilp(log, 1.0, "activity", "timestamp",
                                                                                 "case ID")
    return net, initial_marking, final_marking


def print_petri_net(net, initial_marking, final_marking):
    pm4py.write_pnml(net, initial_marking, final_marking, "createdPetriNet1.pnml")
    pm4py.view_petri_net(net, initial_marking, final_marking)


def print_confermance(log, net, initial_marking, final_marking):
    dict_of_results = pm4py.conformance_diagnostics_token_based_replay(log, net, initial_marking, final_marking,
                                                                       "activity", "timestamp", "case ID")
    print(dict_of_results)


def dfg(log):
    dfg, start_activity, end_activity = pm4py.discover_directly_follows_graph(log, "activity", "timestamp", "case ID")
    pm4py.view_dfg(dfg, start_activity, end_activity)


def create_new_process_tree(process_tree):
    pass


def evaluation_1(log_path):
    log = import_csv(log_path)
    pro_tree = pm4py.discover_process_tree_inductive(log, 0.0, True, "activity", "timestamp", "case ID")
    pm4py.view_process_tree(pro_tree)
    net_1, initial_marking_1, final_marking_1 = petri_net_by_inductive(log)
    print_petri_net(net_1, initial_marking_1, final_marking_1)
    net_2, initial_marking_2, final_marking_2 = petri_net_by_alpha(log)
    # print_petri_net(net_2, initial_marking_2, final_marking_2)
    net_3, initial_marking_3, final_marking_3 = petri_net_by_ilp(log)
    # print_petri_net(net_2, initial_marking_3, final_marking_3)
    net_4, initial_marking_4, final_marking_4 = petri_net_by_heuristics(log)
    # print_petri_net(net_4, initial_marking_4, final_marking_4)
    print_confermance(log, net_4, initial_marking_4, final_marking_4)
    # dfg(log)
    # process_tree = pm4py.discover_process_tree_inductive(log, 0.0, True, "activity", "timestamp", "case ID")
    # pm4py.view_process_tree(process_tree)
    # net, initial_marking, final_marking = pm4py.objects.conversion.process_tree.variants.to_petri_net.apply(
    # process_tree)

    # pm4py.write_pnml(net, initial_marking, final_marking, "createdPetriNet1.pnml")
    # pm4py.view_petri_net(net, initial_marking, final_marking)
    fitness = pm4py.fitness_token_based_replay(log, net_4, initial_marking_4, final_marking_4, "activity", "timestamp",
                                               "case ID")
    prec = pm4py.precision_token_based_replay(log, net_4, initial_marking_4, final_marking_4, "activity", "timestamp",
                                              "case ID")
    # gen = generalization_evaluator.apply(log, net, initial_marking, final_marking)
    simp = simplicity_evaluator.apply(net_4)
    print(fitness)
    print("prec: " + str(prec))
    # print("gen: " + gen)
    print("simp: " + str(simp))


def evaluation(log, net, initial_marking, final_marking):
    replayed_traces = pm4py.conformance_diagnostics_token_based_replay(log, net, initial_marking, final_marking, "activity", "timestamp",
                                              "case ID")
    for trace in replayed_traces[0:30]:
         print(trace)
    #print(pm4py.analysis.check_is_workflow_net(net))
#    print(pm4py.analysis.check_soundness(net,initial_marking,final_marking))
    fitness = pm4py.fitness_token_based_replay(log, net, initial_marking, final_marking, "activity", "timestamp",
                                            "case ID")
    prec = pm4py.precision_token_based_replay(log, net, initial_marking, final_marking, "activity", "timestamp",
                                              "case ID")
    # gen = generalization_evaluator.apply(log, net, initial_marking, final_marking)
    simp = simplicity_evaluator.apply(net)
    print(fitness)
    print("prec: " + str(prec))
    # print("gen: " + gen)
    print("simp: " + str(simp))


# Function that check for each transition if we can do it
def check_if_can_do_transition(transition: PetriNet.Transition, dict_of_tokens):
    arcs_in = transition.in_arcs
    for arc in arcs_in:
        if dict_of_tokens[arc.source] == 0:
            return False
    return True


# Function that return set of the None transitions that we can do
def group_of_can_do_transitions(transitions, dict_of_tokens):
    set_of_None_can_do_transitions = set()
    for transition in transitions:
        if transition.label == None:
            if check_if_can_do_transition(transition, dict_of_tokens):
                set_of_None_can_do_transitions.add(transition)
    return set_of_None_can_do_transitions


# Function that activate the transition
def activate_transition(transition: PetriNet.Transition, dictionary_of_tokens_copy):
    arcs_in = transition.in_arcs
    for arc in arcs_in:
        dictionary_of_tokens_copy[arc.source] = dictionary_of_tokens_copy[arc.source] - 1
    arcs_out = transition.out_arcs
    for arc in arcs_out:
        dictionary_of_tokens_copy[arc.target] = dictionary_of_tokens_copy[arc.target] + 1


def return_final_place(places):
    for place in places:
        if place.name == 'sink' or place.name == 'sink0':
            return place


# Function that return the label of the transition (activity name)
def return_label_transition(transitions, label):
    for transition in transitions.copy():
        if transition.label == label:
            return transition


# Function that return if a trace is in the net
def check_if_trace_in_net(net, trace, final_marking, dict_of_tokens):
    trace_in_net = False
    set_of_activate_None_transitions = group_of_can_do_transitions(net.transitions, dict_of_tokens)
    for None_activate_transition in set_of_activate_None_transitions:
        dictionary_of_tokens_copy = dict_of_tokens.copy()
        activate_transition(None_activate_transition, dictionary_of_tokens_copy)
        trace_in_net = trace_in_net or check_if_trace_in_net(net, trace, final_marking, dictionary_of_tokens_copy)
    if len(trace) == 0:
        trace_in_net = trace_in_net or dict_of_tokens[return_final_place(net.places)] == 1
    else:
        label_transition = return_label_transition(net.transitions, trace[0])
        if check_if_can_do_transition(label_transition, dict_of_tokens):
            dictionary_of_tokens_copy = dict_of_tokens.copy()
            activate_transition(label_transition, dictionary_of_tokens_copy)
            trace_in_net = trace_in_net or check_if_trace_in_net(net, trace[1:], final_marking,
                                                                 dictionary_of_tokens_copy)
    return trace_in_net


def compute_TN_FP(net, initial, final, test_log):
    TN = 0
    FP = 0
    dict_of_tokens = {}
    for place in net.places:
        if place.name != 'source' and place.name != 'source0':
            dict_of_tokens[place] = 0
        else:
            dict_of_tokens[place] = 1
    for trace in test_log:
        if check_if_trace_in_net(net, trace, final, dict_of_tokens):
            TN = TN + 1
        else:
            FP = FP + 1
    return TN, FP


def compute_TP_FN(net, initial, final, test_log):
    TP = 0
    FN = 0
    dict_of_tokens = {}
    for place in net.places:
        if place.name != 'source':
            dict_of_tokens[place] = 0
        else:
            dict_of_tokens[place] = 1
    for trace in test_log:
        if check_if_trace_in_net(net, trace, final, dict_of_tokens):
            FN = FN + 1
        else:
            TP = TP + 1
    return TP, FN


def generate_for_inductive(net, initial, final, test_log):
    print("Inductive Results: \n")
    TN, FP = compute_TN_FP(net, initial, final, test_log[:10000])
    TP, FN = compute_TP_FN(net, initial, final, test_log[10000:])
    print("TP = " + str(TP) + " TN = " + str(TN) + " FP = " + str(FP) + " FN = " + str(FN) + "\n")
    precision = (TP) / (TP + FP)
    recall = (TP) / (TP + FN)
    f1_measure = (2 * precision * recall) / (precision + recall)
    print("Precision = " + str(precision) + " Recall = " + str(recall) + " F1 measure = " + str(f1_measure) + "\n")


def generate_for_heuristic(net, initial, final, test_log):
    print("Heuristic Results: \n")
    TN, FP = compute_TN_FP(net, initial, final, test_log[:15000])
    TP, FN = compute_TP_FN(net, initial, final, test_log[15000:])
    print("TP = " + str(TP) + " TN = " + str(TN) + " FP = " + str(FP) + " FN = " + str(FN) + "\n")
    precision = (TP) / (TP + FP)
    recall = (TP) / (TP + FN)
    f1_measure = (2 * precision * recall) / (precision + recall)
    print("Precision = " + str(precision) + " Recall = " + str(recall) + " F1 measure = " + str(f1_measure) + "\n")


def get_test_log(log_path):
    file = open(log_path)
    csvreader = csv.reader(file)
    rows = []
    for row in csvreader:
        rows.append(row)
    return rows


def year_plus_one_hundred(year):
    int_year = int(year)
    int_year = int_year + 100
    return str(int_year)


def change_year_in_log(log_path):
    event_log = pandas.read_csv(log_path, sep=';')
    index = 0
    for date in event_log['timestamp']:
        date = year_plus_one_hundred(date[:4]) + date[4:]
        event_log.at[index, 'timestamp'] = date
        index = index + 1
    event_log.to_csv(log_path, index=False)


def count_c(trace):
    if occurs_in_trace(trace, 'c') < 3:
        return True
    return False


def less_six(trace):
    return len(trace) < 6


def last_activity_is_c(trace):
    return len(trace) == 0 or trace[len(trace) - 1] == 'c'


def occurs_in_trace(trace, activity):
    index = 0
    for action in trace:
        if action == activity:
            index = index + 1
    return index


def true_func(trace):
    return True


def print_traces_nice(traces, min_length, max_length):
    print("start printing")
    for i in range(max_length - min_length + 1):
        counter = 0
        for trace in traces:
            length = len(trace)
            if length == min_length + i:
                print(trace)
                counter = counter + 1
        if counter>0:
            print("number of traces in length of " + str(min_length + i) + " is: " + str(counter))
            print("===========================================================================")


def count_in_trace(activity, trace):
    counter = 0
    for action in trace:
        if action == activity:
            counter = counter + 1
    return counter

def convert_xes_to_csv(input_file_path, output_file_path):
    # Write to Pandas Dataframe
    log = pm4py.read_xes(input_file_path)  # Input Filename
    df = pm4py.convert_to_dataframe(log)
    df
    df.to_csv(output_file_path)


def build_names_of_transitions(transitions):
    transitions_names = []
    for transition in transitions:
        if transition.label!=None:
            transitions_names.append(transition.label)
    return transitions_names


def build_pre(place):
    pre = []
    for arc in place.in_arcs:
        pre.append(arc.source)
    return pre


if __name__ == "__main__":
    log = import_csv("C:/Users/עידו שפירא/Downloads/train_log.csv")
    Decision_Tree_To_Guards.split_csv_to_train_test(log)
    train_log = import_csv("C:/Users/עידו שפירא/PycharmProjects/play/train_log.csv")
    test_log = import_csv("C:/Users/עידו שפירא/PycharmProjects/play/test_log.csv")
    #convert_xes_to_csv("C:/Users/עידו שפירא/Downloads/PrepaidTravelCost.xes","C:/Users/עידו שפירא/Downloads/PrepaidTravelCost.csv")
    #print_traces_nice(traces)
    # process_tree_Inductive =  pm4py.discover_process_tree_inductive(train_log,0.0,True,"activity","timestamp","case ID")
    # pm4py.view_process_tree(process_tree_Inductive)
    net,im,fm = petri_net_by_inductive(train_log)
    #print_petri_net(net,im,fm)
    names_of_transitions = build_names_of_transitions(net.transitions)
    #tree = pm4py.convert_to_process_tree(net, im, fm)
    #pm4py.view_process_tree(tree)

    print("Without Guards \n")
    #evaluation(test_log, net, im, fm)
    print("\n==============================================================================================================================\nWith Guards\n")
    Decision_Tree_To_Guards.create_ec_kitty_tree(net,train_log,names_of_transitions)
    #print_petri_net(net,im,fm)

    evaluation(test_log,net,im,fm)
# # process_tree_Inductive._print_tree()
# # #print_petri_net(net_1,initial_marking_1,final_marking_1)
# # #generate_for_inductive(net_1,initial_marking_1,final_marking_1,test_log)
#     net_1, initial_marking_1, final_marking_1 = petri_net_by_inductive(train_log)
#     print_petri_net(net_1,initial_marking_1,final_marking_1)
# #tree = pm4py.convert_to_process_tree(net_1, initial_marking_1, final_marking_1)
# #pm4py.view_process_tree(tree)
    #print_petri_net(net_1,initial_marking_1,final_marking_1)
    #evaluation(train_log, net_1, initial_marking_1, final_marking_1)
# #generate_for_heuristic(net_1,initial_marking_1,final_marking_1,test_log)

# tree = pm4py.generate_process_tree()
# pm4py.view_process_tree(tree, format='png')
# tree = pm4py.generate_process_tree()
# pm4py.view_process_tree(tree, format='png')

#     #log = pm4py.play_out(tree)
#     #print((log))
#     net, im, fm = pm4py.convert_to_petri_net(tree)
#     #pm4py.view_process_tree(tree, format='png')
# #     print_petri_net(net,im,fm)
# #     event_log = simulate_execution(net,im,fm, num_cases=10)
# #
# #     # You can now use or export the event log as needed
# #     for event in event_log:
# #         print(event)
# #
# #     #evaluation_1("C:/Users/עידו שפירא/Downloads/log_example.csv")
# #     #evaluation_1("C:/Users/עידו שפירא/Downloads/‏‏count_example.csv")
# #     #log = import_csv("C:/Users/עידו שפירא/Downloads/transaction1.csv")
# #     #net_1, initial_marking_1, final_marking_1 = petri_net_by_heuristics(log)
# #     #dfg(log)
# #     #print_petri_net(net_1, initial_marking_1, final_marking_1)
# #     #transacted_petri_net = double_to_single_transaction.net_of_transaction(net_1)
# #     #pm4py.view_petri_net(transacted_petri_net)
# #     #
# #     # #    bpmn_graph = pm4py.discover_bpmn_inductive(log, activity_key='concept:name', case_id_key='case:concept:name',
# #     #              #               timestamp_key='time:timestamp')
# #     #     process_tree = pm4py.discover_process_tree_inductive(log,0.0,True,"activity","timestamp","case ID")
# #     #     #pm4py.view_process_tree(process_tree)
# #     #     bpmn_model = pm4py.convert_to_bpmn(process_tree)
# #     #     #pm4py.view_bpmn(bpmn_model)
# #     #     petri_net, initial_marking, final_marking = pm4py.objects.conversion.process_tree.variants.to_petri_net.apply(process_tree)
# #     #     pm4py.write_pnml(petri_net, initial_marking, final_marking, "createdPetriNet1.pnml")
# #
# #     # pm4py.view_petri_net(petri_net, initial_marking, final_marking)
# #     net = PetriNet("new_petri_net")
# #     one = PetriNet.Place("one")
# #     two = PetriNet.Place("two")
# #     three = PetriNet.Place("three")
# #     four = PetriNet.Place("four")
# #     five = PetriNet.Place("five")
# #     six = PetriNet.Place("six")
# #     seven = PetriNet.Place("seven")
# #     eight = PetriNet.Place("eight")
# #     nine = PetriNet.Place("nine")
# #     ten = PetriNet.Place("ten")
# #     eleven = PetriNet.Place("eleven")
# #     twelve = PetriNet.Place("twelve")
# #     thirteen = PetriNet.Place("thirteen")
# #     fourteen = PetriNet.Place("fourteen")
# #     fifteen = PetriNet.Place("fifteen")
# #
# #     net.places.add(one)
# #     net.places.add(two)
# #     net.places.add(three)
# #     net.places.add(four)
# #     net.places.add(five)
# #     net.places.add(six)
# #     net.places.add(seven)
# #     net.places.add(eight)
# #     net.places.add(nine)
# #     net.places.add(ten)
# #     net.places.add(eleven)
# #     net.places.add(twelve)
# #     net.places.add(thirteen)
# #     net.places.add(fourteen)
# #     net.places.add(fifteen)
# #
# #     # Create transitions
# #     a = PetriNet.Transition("a", "a")
# #     b = PetriNet.Transition("b", "b")
# #     c = PetriNet.Transition("c", "c")
# #     e1 = PetriNet.Transition("e", "e")
# #     e2 = PetriNet.Transition("e", "e")
# #     d1 = PetriNet.Transition("d", "d")
# #     d2 = PetriNet.Transition("d", "d")
# #     f = PetriNet.Transition("f", "f")
# #     t1 = PetriNet.Transition("t", "t")
# #     g1 = PetriNet.Transition("g", "g")
# #     t2 = PetriNet.Transition("t", "t")
# #     g2 = PetriNet.Transition("g", "g")
# #     empty1 = PetriNet.Transition("empty1", None)
# #
# #     # Add the transitions to the Petri Net
# #     net.transitions.add(a)
# #     net.transitions.add(b)
# #     net.transitions.add(c)
# #     net.transitions.add(d1)
# #     net.transitions.add(d2)
# #     net.transitions.add(e1)
# #     net.transitions.add(e2)
# #     net.transitions.add(g1)
# #     net.transitions.add(f)
# #     net.transitions.add(g2)
# #     net.transitions.add(t1)
# #     net.transitions.add(t2)
# #     net.transitions.add(empty1)
# #
# #
# #     petri_utils.add_arc_from_to(one, a, net)
# #     petri_utils.add_arc_from_to(a, two, net)
# #     petri_utils.add_arc_from_to(a, three, net)
# #     petri_utils.add_arc_from_to(two, b, net)
# #     petri_utils.add_arc_from_to(three, c, net)
# #     petri_utils.add_arc_from_to(b, four, net)
# #     petri_utils.add_arc_from_to(c, five, net)
# #     petri_utils.add_arc_from_to(four, empty1, net)
# #     petri_utils.add_arc_from_to(five, empty1, net)
# #     petri_utils.add_arc_from_to(empty1, six, net)
# #     petri_utils.add_arc_from_to(six, d1, net)
# #     petri_utils.add_arc_from_to(six, e1, net)
# #     petri_utils.add_arc_from_to(e1, eight, net)
# #     petri_utils.add_arc_from_to(d1, nine, net)
# #     petri_utils.add_arc_from_to(eight, d2, net)
# #     petri_utils.add_arc_from_to(nine, e2, net)
# #     petri_utils.add_arc_from_to(d2, ten, net)
# #     petri_utils.add_arc_from_to(e2, eleven, net)
# #     petri_utils.add_arc_from_to(ten, g1, net)
# #     petri_utils.add_arc_from_to(eleven, t1, net)
# #     petri_utils.add_arc_from_to(g1, twelve, net)
# #     petri_utils.add_arc_from_to(t1, thirteen, net)
# #     petri_utils.add_arc_from_to(twelve, t2, net)
# #     petri_utils.add_arc_from_to(thirteen, g2, net)
# #     petri_utils.add_arc_from_to(t2, fourteen, net)
# #     petri_utils.add_arc_from_to(g2, fourteen, net)
# #     petri_utils.add_arc_from_to(fourteen, f, net)
# #     petri_utils.add_arc_from_to(f, fifteen, net)
# #
# #     initial_marking = Marking()
# #     initial_marking[one] = 1
# #     final_marking = Marking()
# #     final_marking[fifteen] = 0
# #     #pm4py.write_pnml(net, initial_marking, final_marking, "createdPetriNet2.pnml")
# #     #pm4py.view_petri_net(net, initial_marking, final_marking)
# #     #evaluation("C:/Users/עידו שפירא/Downloads/‏‏count_example.csv",net,initial_marking,final_marking)
# #
# # # evaluation("C:/Users/עידו שפירא/Downloads/super_example.csv", net, initial_marking, final_marking)
# # # net = PetriNet("new_petri_net")
# # # one = PetriNet.Place("one")
# # # two = PetriNet.Place("two")
# # # three = PetriNet.Place("three")
# # # four = PetriNet.Place("four")
# # # five = PetriNet.Place("five")
# # # six = PetriNet.Place("six")
# # # seven = PetriNet.Place("seven")
# # # eight = PetriNet.Place("eight")
# # # net.places.add(one)
# # # net.places.add(two)
# # # net.places.add(three)
# # # net.places.add(four)
# # # net.places.add(five)
# # # net.places.add(six)
# # # net.places.add(seven)
# # # net.places.add(eight)
# # # # Create transitions
# # # choose_c = PetriNet.Transition("choose_c", "choose_c")
# # # choose_t = PetriNet.Transition("choose_t", "choose_t")
# # # buy_c = PetriNet.Transition("buy_c", "buy_c")
# # # buy_t = PetriNet.Transition("buy_t", "buy_t")
# # # # Add the transitions to the Petri Net
# # # net.transitions.add(choose_c)
# # # net.transitions.add(choose_t)
# # # net.transitions.add(buy_c)
# # # net.transitions.add(buy_t)
# # #
# # # petri_utils.add_arc_from_to(one, choose_c, net)
# # # petri_utils.add_arc_from_to(two, choose_c, net)
# # # petri_utils.add_arc_from_to(two, choose_t, net)
# # # petri_utils.add_arc_from_to(three, buy_c, net)
# # # petri_utils.add_arc_from_to(four, buy_t, net)
# # # petri_utils.add_arc_from_to(five, buy_c, net)
# # # petri_utils.add_arc_from_to(six, buy_t, net)
# # # petri_utils.add_arc_from_to(choose_c, five, net)
# # # petri_utils.add_arc_from_to(choose_t, six, net)
# # # petri_utils.add_arc_from_to(buy_c, seven, net)
# # # petri_utils.add_arc_from_to(buy_c, two, net)
# # # petri_utils.add_arc_from_to(buy_t, eight, net)
# # # petri_utils.add_arc_from_to(buy_t, one, net)
# # # initial_marking = Marking()
# # # initial_marking[two] = 1
# # # initial_marking[three] = 3
# # # initial_marking[four] = 3
# # # final_marking = Marking()
# # # final_marking[seven] = 0
# # # final_marking[eight] = 0
# # #    pm4py.write_pnml(net, initial_marking, final_marking, "createdPetriNet1.pnml")
# #
# # #   pm4py.view_petri_net(net, initial_marking, final_marking)

import shutil
import zipfile
#
# import pickle
#
# if __name__ == "__main__":
#     with open('test_normal_errors.pkl', 'rb') as file:
#         data = pickle.load(file)
#     print(len(data[0]))
