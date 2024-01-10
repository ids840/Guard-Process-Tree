import csv
from datetime import datetime

import clf as clf
import numpy as np
import pandas as pd
import pm4py
from matplotlib import pyplot as plt
from pm4py import PetriNet
from pm4py.objects.dfg.retrieval import pandas
from pm4py.objects.petri_net import semantics
from pm4py.objects.petri_net.utils import petri_utils
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split  # Import train_test_split function
from sklearn import metrics, __all__  # Import scikit-learn metrics module for accuracy calculation
from sklearn.tree import DecisionTreeClassifier

import EC_KITTY
import EC_KITTY_SKL


def add_arcs_from_place_to_transitions(net, place, transitions):
    for transition in transitions:
        petri_utils.add_arc_from_to(place, transition, net, 1)


def found_transition(net, transition_name):
    for transition in net.transitions:
        if (transition.label == None and transition.name == transition_name) or transition.label == transition_name:
            return transition


def found_place(net, place_name):
    for place in net.places:
        if place.name == place_name:
            return place


def found_start_transitions(net, source):
    start_transitions = []
    for arc in net.arcs:
        if arc.source == source:
            start_transitions.append(arc.target)
    return start_transitions


def guard_min_x_times(net, transition, list_of_transitions, times, index_for_transition):
    place = PetriNet.Place("happened " + list_of_transitions[0].label + " as pre condition to " + transition.label)
    net.places.add(place)
    for transition_in_list in list_of_transitions:
        petri_utils.add_arc_from_to(transition_in_list, place, net)
    petri_utils.add_arc_from_to(place, transition, net, times)


def guard_min_x_times_must_happen(net, transition, list_of_transitions, times, index_for_transition):
    place = PetriNet.Place("happened " + list_of_transitions[0].label + " " + str(
        times) + " times as pre condition to " + transition.label)
    net.places.add(place)
    for transition_in_list in list_of_transitions:
        petri_utils.add_arc_from_to(transition_in_list, place, net)
    petri_utils.add_arc_from_to(place, transition, net, times)
    petri_utils.add_arc_from_to(transition, place, net, times)


def create_max_guard_place(net, transition, times, index_of_guard, transition_max_times):
    max_guard_place = PetriNet.Place(
        transition_max_times + " happens max " + str(times) + " times before happen " + transition.label)
    net.places.add(max_guard_place)
    start_transitions = found_start_transitions(net, found_place(net, "source"))
    for start_transition in start_transitions:
        petri_utils.add_arc_from_to(start_transition, max_guard_place, net, times + 1)
    return max_guard_place


def minus_one_from_transitions(net, max_guard_place, list_of_transitions):
    for transition in list_of_transitions:
        petri_utils.add_arc_from_to(transition, max_guard_place, net, -1)


def minus_counter_to_list_of_activites(net, list_of_transitions, max_guard_place):
    minus_one_from_transitions(net, max_guard_place, list_of_transitions)


def guard_of_max_times(net, transition, list_of_transitions, times, index_of_guard):
    max_guard_place = create_max_guard_place(net, transition, times, index_of_guard)
    minus_counter_to_list_of_activites(net, list_of_transitions, max_guard_place)
    add_arcs_from_place_to_transitions(net, max_guard_place, [transition])


def guard_of_max_times_must_happen(net, transition, list_of_transitions, times, index_of_guard):
    transition_max_name = list_of_transitions[0].label
    max_guard_place = create_max_guard_place(net, transition, times, index_of_guard, transition_max_name)
    minus_counter_to_list_of_activites(net, list_of_transitions, max_guard_place)
    add_arcs_from_place_to_transitions(net, max_guard_place, [transition])
    petri_utils.add_arc_from_to(transition, max_guard_place, net, 1)


def replace_element_with_last(original_list, index):
    last_element = original_list[-1]
    original_list[len(original_list) - 1] = original_list[index]
    original_list[index] = last_element
    return original_list


def builds_all_target(column):
    targets = [column]
    for index in range(len(column) - 1):
        copy_column = column.copy()
        copy_column = replace_element_with_last(copy_column, index)
        targets.append(copy_column)
    return targets


def build_class_names(labeled):
    values = []
    for row in labeled.iterrows():
        value = row[1].iloc[0]
        values.append(value)
    set_of_values = set(values)
    sorted_list = sorted(set_of_values)
    classs_names = []
    for item in sorted_list:
        classs_names.append(str(item))
    return classs_names


def build_linear_regression(csv_file, col_names):
    from sklearn import linear_model
    feature_columns = col_names[:-1]
    labeled_column = col_names[len(col_names) - 1:]
    features = csv_file[feature_columns][1:]
    label = csv_file[labeled_column][1:]
    regr = linear_model.LinearRegression()
    regr.fit(features, label)
    print(regr.coef_)


def build_decision_tree(csv_file, col_names):
    feature_columns = col_names[:-1]
    labeled_column = col_names[len(col_names) - 1:]
    features = csv_file[feature_columns][1:]
    labeled = csv_file[labeled_column][1:]
    # Split dataset into training set and test set
    X_train, X_test, y_train, y_test = train_test_split(features, labeled, test_size=0.3, train_size=0.7,
                                                        random_state=1)
    # Create Decision Tree classifer object
    clf = DecisionTreeClassifier()

    # Train Decision Tree Classifer
    clf = clf.fit(X_train, y_train)

    class_names = build_class_names(labeled)
    # Predict the response for test dataset
    y_pred = clf.predict(X_test)
    # Model Accuracy, how often is the classifier correct?
    # print("Accuracy:", metrics.accuracy_score(y_test, y_pred))

    clf = clf.fit(features, labeled)

    # plt.figure(figsize=(20, 10))  # You can adjust the figure size as needed
    # plot_tree(clf, feature_names=feature_columns, class_names=class_names, filled=True, rounded=True,
    #           precision=2)
    # plt.show()

    return clf.tree_


def list_are_zero_except_one(list):
    counter_of_not_zero = 0
    index = -1
    curr_index = 0
    for item in list:
        if item != 0:
            index = curr_index
            counter_of_not_zero = counter_of_not_zero + 1
        curr_index = curr_index + 1
    if counter_of_not_zero != 1:
        index = -1
    return index


def build_values_list(node_id, traces_list, tree):
    if node_id != 0:
        traces_list.append(tree.value[node_id][0])
    is_split_node = tree.children_left[node_id] != tree.children_right[node_id]
    if is_split_node:
        build_values_list(tree.children_left[node_id], traces_list, tree)
        build_values_list(tree.children_right[node_id], traces_list, tree)
    return traces_list


def build_is_leaves_list(node_id, traces_list, tree):
    is_split_node = tree.children_left[node_id] != tree.children_right[node_id]
    if is_split_node:
        if node_id != 0:
            traces_list.append("no")
        build_is_leaves_list(tree.children_left[node_id], traces_list, tree)
        build_is_leaves_list(tree.children_right[node_id], traces_list, tree)
    else:
        traces_list.append("yes")
    return traces_list


def build_features_list(node_id, traces_list, current_trace, tree):
    if len(current_trace) > 0:
        traces_list.append(current_trace.copy())
    is_split_node = tree.children_left[node_id] != tree.children_right[node_id]
    if is_split_node:
        current_trace.append(tree.feature[node_id])
        build_features_list(tree.children_left[node_id], traces_list, current_trace.copy(), tree)
        build_features_list(tree.children_right[node_id], traces_list, current_trace.copy(), tree)
    return traces_list


def build_therashold_list(node_id, traces_list, current_trace, tree):
    if len(current_trace) > 0:
        traces_list.append(current_trace.copy())
    is_split_node = tree.children_left[node_id] != tree.children_right[node_id]
    if is_split_node:
        current_trace.append(tree.threshold[node_id])
        build_therashold_list(tree.children_left[node_id], traces_list, current_trace.copy(), tree)
        build_therashold_list(tree.children_right[node_id], traces_list, current_trace.copy(), tree)
    return traces_list


def build_traces_list(node_id, traces_list, current_trace, tree):
    if len(current_trace) > 0:
        traces_list.append(current_trace)
    is_split_node = tree.children_left[node_id] != tree.children_right[node_id]
    if is_split_node:
        trace_for_left = current_trace.copy()
        trace_for_left.append("left")
        trace_for_right = current_trace.copy()
        trace_for_right.append("right")
        build_traces_list(tree.children_left[node_id], traces_list, trace_for_left, tree)
        build_traces_list(tree.children_right[node_id], traces_list, trace_for_right, tree)
    return traces_list


def build_guard(trace, threasholds, features):
    traces = []
    for i in range(len(threasholds)):
        traces.append((features[i], trace[i], threasholds[i]))
    return traces


def build_guard_for_counter(traces, threasholds, leaves, features, values, counter):
    list_of_guards = []
    for i in range(len(traces)):
        if leaves[i] == "yes" and list_are_zero_except_one(values[i]) == counter:
            list_of_guards.append(build_guard(traces[i], threasholds[i], features[i]))
    return list_of_guards


#
# def find_must_guards(tree,features):
#     # traces = build_traces_list(0, [], [], tree)
#     # threasholds = build_therashold_list(0,[],[],tree)
#     # leaves = build_is_leaves_list(0,[],tree)
#     # features = build_features_list(0,[],[],tree)
#     # values = build_values_list(0,[],tree)
#     # dictionary_of_classes = {}
#     list_of_guards = []
#     stack = [0]
#     direction = "start"
#     while len(stack) > 0 :
#         node_id = stack.pop(0)
#         left_node_id = tree.children_left[node_id]
#         right_node_id = tree.children_right[node_id]
#         is_split_node = left_node_id != right_node_id
#         if is_split_node:
#             value_of_curr = tree.value[node_id][0]
#             value_of_left = tree.value[left_node_id][0]
#             value_of_right = tree.value[right_node_id][0]
#             threshold = int(tree.threshold[node_id])
#             if direction == "start" or direction == "left":
#                 if value_of_curr[0] == value_of_left[0]:
#                     list_of_guards.append((features[tree.feature[node_id]], "bigger", threshold))
#                     stack.append(left_node_id)
#                     direction = "left"
#                 if value_of_curr[0] == value_of_right[0]:
#                     list_of_guards.append((features[tree.feature[node_id]], "smaller", threshold))
#                     stack.append(right_node_id)
#                     direction = "left"
#             if direction == "start" or direction == "right":
#                 if value_of_curr[1] == value_of_left[1]:
#                     list_of_guards.append((features[tree.feature[node_id]], "smaller", threshold))
#                     stack.append(left_node_id)
#                 if value_of_curr[1] == value_of_right[1]:
#                     list_of_guards.append((features[tree.feature[node_id]], "bigger", threshold))
#                     stack.append(right_node_id)
#                 direction = "right"
#     return list_of_guards, direction

def find_must_guard_new(tree, features):
    # traces = build_traces_list(0, [], [], tree)
    # threasholds = build_therashold_list(0,[],[],tree)
    # leaves = build_is_leaves_list(0,[],tree)
    # features = build_features_list(0,[],[],tree)
    # values = build_values_list(0,[],tree)
    # dictionary_of_classes = {}
    list_of_or_guards = []
    list_of_and_guard = []
    stack = [0]
    add_last_maybe = False
    last_was_and = False
    while len(stack) > 0:
        found = False
        node_id = stack.pop(0)
        value_of_curr = tree.value[node_id][0]
        left_node_id = tree.children_left[node_id]
        right_node_id = tree.children_right[node_id]
        is_split_node = left_node_id != right_node_id
        if is_split_node:
            value_of_left = tree.value[left_node_id][0]
            value_of_right = tree.value[right_node_id][0]
            threshold = int(tree.threshold[node_id])
            if 0 == value_of_right[0]:
                copy_list_of_and = list_of_and_guard.copy()
                copy_list_of_and.append((features[tree.feature[node_id]], "bigger", threshold + 1))
                list_of_or_guards.append(copy_list_of_and)
                list_of_and_guard.append((features[tree.feature[node_id]], "smaller", threshold))
                stack.append(left_node_id)
                last_was_and = False
                found = True
            if 0 == value_of_left[0]:
                copy_list_of_and = list_of_and_guard.copy()
                copy_list_of_and.append((features[tree.feature[node_id]], "smaller", threshold))
                list_of_or_guards.append(copy_list_of_and)
                list_of_and_guard.append((features[tree.feature[node_id]], "bigger", threshold + 1))
                stack.append(right_node_id)
                last_was_and = False
                found = True
            if value_of_curr[1] == value_of_left[1] and found == False:
                list_of_and_guard.append((features[tree.feature[node_id]], "smaller", threshold))
                stack.append(left_node_id)
                last_was_and = True
                found = False
            if value_of_curr[1] == value_of_right[1] and found == False:
                list_of_and_guard.append((features[tree.feature[node_id]], "bigger", threshold + 1))
                stack.append(right_node_id)
                last_was_and = True
                found = False
    if value_of_curr[0] == 0:
        list_of_or_guards.append(list_of_and_guard)
    if value_of_curr[1] != 0:
        list_of_or_guards = []
    return list_of_or_guards


def special_transition_condition_function(tree, features):
    list_of_or_guards = []
    list_of_and_guard = []
    stack = [0]
    value_of_positive =value_of_curr = tree.value[0][0][1]
    while len(stack) > 0:
        found = False
        node_id = stack.pop(0)
        value_of_curr = tree.value[node_id][0]
        left_node_id = tree.children_left[node_id]
        right_node_id = tree.children_right[node_id]
        is_split_node = left_node_id != right_node_id
        if is_split_node:
            value_of_left = tree.value[left_node_id][0]
            value_of_right = tree.value[right_node_id][0]
            if 0 == value_of_right[0]:
                stack.append(left_node_id)
                value_of_positive = value_of_positive - value_of_right[1]
                found = True
            if 0 == value_of_left[0]:
                stack.append(right_node_id)
                value_of_positive = value_of_positive - value_of_left[1]
                found = True
            if value_of_curr[1] == value_of_left[1] and found == False:
                stack.append(left_node_id)
            if value_of_curr[1] == value_of_right[1] and found == False:
                stack.append(right_node_id)
    if value_of_curr[0] == 0:
        value_of_positive = value_of_positive - value_of_curr[1]
    return value_of_positive == 0

def find_must_guards(tree, features):
    # traces = build_traces_list(0, [], [], tree)
    # threasholds = build_therashold_list(0,[],[],tree)
    # leaves = build_is_leaves_list(0,[],tree)
    # features = build_features_list(0,[],[],tree)
    # values = build_values_list(0,[],tree)
    # dictionary_of_classes = {}
    list_of_or_guards = []
    list_of_and_guard = []
    stack = [0]
    add_last_maybe = False
    last_was_and = False
    while len(stack) > 0:
        found = False
        node_id = stack.pop(0)
        value_of_curr = tree.value[node_id][0]
        left_node_id = tree.children_left[node_id]
        right_node_id = tree.children_right[node_id]
        is_split_node = left_node_id != right_node_id
        if is_split_node:
            add_last_maybe = True
            value_of_left = tree.value[left_node_id][0]
            value_of_right = tree.value[right_node_id][0]
            threshold = int(tree.threshold[node_id])
            if value_of_curr[0] == value_of_left[0]:
                copy_list_of_and = list_of_and_guard.copy()
                copy_list_of_and.append((features[tree.feature[node_id]], "bigger", threshold + 1))
                list_of_or_guards.append(copy_list_of_and)
                list_of_and_guard.append((features[tree.feature[node_id]], "smaller", threshold))
                stack.append(left_node_id)
                last_was_and = False
                found = True
            if value_of_curr[0] == value_of_right[0]:
                copy_list_of_and = list_of_and_guard.copy()
                copy_list_of_and.append((features[tree.feature[node_id]], "smaller", threshold))
                list_of_or_guards.append(copy_list_of_and)
                list_of_and_guard.append((features[tree.feature[node_id]], "bigger", threshold + 1))
                stack.append(right_node_id)
                last_was_and = False
                found = True
            if value_of_curr[1] == value_of_left[1] and found == False:
                list_of_and_guard.append((features[tree.feature[node_id]], "smaller", threshold))
                stack.append(left_node_id)
                last_was_and = True
                found = False
            if value_of_curr[1] == value_of_right[1] and found == False:
                list_of_and_guard.append((features[tree.feature[node_id]], "bigger", threshold + 1))
                stack.append(right_node_id)
                last_was_and = True
                found = False

        else:
            if add_last_maybe and value_of_curr[1] > 0 and last_was_and == False:
                list_of_or_guards.append(list_of_and_guard)

    if last_was_and:
        list_of_or_guards.append(list_of_and_guard)
    return list_of_or_guards


def find_features_counter(tree):
    traces = build_traces_list(0, [], [], tree)
    threasholds = build_therashold_list(0, [], [], tree)
    leaves = build_is_leaves_list(0, [], tree)
    features = build_features_list(0, [], [], tree)
    values = build_values_list(0, [], tree)
    dictionary_of_classes = {}
    for counter in range(len(tree.value[0][0])):
        dictionary_of_classes[counter] = build_guard_for_counter(traces, threasholds, leaves, features, values, counter)
    return dictionary_of_classes


def counter_guard_depend_on_features(tree, features):
    dictionary_of_classes = find_features_counter(tree)
    list_of_guards = find_features_guards_for_target_special_case(features, dictionary_of_classes)
    return list_of_guards


def find_features_guards_for_target(features, dictionary_of_features_counter):
    list_of_list_of_guards = []
    for i in range(len(dictionary_of_features_counter)):
        cases = dictionary_of_features_counter.get(i)
        list_of_or_guards = []
        if cases != None:
            for case in cases:
                list_of_and_guards = []
                for guard in case:
                    feature_index, direction, threashold = guard[0], guard[1], guard[2]
                    feature = features[feature_index]
                    threashold = int(threashold)
                    if direction == "left":
                        direction = "smaller"
                    else:
                        direction = "bigger"
                        threashold = threashold + 1
                    list_of_and_guards.append((feature, direction, threashold))
                list_of_or_guards.append(list_of_and_guards)
        list_of_list_of_guards.append(list_of_or_guards)
    return list_of_list_of_guards


def find_features_guards_for_target_special_case(features, dictionary_of_features_counter):
    cases = dictionary_of_features_counter.get(1)
    list_of_or_guards = []
    if cases != None:
        for case in cases:
            list_of_and_guards = []
            for guard in case:
                feature_index, direction, threashold = guard[0], guard[1], guard[2]
                feature = features[feature_index]
                threashold = int(threashold)
                if direction == "left":
                    direction = "smaller"
                else:
                    direction = "bigger"
                    threashold = threashold + 1
                list_of_and_guards.append((feature, direction, threashold))
            # if len(list_of_and_guards)<3:
            #     list_of_or_guards.append(list_of_and_guards)
    return list_of_or_guards


def build_guard_for_target_special_case(net, list_of_or_guards, empty_transitions):
    guards_parameters_list = []
    guards_functions_list = []
    index = 0
    for list_of_guards in list_of_or_guards:
        index_of_internal = 1
        parameters_list = []
        functions_list_internal = []
        # functions_list = []
        for guard in list_of_guards:
            feature, smaller_or_bigger, threashold = guard[0], guard[1], guard[2]
            parameters_list_internal = [net, found_transition(net, empty_transitions[index]),
                                        [found_transition(net, feature)], threashold, index_of_internal]
            if smaller_or_bigger == "smaller":
                functions_list_internal.append(guard_of_max_times)
                index_of_internal = index_of_internal + 1
            else:
                functions_list_internal.append(guard_min_x_times)
                index_of_internal = index_of_internal + 1
            parameters_list.append(parameters_list_internal)
            # functions_list.append(functions_list_internal)
        guards_parameters_list.append(parameters_list)
        guards_functions_list.append(functions_list_internal)
        index = index + 1
    return guards_parameters_list, guards_functions_list


def build_guard_for_target_must_happen(net, list_of_guards, transition_name):
    guards_parameters_list_general = []
    guards_functions_list_general = []
    index = 0
    for and_guards in list_of_guards:
        guards_parameters_list = []
        guards_functions_list = []
        for guard in and_guards:
            feature, smaller_or_bigger, threashold = guard[0], guard[1], guard[2]
            parameters_list_internal = [net, found_transition(net, transition_name), [found_transition(net, feature)],
                                        threashold, index]
            if smaller_or_bigger == "smaller":
                guards_functions_list.append(guard_of_max_times_must_happen)
                index = index + 1
            else:
                guards_functions_list.append(guard_min_x_times_must_happen)
                index = index + 1
            guards_parameters_list.append(parameters_list_internal)
        guards_functions_list_general.append(guards_functions_list)
        guards_parameters_list_general.append(guards_parameters_list)
    return guards_functions_list_general, guards_parameters_list_general


def or_guard_special(net, transition_name, list_of_guards):
    transition = found_transition(net, transition_name)
    pre_places = found_pre_places(transition)
    # pre_places = transition.pre_places
    empty_transitions = create_empty_transitions_for_or_guards(net, len(list_of_guards), pre_places, transition_name)
    remove_xor_edge_from_option_with_xor(net, pre_places, transition_name)
    place_of_or = PetriNet.Place("or place " + transition_name)
    net.places.add(place_of_or)
    guards_parameters_list, guards_functions_list = build_guard_for_target_special_case(net, list_of_guards[1],
                                                                                        empty_transitions)
    apply_or_guards(guards_parameters_list, guards_functions_list)
    add_arcs_from_transition_to_place_of_or(net, empty_transitions, place_of_or)
    transition = found_transition(net, transition_name)
    add_arc_from_place_to_transition(net, place_of_or, transition)


def and_guard(functions, parameters):
    list_of_functions = functions[0]
    list_of_parameters = parameters[0]
    for index in range(len(list_of_functions)):
        function = list_of_functions[index]
        parameter_list = list_of_parameters[index]
        function(*parameter_list)


def apply_must_happen(net, transition_name, must_happen):
    functions, parameters = build_guard_for_target_must_happen(net, must_happen, transition_name)
    if len(must_happen) == 1:
        and_guard(functions, parameters)
    else:
        or_guard_of_and_guards(net, transition_name, functions, parameters)


def build_empty_transition_for_and(net, list_of_functions, list_of_parameters, empty_transition):
    for index in range(len(list_of_functions)):
        function = list_of_functions[index]
        parameter_list = list_of_parameters[index]
        parameter_list[1] = empty_transition
        function(*parameter_list)


def or_guard_of_and_guards(net, transition_name, functions, parameters):
    transition = found_transition(net, transition_name)
    pre_places = found_pre_places(transition)
    # pre_places = transition.pre_places
    empty_transitions = create_empty_transitions_for_or_guards(net, len(functions), pre_places, transition_name)
    remove_xor_edge_from_option_with_xor(net, pre_places, transition_name)
    place_of_or = PetriNet.Place("or place " + transition_name)
    net.places.add(place_of_or)
    for index in range(len(functions)):
        build_empty_transition_for_and(net, functions[index], parameters[index],
                                       found_transition(net, empty_transitions[index]))
    add_arcs_from_transition_to_place_of_or(net, empty_transitions, place_of_or)
    transition = found_transition(net, transition_name)
    add_arc_from_place_to_transition(net, place_of_or, transition)


def build_places_for_target_counter(net, transition_name, max_times):
    places = []
    for i in range(max_times - 1):
        place = PetriNet.Place(transition_name + " happened " + str(i) + " times")
        net.places.add(place)
        places.append(place)
    return places


def add_arc_to_counter_places(net, transition, places_for_target_counter):
    start_transitions = found_start_transitions(net, found_place(net, "source"))
    for start_transition in start_transitions:
        petri_utils.add_arc_from_to(start_transition, places_for_target_counter[0], net, 1)
    for i in range(len(places_for_target_counter) - 1):
        petri_utils.add_arc_from_to(places_for_target_counter[i], transition, net, 1)
        petri_utils.add_arc_from_to(transition, places_for_target_counter[i + 1], net, 1)


# def or_guard_every_target(net,transition_name, list_of_guards):
#     transition = found_transition(net, transition_name)
#     pre_places = found_pre_places(transition)
#     #pre_places = transition.pre_places
#     places_for_target_counter = build_places_for_target_counter(net,transition_name,len(list_of_guards))
#     add_arc_to_counter_places(net,transition,places_for_target_counter)
#     remove_xor_edge_from_option_with_xor(net, pre_places, transition_name)
#     place_of_or = PetriNet.Place("or place " + transition_name)
#     net.places.add(place_of_or)
#     empty_transitions = create_empty_transitions_for_or_guards(net, len(list_of_guards), pre_places, transition_name)
#     guards_parameters_list, guards_functions_list = build_guard_for_target_special_case(net,list_of_guards,empty_transitions)
#     apply_or_guards(guards_parameters_list, guards_functions_list)
#     add_arcs_from_transition_to_place_of_or(net, empty_transitions, place_of_or)
#     transition = found_transition(net, transition_name)
#     add_arc_from_place_to_transition(net, place_of_or, transition)


def found_pre_places(transition):
    places = []
    for arc in transition.in_arcs:
        places.append(arc.source)
    return places


def create_empty_transitions_for_or_guards(net, number_of_or_guards, places, transition_name):
    list_of_empty_transitions = []
    for index in range(number_of_or_guards):
        empty_transition_name = transition_name + " empty transition " + str(index + 1)
        empty_transition = PetriNet.Transition(empty_transition_name, empty_transition_name)
        net.transitions.add(empty_transition)
        list_of_empty_transitions.append(empty_transition_name)
        for place in places:
            add_arc_from_place_to_transition(net, place, empty_transition)
    return list_of_empty_transitions


def remove_xor_edge_from_option_with_xor(net, places, transition_name):
    transition = found_transition(net, transition_name)
    for place in places:
        arc = found_arc(net, place, transition)
        net.arcs.remove(arc)
        transition.in_arcs.remove(arc)
        place.out_arcs.remove(arc)


def found_arc(net, xor_place, transition):
    for arc in net.arcs:
        if arc.target == transition and arc.source == xor_place:
            return arc


def add_arc_from_place_to_transition(net, place_of_or, transition):
    petri_utils.add_arc_from_to(place_of_or, transition, net, 1)


def apply_or_guards(guards_parameters_list, guards_functions_list):
    for index_in_or in range(len(guards_functions_list)):
        # functions = guards_functions_list[index_in_or]
        # functions_paramater_list = guards_parameters_list[index_in_or]
        # for index_of_function in range(len(functions)):
        function = guards_functions_list[index_in_or]
        parameter_list = guards_parameters_list[index_in_or]
        function(*parameter_list)


def apply_or_guards_must_happen(guards_parameters_list, guards_functions_list):
    for index_of_function in range(len(guards_functions_list)):
        function = guards_functions_list[index_of_function]
        parameter_list = guards_parameters_list[index_of_function]
        function(*parameter_list)


def add_arcs_from_transition_to_place_of_or(net, empty_transitions_names, place_of_or):
    for empty_transitions_name in empty_transitions_names:
        empty_transition = found_transition(net, empty_transitions_name)
        petri_utils.add_arc_from_to(empty_transition, place_of_or, net, 1)
        empty_transition.label = None


def or_guard(net, guards_parameters_list, guards_functions_list, transition_name, number_of_or_guards):
    transition = found_transition(net, transition_name)
    pre_places = found_pre_places(transition)
    empty_transitions = create_empty_transitions_for_or_guards(net, number_of_or_guards, pre_places, transition_name)
    remove_xor_edge_from_option_with_xor(net, pre_places, transition_name)
    place_of_or = PetriNet.Place("or place " + transition_name)
    net.places.add(place_of_or)
    apply_or_guards(guards_parameters_list, guards_functions_list)
    add_arcs_from_transition_to_place_of_or(net, empty_transitions, place_of_or)
    transition = found_transition(net, transition_name)
    add_arc_from_place_to_transition(net, place_of_or, transition)


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


def build_log(traces):
    log = []
    for i in range(len(traces)):
        trace_log = build_events(traces[i], i + 1)
        log.extend(trace_log)
    return log


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


def count_transition(trace, transition):
    counter = 0
    for action in trace:
        if action == transition:
            counter = counter + 1
    return counter


def create_csv_file(headlines, data, csv_name):
    with open(csv_name, 'w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(headlines)

        for row in data:
            writer.writerow(row)


def count_transition_until_feature(trace, feature, target):
    if trace.__contains__(target):
        index_of_first = trace.index(target)
        trace = trace[0:index_of_first + 1]
    return count_transition(trace, feature)


def build_csv_for_child_of_xor(rows, column):
    create_csv_file(column, rows, "decision_tree.csv")


def build_csv_for_column_first_occurance(csv, column):
    traces = build_traces_from_csv(csv)
    rows = []
    target = column[len(column) - 1]
    for trace in traces:
        row = []
        for feature in column:
            number_of_occurances = count_transition_until_feature(trace, feature, target)
            row.append(number_of_occurances)
        rows.append(row.copy())
    create_csv_file(column, rows, "decision_tree.csv")


def find_next_index_of_target(trace, target, index):
    next_index = -1
    copy_trace = trace.copy()
    copy_trace = copy_trace[index:]
    if copy_trace.__contains__(target):
        index_of_target = copy_trace.index(target)
        next_index = index + index_of_target
    return next_index


def build_row(trace, column):
    row = []
    for feature in column:
        number_of_occurances = count_transition(trace, feature)
        row.append(number_of_occurances)
    return row


def build_csv_for_column_every_time_target_happen(csv, column):
    traces = build_traces_from_csv(csv)
    rows = []
    target = column[len(column) - 1]
    for trace in traces:
        index_of_prev = 0
        if trace.__contains__(target):
            index_of_next = find_next_index_of_target(trace, target, index_of_prev)
            while index_of_next != -1:
                trace_for_row = trace.copy()[0: index_of_next + 1]
                row = build_row(trace_for_row, column)
                index_of_prev = index_of_next
                rows.append(row)
                index_of_next = find_next_index_of_target(trace, target, index_of_prev + 1)
        else:
            row = build_row(trace, column)
            rows.append(row)
    create_csv_file(column, rows, "decision_tree.csv")
    return len(rows)


def build_prefixes(traces):
    list_of_prefixes = []
    list_of_prefixes.append([])
    for trace in traces:
        for length_of_prefix in range(len(trace)):
            prefix = trace[0:length_of_prefix + 1]
            list_of_prefixes.append(prefix.copy())
    return list_of_prefixes


def build_csv_for_prefixes(net, csv, column, initial_marking, final_marking):
    traces = build_traces_from_csv(csv)
    prefixes = build_prefixes(traces)
    rows = []
    target = column[len(column) - 1]
    features = column[:-1]
    good_prefixes, bad_prefixes = build_good_and_bad_prefixes_for_transition(net, prefixes, target, initial_marking,
                                                                             final_marking)
    for good_prefix in good_prefixes:
        row = build_row(good_prefix, features)
        row.append(1)
        rows.append(row)
    for bad_prefix in bad_prefixes:
        row = build_row(bad_prefix, features)
        row.append(0)
        rows.append(row)
    create_csv_file(column, rows, "decision_tree.csv")
    return len(rows)


def build_all_decision_trees_first_occurance(net, csv, col_name):
    columns = builds_all_target(col_name)
    for column in columns:
        # if column[len(column)-1] == "Send Purchase Order Update":
        #     print("f")
        build_csv_for_column_every_time_target_happen(csv, column)
        csv_decision = pd.read_csv("decision_tree.csv", header=None, names=column)
        tree = build_decision_tree(csv_decision, column)
        list_of_guards = counter_guard_depend_on_features(tree, column)
        # if len(list_of_guards)>0:
        #     or_guard_special(net, column[len(column) - 1:][0], list_of_guards)


def list_of_guards_must_happen(tree, features):
    list_of_guards = find_must_guard_new(tree, features)
    return list_of_guards


def counter_guard_depend_on_features_every_time_target_happen(tree, features):
    dictionary_of_classes = find_features_counter(tree)
    list_of_guards = find_features_guards_for_target(features, dictionary_of_classes)
    return list_of_guards


def transitions_must_happen(list_of_guards):
    list_of_guards_for_transition_to_happen = list_of_guards[1]
    set_of_intersection = set(list_of_guards_for_transition_to_happen[0])
    for list_of_g in list_of_guards_for_transition_to_happen[1:]:
        set_of_intersection = set_of_intersection.intersection(list_of_g)
    list_of_intersection = list(set_of_intersection)
    for i in range(len(list_of_guards_for_transition_to_happen)):
        list_of_guards_for_transition_to_happen[i] = list(
            set(list_of_guards_for_transition_to_happen[i]).difference(list_of_intersection))
    return list_of_intersection


def features_must_happen_for_target(must_happen):
    features_must_happen = []
    for guard in must_happen:
        feature = guard[0]
        features_must_happen.append(feature)
    return features_must_happen


def get_features_of_class(list_of_guards):
    features = []
    for or_guard in list_of_guards:
        for guard in or_guard:
            feature = guard[0]
            features.append(feature)
    return features


def get_features_appears_in_every_class(list_of_guards):
    list_of_features_for_every_class = []
    for class_of_target in range(len(list_of_guards) - 1):
        features_in_class = get_features_of_class(list_of_guards[class_of_target + 1])
        list_of_features_for_every_class.append(features_in_class)
    set_of_intersection = set(list_of_features_for_every_class[0])
    for list_of_features in list_of_features_for_every_class[1:]:
        set_of_intersection = set_of_intersection.intersection(list_of_features)
    list_of_intersection = list(set_of_intersection)
    return list_of_intersection


def find_connection(features_appears_in_every_class, target):
    pass


def build_all_decision_trees_every_time_target_happen(net, csv, col_name, initial_marking, final_marking):
    copy_net = net.__deepcopy__()
    columns = builds_all_target(col_name)
    for column in columns:
        target_name = column[len(column) - 1:][0]
        # if target_name == "Change Price":
        #     x=5
        rows_number = build_csv_for_prefixes(copy_net, csv, column, initial_marking, final_marking)
        # build_csv_for_column_every_time_target_happen(csv,column)
        if rows_number > 9:
            csv_decision = pd.read_csv("decision_tree.csv", header=None, names=column)
            tree = build_decision_tree(csv_decision, column)
            list_of_guards = list_of_guards_must_happen(tree, column)
            # print(target_name)
            # print(list_of_guards)
            if len(list_of_guards) > 0:
                apply_must_happen(net, target_name, list_of_guards)
            # list_of_guards = counter_guard_depend_on_features_every_time_target_happen(tree, column)
            # apply_must_happen(net, column[len(column) - 1:][0], list_of_guards)
            # if len(list_of_guards) > 1 and len(list_of_guards[1]) > 0:
            #     must_happen = transitions_must_happen(list_of_guards)
            #     apply_must_happen(net, column[len(column) - 1:][0], must_happen)
            #     if list_of_guards[1] != [[]]:
            #         or_guard_depend_on_features_every_time_target_happen(net, column[len(column) - 1:][0], list_of_guards)
            # features_must_happen = features_must_happen_for_target(must_happen)
            # column = list(set(column).difference(features_must_happen))
            # build_csv_for_column_every_time_target_happen(csv,column)
            # csv_decision = pd.read_csv("decision_tree.csv", header=None, names=column)
            # tree = build_decision_tree(csv_decision, column)
            # list_of_guards = counter_guard_depend_on_features_every_time_target_happen(tree, column)
            # features_appears_in_every_class = get_features_appears_in_every_class(list_of_guards)
            # connection_between_features_to_target = find_connection(features_appears_in_every_class, column[len(column) - 1:][0])


def create_ec_kitty_guard_in_net(net, tree):
    pass


def create_ec_kitty_tree(net, csv, col_name):
    columns = builds_all_target(col_name)
    for column in columns:
        target_name = column[len(column) - 1:][0]
        # print("target: ", target_name)
        rows_number = build_csv_for_column_every_time_target_happen(csv, column)
        if rows_number > 9:
            csv_decision = pd.read_csv("decision_tree.csv", header=None, names=column)
            regression = EC_KITTY_SKL.ec_kitty_tree(csv_decision, column)
            tree = regression.algorithm.best_of_run_.tree
            if regression.algorithm.best_of_run_.fitness.fitness == 0:
                print("predicted ", target_name, " succesfully using ec kitty")
                for node in tree:
                    print_node = ""
                    if type(node) is str:
                        print_node = column[int(node[1:])]
                    if type(node) is int:
                        print_node = node
                    if callable(node):
                        print_node = getattr(node, "__name__", None)
                    print(print_node)


def has_empty_child(process_tree_Inductive):
    for children in process_tree_Inductive.children:
        if len(children.children) == 0 and children.label == None:
            return True
    return False


def check_if_has_empty_transition_another_way_helper(process_tree):
    has_empty_transition_another_way = False
    if process_tree.label != None:
        return False
    children_empty = len(process_tree.children) == 0 and process_tree.label == None
    if children_empty:
        return True
    xor_node = (process_tree.operator.value == "X")
    seq_node = (process_tree.operator.value == "->")
    loop_node = (process_tree.operator.value == "*")
    parallel_node = (process_tree.operator.value == "+")
    if xor_node:
        for children in process_tree.children:
            has_empty_transition_another_way = has_empty_transition_another_way or check_if_has_empty_transition_another_way_helper(
                children)
    if seq_node or parallel_node:
        all_children = True
        for children in process_tree.children:
            all_children = all_children and check_if_has_empty_transition_another_way_helper(
                children)
        has_empty_transition_another_way = all_children
    if loop_node:
        has_empty_transition_another_way = check_if_has_empty_transition_another_way_helper(process_tree.children[0])
    return has_empty_transition_another_way


def check_if_has_empty_transition_another_way(process_tree):
    for children in process_tree.children:
        children_empty = len(children.children) == 0 and children.label == None
        if children_empty == False:
            has_by_another = check_if_has_empty_transition_another_way_helper(children)
            if has_by_another:
                return True
    return False


def node_without_empty(process_tree):
    return has_empty_child(process_tree) == False and check_if_has_empty_transition_another_way(process_tree) == False


def find_xor_node(pointer, xor_nodes):
    index = 0
    for node in xor_nodes:
        if pointer == node:
            return index
        else:
            index = index + 1


def found_way(tree, transition):
    if len(tree.children) == 0:
        if tree.label == None:
            return False
        else:
            return tree.label == transition
    if len(tree.children) > 0:
        ans = False
        for children in tree.children:
            ans = ans or found_way(children, transition)
    return ans


def find_child_index(tree, transition):
    index = 0
    for node in tree.children:
        if found_way(node, transition):
            return index
        else:
            index = index + 1


def find_pointer_index(pointers, transition):
    index = 0
    for node in pointers:
        if found_way(node, transition):
            return index
        else:
            index = index + 1
    return -1


def in_transition(process_tree, transition):
    return len(process_tree.children) == 0 and process_tree.label != None and process_tree.label == transition


def is_child_helper(node, curr, child):
    if node == curr:
        return node != child
    else:
        is_child_bool = False
        for children in curr.children:
            is_child_bool = is_child_bool or is_child_helper(node, children, child)
        return is_child_bool


def is_child(node, child):
    return is_child_helper(node, child, child)


def delete_from_list_childs(child, seq_loop_emergency_pointers, indexes_of_childs, pointers):
    list_of_indexes_to_delete = []
    for index in range(len(seq_loop_emergency_pointers)):
        node = seq_loop_emergency_pointers[index]
        if is_child(node, child):
            list_of_indexes_to_delete.append(index)
    for index in sorted(list_of_indexes_to_delete, reverse=True):
        seq_loop_emergency_pointers.pop(index)
        indexes_of_childs.pop(index)

    list_of_indexes_to_delete = []
    for index in range(len(pointers)):
        node = pointers[index]
        if is_child(node, child):
            list_of_indexes_to_delete.append(index)
    for index in sorted(list_of_indexes_to_delete, reverse=True):
        pointers.pop(index)


def node_without_empty_right_xor(node):
    right_childrens = node.children[1:]
    for right_children in right_childrens:
        if node_without_empty(right_children):
            return False
    return True


def add_contrast_empty(node, start_index, end_index, list_of_xor_and_choices, nodes, enabled_transitions_for_nodes,
                       rows, row):
    for index in range(start_index, end_index, 1):
        index_of_node = find_xor_node(node.children[index], nodes)
        transitions_enabled = enabled_transitions_for_nodes[index_of_node]
        row_copy = row.copy()
        row_copy.append("empty transition")
        row_copy.append(transitions_enabled)
        rows.append(row_copy)


def find_emergency_pointer_index(seq_loop_emergency_pointers, indexes_of_childs, transition, pointers,
                                 list_of_xor_and_choices, nodes, enabled_transitions_for_nodes, rows, row):
    last_index = len(seq_loop_emergency_pointers) - 1
    for i in range(len(seq_loop_emergency_pointers)):
        curr_index = last_index - i
        node = seq_loop_emergency_pointers[curr_index]
        child_index = indexes_of_childs[curr_index]
        seq_node = (node.operator.value == "->")
        if seq_node:
            child = node.children[child_index]
            if found_way(child, transition):
                if len(node.children) > child_index + 1:
                    indexes_of_childs[curr_index] = child_index + 1
                else:
                    index_of_node_deleted = seq_loop_emergency_pointers.index(node)
                    del seq_loop_emergency_pointers[index_of_node_deleted]
                    del indexes_of_childs[index_of_node_deleted]
                delete_from_list_childs(node, seq_loop_emergency_pointers, indexes_of_childs, pointers)
                return node
            else:
                if node_without_empty(child) == False or (child.operator == "X" and seq_loop_emergency_pointers.__contains__(child) == False):
                    for i in range(len(node.children) - child_index - 1):
                        new_child_index = child_index + i + 1
                        child = node.children[new_child_index]
                        if found_way(child, transition):
                            add_contrast_empty(node, child_index, new_child_index, list_of_xor_and_choices, nodes,
                                               enabled_transitions_for_nodes, rows, row)
                            if len(node.children) > child_index + 1:
                                indexes_of_childs[curr_index] = child_index + 1
                            else:
                                index_of_node_deleted = seq_loop_emergency_pointers.index(node)
                                del seq_loop_emergency_pointers[index_of_node_deleted]
                                del indexes_of_childs[index_of_node_deleted]
                            delete_from_list_childs(node, seq_loop_emergency_pointers, indexes_of_childs, pointers)
                            return node

        else:
            child = node.children[child_index]
            if child_index == 0:
                if found_way(child, transition):
                    indexes_of_childs[curr_index] = 1
                    delete_from_list_childs(node, seq_loop_emergency_pointers, indexes_of_childs, pointers)
                    return node
                else:
                    if node_without_empty(child) == False:
                        for child in node.children[1:]:
                            if found_way(child, transition):
                                indexes_of_childs[curr_index] = 0
                                delete_from_list_childs(node, seq_loop_emergency_pointers, indexes_of_childs, pointers)
                                return node
            else:
                while len(node.children) >= child_index + 1:
                    child = node.children[child_index]
                    child_index = child_index + 1
                    if found_way(child, transition):
                        indexes_of_childs[curr_index] = 0
                        delete_from_list_childs(node, seq_loop_emergency_pointers, indexes_of_childs, pointers)
                        return node
                if node_without_empty_right_xor(node) == False:
                    child = node.children[0]
                    if found_way(child, transition):
                        indexes_of_childs[curr_index] = 1
                        delete_from_list_childs(node, seq_loop_emergency_pointers, indexes_of_childs, pointers)
                        return node


def build_list_of_xor_and_choices(process_tree, pointers, seq_loop_emergency_pointers, indexes_of_childs, xor_nodes,
                                  activities_enables_for_nodes,
                                  transition, list_of_xor_choices, appended, transitions_enabled, rows, row):
    if len(pointers) > 0 and in_transition(pointers[0], transition):
        pointers.pop(0)
        return True
    else:
        stop = False
        not_from_pointers = False
        while not stop:
            child_index = find_pointer_index(pointers, transition)
            if child_index == -1:
                not_from_pointers = True
                pointer = find_emergency_pointer_index(seq_loop_emergency_pointers, indexes_of_childs, transition,
                                                       pointers, list_of_xor_choices, xor_nodes,
                                                       activities_enables_for_nodes, rows, row)
            else:
                pointer = pointers[child_index]
            child_index = find_child_index(pointer, transition)
            if len(pointer.children) == 0:
                pointers.remove(pointer)
                return True
            if not_from_pointers and len(pointer.children[child_index].children) == 0:
                return True
            xor_node = (pointer.operator.value == "X")
            seq_node = (pointer.operator.value == "->")
            loop_node = (pointer.operator.value == "*")
            parallel_node = (pointer.operator.value == "+")
            if not_from_pointers:
                index_of_node = find_xor_node(pointer.children[child_index], xor_nodes)
            else:
                index_of_node = find_xor_node(pointer, xor_nodes)
            transitions_enabled_for_current_node = activities_enables_for_nodes[index_of_node]
            for transition_enabled_for_current_node in transitions_enabled_for_current_node:
                if not transitions_enabled.__contains__(transition_enabled_for_current_node):
                    transitions_enabled.append(transition_enabled_for_current_node)
            if seq_node:
                if pointers.__contains__(pointer):
                    pointers.remove(pointer)
                if child_index + 1 != len(pointer.children) and not seq_loop_emergency_pointers.__contains__(pointer):
                    seq_loop_emergency_pointers.append(pointer)
                    indexes_of_childs.append(child_index + 1)
                pointers.insert(0, pointer.children[child_index])
                stop = build_list_of_xor_and_choices(process_tree, pointers, seq_loop_emergency_pointers,
                                                     indexes_of_childs, xor_nodes, activities_enables_for_nodes,
                                                     transition,
                                                     list_of_xor_choices, appended, transitions_enabled, rows, row)
            if parallel_node:
                # if pointers.__contains__(pointer):
                #     pointers.remove(pointer)
                pointers.insert(0, pointer.children[child_index])
                for index_of_child in range(len(pointer.children)):
                    if child_index != index_of_child:
                        if pointers.__contains__(pointer.children[index_of_child]) == False:
                            pointers.append(pointer.children[index_of_child])
                stop = build_list_of_xor_and_choices(process_tree, pointers, seq_loop_emergency_pointers,
                                                     indexes_of_childs, xor_nodes, activities_enables_for_nodes,
                                                     transition,
                                                     list_of_xor_choices, appended, transitions_enabled, rows, row)
            if xor_node:
                if pointers.__contains__(pointer):
                    pointers.remove(pointer)
                pointers.insert(0, pointer.children[child_index])
                stop = build_list_of_xor_and_choices(process_tree, pointers, seq_loop_emergency_pointers,
                                                     indexes_of_childs, xor_nodes, activities_enables_for_nodes,
                                                     transition,
                                                     list_of_xor_choices, appended, transitions_enabled, rows, row)
            if loop_node:
                if pointers.__contains__(pointer):
                    pointers.remove(pointer)
                if not seq_loop_emergency_pointers.__contains__(pointer):
                    seq_loop_emergency_pointers.append(pointer)
                    if child_index == 0:
                        indexes_of_childs.append(1)
                    else:
                        indexes_of_childs.append(0)
                pointers.insert(0, pointer.children[child_index])
                stop = build_list_of_xor_and_choices(process_tree, pointers, seq_loop_emergency_pointers,
                                                     indexes_of_childs, xor_nodes, activities_enables_for_nodes,
                                                     transition,
                                                     list_of_xor_choices, appended, transitions_enabled, rows, row)

    return stop


# def build_list_of_xor_and_choices(process_tree, pointers, xor_nodes, transition, list_of_xor_choices):
#     if len(pointers)>0 and in_transition(pointers[0],transition):
#         pointers.pop(0)
#         return True
#     else:
#         stop = False
#         for index in range(len(pointers.copy())):
#             pointer = pointers[index]
#             if found_way(pointer, transition) and not stop:
#                 child_index = find_child_index(pointer, transition)
#                 xor_node = (pointer.operator.value == "X")
#                 seq_node = (pointer.operator.value == "->")
#                 loop_node = (pointer.operator.value == "*")
#                 parallel_node = (pointer.operator.value == "+")
#                 if seq_node:
#                     pointers.remove(pointer)
#                     pointers.insert(0, pointer.children[child_index])
#                     stop = build_list_of_xor_and_choices(process_tree, pointers, xor_nodes, transition,
#                                                   list_of_xor_choices)
#                 if parallel_node:
#                     pointers.remove(pointer)
#                     pointers.insert(0, pointer.children[child_index])
#                     for index_of_child in range(len(pointer.children)):
#                         if child_index != index_of_child:
#                             pointers.append(pointer.children[index_of_child])
#                     stop = build_list_of_xor_and_choices(process_tree, pointers, xor_nodes, transition,
#                                                   list_of_xor_choices)
#                 if xor_node:
#                     pointers.remove(pointer)
#                     index_of_xor_node = find_xor_node(pointer, xor_nodes)
#                     list_of_xor_choices.append((index_of_xor_node, child_index))
#                     pointers.insert(0, pointer.children[child_index])
#                     stop = build_list_of_xor_and_choices(process_tree, pointers, xor_nodes, transition,
#                                                   list_of_xor_choices)
#                 if loop_node:
#                     pointers.remove(pointer)
#                     pointers.insert(0, pointer.children[child_index])
#                     stop = build_list_of_xor_and_choices(process_tree, pointers, xor_nodes, transition,
#                                                   list_of_xor_choices)
#
#     return False
def build_list_of_xor_nodes_and_choses(process_tree, traces, xor_nodes, activities_enables_for_nodes, column):
    rows = []
    for trace in traces:
        for index in range(len(trace)):
            list_of_xor_and_choices = []
            if index == 0:
                pointers = [process_tree]
                seq_loop = []
                indexes_seq_loop = []
            pref = trace[0:index + 1]
            row = build_row(pref[:-1], column)
            transitions_enabled = []
            build_list_of_xor_and_choices(process_tree, pointers, seq_loop, indexes_seq_loop, xor_nodes,
                                          activities_enables_for_nodes, trace[index],
                                          list_of_xor_and_choices, False, transitions_enabled, rows, row)
            row_copy = row.copy()
            row_copy.append(trace[index])
            row_copy.append(transitions_enabled)
            rows.append(row_copy)
    return rows


def is_transition_and_not_an_empty_one(tree):
    return len(tree.children) == 0 and tree.label != None


def is_empty_transition(tree):
    return len(tree.children) == 0 and tree.label == None


def build_first_options_of_tree(tree, activities_for_node):
    xor_node = (tree.operator.value == "X")
    seq_node = (tree.operator.value == "->")
    loop_node = (tree.operator.value == "*")
    parallel_node = (tree.operator.value == "+")
    if xor_node or parallel_node:
        for child in tree.children:
            if is_transition_and_not_an_empty_one(child):
                activities_for_node.append(child.label)
            elif is_empty_transition(child) == False:
                build_first_options_of_tree(child, activities_for_node)
    if seq_node:
        left_child = tree.children[0]
        if is_transition_and_not_an_empty_one(left_child):
            activities_for_node.append(left_child.label)
        else:
            stop = False
            index = 0
            while index < len(tree.children) and stop == False:
                stop = (node_without_empty(tree.children[index]) == False)
                if is_transition_and_not_an_empty_one(tree.children[index]):
                    activities_for_node.append(tree.children[index].label)
                else:
                    build_first_options_of_tree(tree.children[index], activities_for_node)
    if loop_node:
        left_child = tree.children[0]
        if is_transition_and_not_an_empty_one(left_child):
            activities_for_node.append(left_child.label)
        elif node_without_empty(left_child):
            build_first_options_of_tree(left_child, activities_for_node)
        else:
            stop = False
            index = 0
            while index < len(tree.children) and stop == False:
                stop = (node_without_empty(tree.children[index]) == False)
                if is_transition_and_not_an_empty_one(tree.children[index]):
                    activities_for_node.append(tree.children[index].label)
                else:
                    build_first_options_of_tree(tree.children[index], activities_for_node)


def build_xor_nodes(tree, nodes, activities_enabled_for_nodes):
    activities_enabled_for_node = []
    if len(tree.children) > 0:
        xor_node = (tree.operator.value == "X")
        loop_node = (tree.operator.value == "*")
        seq_node = (tree.operator.value == "->")
        parallel_node = (tree.operator.value == "+")
        if xor_node or loop_node or parallel_node or seq_node:
            nodes.append(tree)
            build_first_options_of_tree(tree, activities_enabled_for_node)
            activities_enabled_for_nodes.append(activities_enabled_for_node)
        for children in tree.children:
            build_xor_nodes(children, nodes, activities_enabled_for_nodes)


def clear_rows(rows):
    for row in rows.copy():
        chosen = row[len(row)-1]
        if not chosen:
            copy_row = row.copy()
            features = copy_row[:-1]
            features.append(1)
            if rows.__contains__(features):
                rows.remove(row)



def build_rows(list_of_xor_nodes_and_choses, target_name):
    rows = []
    for row in list_of_xor_nodes_and_choses:
        row_without_target = row[:-2]
        transition_chosen = row[len(row) - 2]
        transitions_enabled = row[len(row) - 1]
        if transitions_enabled.__contains__(target_name):
            row_to_append = row_without_target.copy()
            if target_name == transition_chosen:
                row_to_append.append(1)
            else:
                row_to_append.append(0)
            rows.append(row_to_append)
    clear_rows(rows)
    return rows


def build_rows_for_target(list_of_xor_nodes_and_choses, index):
    rows = []
    for row in list_of_xor_nodes_and_choses:
        row_without_index = []
        for index_in_row in range(len(row)):
            if index != index_in_row:
                row_without_index.append(row[index_in_row])
        rows.append(row_without_index)
    return rows


def get_must_happen_special_guard(tree, features):
    left_node_id = tree.children_left[0]
    right_node_id = tree.children_right[0]
    value_of_left = tree.value[left_node_id][0]
    value_of_right = tree.value[right_node_id][0]
    threshold = int(tree.threshold[0])
    if 0 == value_of_right[1]:
        return (features[tree.feature[0]], "smaller", threshold)
    if 0 == value_of_left[1]:
        return (features[tree.feature[0]], "bigger", threshold + 1)
    return None


def get_must_happen_special_guards(tree, features):
    list_of_and_guard = []
    stack = [0]
    while len(stack) > 0:
        node_id = stack.pop(0)
        left_node_id = tree.children_left[node_id]
        right_node_id = tree.children_right[node_id]
        value_of_left = tree.value[left_node_id][0]
        value_of_right = tree.value[right_node_id][0]
        threshold = int(tree.threshold[node_id])
        is_split_node = left_node_id != right_node_id
        if is_split_node:
            if 0 == value_of_right[1]:
                list_of_and_guard.append((features[tree.feature[node_id]], "smaller", threshold))
                stack.append(left_node_id)
            if 0 == value_of_left[1]:
                list_of_and_guard.append((features[tree.feature[node_id]], "bigger", threshold + 1))
                stack.append(right_node_id)
    return list_of_and_guard

def apply_special_must_happen(net, transition_name, guard):
    feature, smaller_or_bigger, threashold = guard[0], guard[1], guard[2]
    parameter_list = [net, found_transition(net, transition_name), [found_transition(net, feature)],
                      threashold, 0]
    if smaller_or_bigger == "smaller":
        function = guard_of_max_times_must_happen
    else:
        function = guard_min_x_times_must_happen
    function(*parameter_list)

def add_xor_guards(tree, net, train_log, col_name):
    traces = build_traces_from_csv(train_log)
    nodes = []
    activities_enables_for_nodes = []
    build_xor_nodes(tree, nodes, activities_enables_for_nodes)
    list_of_xor_nodes_and_choses = build_list_of_xor_nodes_and_choses(tree, traces, nodes, activities_enables_for_nodes,
                                                                      col_name)
    columns = builds_all_target(col_name)
    for column in columns:
        col_name_copy = col_name.copy()
        target_name = column[len(column) - 1]
        index_of_target = col_name.index(target_name)
        col_name_copy.remove(target_name)
        col_name_copy.append(target_name)
        list_of_xor_nodes_and_choses_for_target = build_rows_for_target(list_of_xor_nodes_and_choses,
                                                                        index_of_target)
        rows = build_rows(list_of_xor_nodes_and_choses_for_target, target_name)
        if len(rows) > 10:
            build_csv_for_child_of_xor(rows, col_name_copy)
            csv_decision = pd.read_csv("decision_tree.csv", header=None, names=col_name_copy)
            tree = build_decision_tree(csv_decision, col_name_copy)
            if tree.capacity > 1:
                # print(target_name)
                #must_happen_special_guard = get_must_happen_special_guard(tree, col_name_copy)
                must_happen_special_guards = get_must_happen_special_guards(tree,col_name_copy)
                # print(must_happen_special_guards)
                list_of_guards = list_of_guards_must_happen(tree, col_name_copy)
                for must_happen_special_guard in must_happen_special_guards:
                    apply_special_must_happen(net, target_name, must_happen_special_guard)
                    for list_of_guards_internal in list_of_guards:
                        if list_of_guards_internal.__contains__(must_happen_special_guard):
                            list_of_guards_internal.remove(must_happen_special_guard)
                            if len(list_of_guards_internal) == 0:
                                list_of_guards.remove(list_of_guards_internal)
                if len(list_of_guards) > 0:
                    # print(list_of_guards)
                    apply_must_happen(net, target_name, list_of_guards)
        col_name_copy.remove(target_name)
        col_name_copy.insert(index_of_target, target_name)


def check_delete_empty(tree, special_transitions):
    activities_enabled_for_node = []
    build_first_options_of_tree(tree, activities_enabled_for_node)
    delete_empty_transition = all(element in special_transitions for element in activities_enabled_for_node)
    if delete_empty_transition:
        for child in tree.children:
            if len(child.children) == 0 and child.label == None:
                tree.children.remove(child)
        if len(tree.children) == 1:
            index_of_tree_in_parent = tree.parent.children.index(tree)
            tree.parent.children[index_of_tree_in_parent] = tree.children[0]
            tree.children[0].parent = tree.parent

def delete_empty_transitions_active(tree, special_transitions):
    if len(tree.children) > 0:
        xor_node = (tree.operator.value == "X")
        if xor_node and has_empty_child(tree):
            check_delete_empty(tree,special_transitions)
        for child in tree.children:
            delete_empty_transitions_active(child,special_transitions)

def delete_empty_transitions(process_tree, train_log, col_name):
    traces = build_traces_from_csv(train_log)
    nodes = []
    activities_enables_for_nodes = []
    build_xor_nodes(process_tree, nodes, activities_enables_for_nodes)
    list_of_xor_nodes_and_choses = build_list_of_xor_nodes_and_choses(process_tree, traces, nodes, activities_enables_for_nodes,
                                                                      col_name)
    columns = builds_all_target(col_name)
    special_transitions = []
    for column in columns:
        col_name_copy = col_name.copy()
        target_name = column[len(column) - 1]
        index_of_target = col_name.index(target_name)
        col_name_copy.remove(target_name)
        col_name_copy.append(target_name)
        list_of_xor_nodes_and_choses_for_target = build_rows_for_target(list_of_xor_nodes_and_choses,
                                                                        index_of_target)
        rows = build_rows(list_of_xor_nodes_and_choses_for_target, target_name)
        if len(rows) > 10:
            build_csv_for_child_of_xor(rows, col_name_copy)
            csv_decision = pd.read_csv("decision_tree.csv", header=None, names=col_name_copy)
            tree = build_decision_tree(csv_decision, col_name_copy)
            if tree.capacity > 1:
                special_transition_condition = special_transition_condition_function(tree, col_name_copy)
                if special_transition_condition:
                    special_transitions.append(target_name)
        col_name_copy.remove(target_name)
        col_name_copy.insert(index_of_target, target_name)
    delete_empty_transitions_active(process_tree, special_transitions)


def transition_enabled(transition, marking):
    for arc in transition.in_arcs:
        if marking[arc.source] < arc.weight:
            return False
    return True


def build_initial_marking(net):
    marking = {}
    for place in net.places:
        if place.name != 'source':
            marking[place] = 0
        else:
            marking[place] = 1
    return marking


# Function that return set of the None transitions that we can do
def group_of_can_do_transitions(transitions, dict_of_tokens):
    set_of_None_can_do_transitions = set()
    for transition in transitions:
        if transition.label == None:
            if transition_enabled(transition, dict_of_tokens):
                set_of_None_can_do_transitions.add(transition)
    return set_of_None_can_do_transitions


def activate_transition(transition: PetriNet.Transition, dictionary_of_tokens_copy):
    arcs_in = transition.in_arcs
    for arc in arcs_in:
        dictionary_of_tokens_copy[arc.source] = dictionary_of_tokens_copy[arc.source] - arc.weight
    arcs_out = transition.out_arcs
    for arc in arcs_out:
        dictionary_of_tokens_copy[arc.target] = dictionary_of_tokens_copy[arc.target] + arc.weight


# Function that return if a trace is in the net
def check_if_trace_in_net(net, trace, final_marking, dict_of_tokens):
    trace_in_net = False
    set_of_activate_None_transitions = group_of_can_do_transitions(net.transitions, dict_of_tokens)
    for None_activate_transition in set_of_activate_None_transitions:
        dictionary_of_tokens_copy = dict_of_tokens.copy()
        activate_transition(None_activate_transition, dictionary_of_tokens_copy)
        trace_in_net = trace_in_net or check_if_trace_in_net(net, trace, final_marking, dictionary_of_tokens_copy)
    if len(trace) == 0:
        trace_in_net = True
    else:
        label_transition = found_transition(net, trace[0])
        if transition_enabled(label_transition, dict_of_tokens):
            dictionary_of_tokens_copy = dict_of_tokens.copy()
            activate_transition(label_transition, dictionary_of_tokens_copy)
            trace_in_net = trace_in_net or check_if_trace_in_net(net, trace[1:], final_marking,
                                                                 dictionary_of_tokens_copy)
    return trace_in_net


def import_csv(file_path):
    event_log = pd.read_csv(file_path, sep=';')
    event_log['case ID'] = event_log['case ID'].astype(str)
    event_log['activity'] = event_log['activity'].astype(str)
    event_log['timestamp'] = pd.to_datetime(event_log['timestamp'], format='mixed')
    return event_log


def build_good_and_bad_prefixes_for_transition(net, prefixes, transition, initial_marking, final_marking):
    list_of_good_prefixes = []
    list_of_bad_prefixes = []
    prefixes_in_net = []
    prefixes_original = []
    for prefix in prefixes:
        prefixes_original.append(prefix.copy())
        prefix.append(transition)
    log = build_log(prefixes)
    create_train_log(log)
    train_log = import_csv("C:/Users/עידו שפירא/PycharmProjects/play/train_log.csv")
    replayed_traces = pm4py.conformance_diagnostics_token_based_replay(train_log, net, initial_marking, final_marking,
                                                                       "activity", "timestamp",
                                                                       "case ID")
    index_of_prefix = 0
    for trace in replayed_traces:
        if trace['missing_tokens'] == 1:
            trace_with_transition = prefixes[index_of_prefix]
            trace_without_transition = prefixes_original[index_of_prefix]
            if prefixes_original.__contains__(trace_with_transition) and list_of_good_prefixes.__contains__(
                    trace_without_transition) == False:
                list_of_good_prefixes.append(trace_without_transition)
            if prefixes_original.__contains__(trace_with_transition) == False and list_of_bad_prefixes.__contains__(
                    trace_without_transition) == False:
                list_of_bad_prefixes.append(trace_without_transition)
        index_of_prefix = index_of_prefix + 1

    return list_of_good_prefixes, list_of_bad_prefixes


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
    trace_number = 0
    for trace in traces:
        trace_log = build_events(trace, trace_number + 1)
        trace_number = trace_number + 1
        log.extend(trace_log)
    return log


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


def create_train_log(log):
    timestamp = ''
    last_case_id = 0
    list_of_events_for_log = []
    for event in log:
        case_id = event.get("case_id")[5:]
        activity = event.get("activity")
        if int(case_id) != last_case_id:
            timestamp = '1700-12-30'
            last_case_id = int(case_id)
        else:
            timestamp = add_one_year(timestamp)
        event_for_log = case_id + ';' + activity + ';' + timestamp
        list_of_events_for_log.append([event_for_log])
    create_csv_file(['case ID;activity;timestamp'], list_of_events_for_log, 'train_log.csv')
