import csv
import subprocess
from datetime import datetime
import pandas as pd

import ApplyPonyGuard


def build_csv_for_child_of_xor(rows, column):
    create_csv_file(column, rows, "C:/Users/עידו שפירא/PycharmProjects/play/PonyGE2/datasets/decision_tree.csv")

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


def build_row(trace, column):
    row = []
    for feature in column:
        number_of_occurances = count_transition(trace, feature)
        row.append(number_of_occurances)
    return row



def has_empty_child(process_tree_Inductive):
    if len(process_tree_Inductive.children) == 0 and process_tree_Inductive.label == None:
        return True
    for children in process_tree_Inductive.children:
        if has_empty_child(children):
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
    for index in range(len(pointers) - 1, -1, -1):
        node = pointers[index]
        if found_way(node, transition):
            return index
    return -1


def in_transition(process_tree, transition):
    return len(process_tree.children) == 0 and process_tree.label != None and process_tree.label == transition




def is_son_of(node, pointer):
    if node.parent == None or node == pointer:
        return False
    if node.parent == pointer:
        return True
    return is_son_of(node.parent, pointer)

def transitions_can_happen_in_pointer(pointer, names_of_transitions):
    if len(pointer.children) == 0:
        if pointer.label != None:
            names_of_transitions.append(pointer.label)
    else:
        xor_node = (pointer.operator.value == "X")
        loop_node = (pointer.operator.value == "*")
        seq_node = (pointer.operator.value == "->")
        parallel_node = (pointer.operator.value == "+")
        if xor_node or parallel_node:
            for children in pointer.children:
                transitions_can_happen_in_pointer(children, names_of_transitions)
        if seq_node:
            cont = True
            for children in pointer.children:
                if cont:
                    transitions_can_happen_in_pointer(children, names_of_transitions)
                    cont = not (pointer_not_empty(children))
        if loop_node:
            transitions_can_happen_in_pointer(pointer.children[0], names_of_transitions)
            if not (pointer_not_empty(pointer.children[0])):
                for children in pointer.children[1:]:
                    transitions_can_happen_in_pointer(children, names_of_transitions)


def pointer_not_empty(pointer):
    if len(pointer.children) == 0:
        return pointer.label != None
    xor_node = (pointer.operator.value == "X")
    loop_node = (pointer.operator.value == "*")
    seq_node = (pointer.operator.value == "->")
    parallel_node = (pointer.operator.value == "+")
    if xor_node:
        ans = True
        for child in pointer.children:
            ans = ans and pointer_not_empty(child)
    if parallel_node or seq_node:
        ans = False
        for child in pointer.children:
            ans = ans or pointer_not_empty(child)
    if loop_node:
        ans = pointer_not_empty(pointer.children[0])
    return ans


def handle_parallel_node(pointers, pointer, child_index):
    pointers.remove(pointer)
    for index_of_child in range(len(pointer.children)):
        if child_index != index_of_child:
            pointers.append(pointer.children[index_of_child])
    pointers.append(pointer.children[child_index])


def handle_xor_node(pointers, pointer, child_index):
    pointers.remove(pointer)
    pointers.append(pointer.children[child_index])


def handle_seq_node(pointers, backup_pointers, backup_indexes, pointer, child_index):
    if pointers.__contains__(pointer):
        pointers.remove(pointer)
    if not backup_pointers.__contains__(pointer):
        if child_index + 1 != len(pointer.children):
            backup_pointers.append(pointer)
            backup_indexes.append(child_index + 1)
    else:
            pointer_index = backup_pointers.index(pointer)
            if child_index + 1 != len(pointer.children):
                backup_indexes[pointer_index] = child_index + 1
            else:
                backup_pointers.pop(pointer_index)
                backup_indexes.pop(pointer_index)
    pointers.append(pointer.children[child_index])


def handle_loop_node(pointers, backup_pointers, backup_indexes, pointer, child_index):
    if pointers.__contains__(pointer):
        pointers.remove(pointer)
    if not backup_pointers.__contains__(pointer):
        backup_pointers.append(pointer)
        backup_indexes.append(1 - child_index)
    else:
        pointer_index = backup_pointers.index(pointer)
        backup_indexes[pointer_index] = 1 - child_index
    pointers.append(pointer.children[child_index])


def add_to_transition_enables(pointers, transitions_enabled):
    for pointer in pointers:
        names_of_transitions_enable = []
        transitions_can_happen_in_pointer(pointer, names_of_transitions_enable)
        for name_of_transition in names_of_transitions_enable:
            if not transitions_enabled.__contains__(name_of_transition):
                transitions_enabled.append(name_of_transition)


def get_type_of_node(pointer):
    if pointer.operator.value == "X":
        return "xor"
    if pointer.operator.value == "->":
        return "seq"
    if pointer.operator.value == "*":
        return "loop"
    if pointer.operator.value == "+":
        return "parallel"


def delete_from_pointers(pointers, pointer):
    for pointer_in_list in pointers.copy():
        if is_son_of(pointer_in_list, pointer):
            pointers.remove(pointer_in_list)


def delete_from_backups(pointer, backup_pointers, backup_indexes):
    for index in range(len(backup_indexes) - 1, -1, -1):
        curr_backup_pointer = backup_pointers[index]
        if is_son_of(curr_backup_pointer, pointer):
            backup_pointers.pop(index)
            backup_indexes.pop(index)


def handle_seq_node_backup(backup_indexes, transition, transitions_enabled, pointer, pointer_index):
    child_index = find_child_index(pointer, transition)
    inedx_of_pointer_in_backup = backup_indexes[pointer_index]
    add_to_transition_enables(pointer.children[inedx_of_pointer_in_backup:child_index], transitions_enabled)


def handle_loop_node_backup(backup_indexes, transitions_enabled, pointer, pointer_index):
    inedx_of_pointer_in_backup = backup_indexes[pointer_index]
    if inedx_of_pointer_in_backup == 0:
        add_to_transition_enables(pointer.children[0:1], transitions_enabled)
    else:
        add_to_transition_enables(pointer.children[1:], transitions_enabled)


def fix_backup_pointers_and_pointers(pointers, backup_pointers, backup_indexes, transition, transitions_enabled,
                                     pointer):
    delete_from_pointers(pointers, pointer)
    delete_from_backups(pointer, backup_pointers, backup_indexes)
    type_of_node = get_type_of_node(pointer)
    pointer_index = find_pointer_index(backup_pointers, transition)
    if type_of_node == "seq":
        handle_seq_node_backup(backup_indexes, transition, transitions_enabled, pointer, pointer_index)
    if type_of_node == "loop":
        handle_loop_node_backup(backup_indexes, transitions_enabled, pointer, pointer_index)


def build_choices_of_train_log_3(pointers, backup_pointers, backup_indexes, transition, transitions_enabled):
    add_to_transition_enables(pointers, transitions_enabled)
    pointer_index = find_pointer_index(pointers, transition)
    if pointer_index != -1:
        pointer = pointers[pointer_index]
    else:
        pointer_index = find_pointer_index(backup_pointers, transition)
        pointer = backup_pointers[pointer_index]
        fix_backup_pointers_and_pointers(pointers, backup_pointers, backup_indexes, transition, transitions_enabled,pointer)
    if in_transition(pointer, transition):
        pointers.remove(pointer)
        return
    type_of_node = get_type_of_node(pointer)
    child_index = find_child_index(pointer, transition)
    if type_of_node == "seq":
        handle_seq_node(pointers, backup_pointers, backup_indexes, pointer, child_index)
    if type_of_node == "parallel":
        handle_parallel_node(pointers, pointer, child_index)
    if type_of_node == "xor":
        handle_xor_node(pointers, pointer, child_index)
    if type_of_node == "loop":
        handle_loop_node(pointers, backup_pointers, backup_indexes, pointer, child_index)
    build_choices_of_train_log_3(pointers, backup_pointers, backup_indexes, transition, transitions_enabled)




def build_list_of_xor_nodes_and_choses_2(process_tree, traces, xor_nodes, activities_enables_for_nodes, column):
    rows = []
    for trace in traces:
        pointers = [process_tree]
        list_backup_pointers = []
        list_of_backup_indexes = []
        for index in range(len(trace)):
            pref = trace[0:index + 1]
            row = build_row(pref[:-1], column)
            transitions_enabled = []
            transition = trace[index]
            build_choices_of_train_log_3(pointers, list_backup_pointers, list_of_backup_indexes,transition, transitions_enabled)
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
        chosen = row[len(row) - 1]
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




def print_guard_of_target(target_name, Phenotype, col_name_copy):
    print(target_name, " guard:")
    print(Phenotype)
    start_index = Phenotype.find("x")
    new_phenotype = ""
    curr_index = 0
    while start_index != -1:
        new_phenotype = new_phenotype + Phenotype[curr_index:start_index]
        first_index_of_close_bracket = Phenotype.index("]", start_index + 1)
        feature_index = int(Phenotype[start_index + 5:first_index_of_close_bracket])
        feature = col_name_copy[feature_index]
        new_phenotype = new_phenotype + feature
        start_index = Phenotype.find("x", first_index_of_close_bracket + 1)
        curr_index = first_index_of_close_bracket + 1
    new_phenotype = new_phenotype + Phenotype[curr_index:]
    print(new_phenotype)


def generate_bnf_file(number_of_transitions):
    with open("C:/Users/עידו שפירא/PycharmProjects/play/PonyGE2/grammars/supervised_learning/decision_tree.bnf",
              'w') as bnf_file:
        bnf_file.write('<b> ::= np.less(<e>,<e>)|\n')
        bnf_file.write('        np.greater(<e>,<e>)|\n')
        bnf_file.write('        np.logical_and(<b>,<b>)|\n')
        bnf_file.write('        np.logical_or(<b>,<b>)|\n')
        # bnf_file.write('        np.where(<b>,<e>,<e>)|\n')
        # bnf_file.write('        np.equal(<e>,<e>)\n\n')

        bnf_file.write('<e> ::= x[:, 0]|\n')
        for i in range(1, number_of_transitions):
            bnf_file.write(f'        x[:, {i}]|\n')

        bnf_file.write('        np.subtract(<e>,<e>)|\n')
        bnf_file.write('        np.add(<e>,<e>)|\n')
        bnf_file.write('        <c>\n\n')

        bnf_file.write('<c> ::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9\n')


def build_good_indexes(column, not_relevant_features_for_target):
    good_indexexs = []
    for index in range(len(column)):
        if not not_relevant_features_for_target.__contains__(column[index]):
            good_indexexs.append(index)
    return good_indexexs


def build_row_to_append(row, good_indexes):
    row_to_append = []
    for index in range(len(row)):
        if good_indexes.__contains__(index):
            row_to_append.append(row[index])
    return row_to_append


def build_rows_not_relevant(list_of_xor_nodes_and_choses, target_name, column, not_relevant_features_for_target):
    good_indexes = build_good_indexes(column, not_relevant_features_for_target)
    rows = []
    for row in list_of_xor_nodes_and_choses:
        transition_chosen = row[len(row) - 2]
        transitions_enabled = row[len(row) - 1]
        if transitions_enabled.__contains__(target_name):
            row_to_append = build_row_to_append(row, good_indexes)
            if target_name == transition_chosen:
                row_to_append.append(1)
            else:
                row_to_append.append(0)
            rows.append(row_to_append)
    clear_rows(rows)
    return rows


def build_unique_indexes(rows, len_of_row):
    indexes = []
    for i in range(len_of_row):
        bad_index = True
        value = rows[0][i]
        for row in rows:
            if row[i] != value:
                bad_index = False
        if bad_index:
            indexes.append(bad_index)
    return indexes


def build_bad_features(list_of_bad_indexes, column):
    bad_features = []
    for index in list_of_bad_indexes:
        bad_features.append(column[index])
    return bad_features


def fix_rows_unique(rows, list_of_bad_indexes):
    for index_of_row in range(len(rows)):
        row = rows[index_of_row]
        row_to_replace = []
        for index in range(len(row)):
            if not list_of_bad_indexes.__contains__(index):
                row_to_replace.append(row[index])
        rows[index_of_row] = row_to_replace


def remove_unique_columns(rows, column):
    list_of_bad_indexes = build_unique_indexes(rows, len(column) - 2)
    list_of_bad_features = build_bad_features(list_of_bad_indexes, column)
    fix_rows_unique(rows, list_of_bad_indexes)
    for bad_feature in list_of_bad_features:
        column.remove(bad_feature)


def add_xor_guards_ponyG(tree, net, train_log, col_name, initial_marking, final_marking, dicitionary_for_transitions):
    # copy_net = net.__deepcopy__()
    traces = build_traces_from_csv(train_log)
    nodes = []
    activities_enables_for_nodes = []
    build_xor_nodes(tree, nodes, activities_enables_for_nodes)
    list_of_xor_nodes_and_choses = build_list_of_xor_nodes_and_choses_2(tree, traces, nodes,
                                                                        activities_enables_for_nodes,
                                                                        col_name)
    columns = builds_all_target(col_name)
    for column in columns:
        target_name = column[len(column) - 1]
        not_relevant_features_for_target = dicitionary_for_transitions[target_name]
        rows = build_rows_not_relevant(list_of_xor_nodes_and_choses, target_name, column,
                                       not_relevant_features_for_target)
        for not_relevant_feature_for_target in not_relevant_features_for_target:
            column.remove(not_relevant_feature_for_target)
        # remove_unique_columns(rows,column)
        generate_bnf_file(len(column))
        # build_csv_for_prefixes(copy_net, train_log, column, initial_marking, final_marking)
        col_name_copy = column.copy()
        col_name_copy.append("choose")
        # build_rows_for_target(list_of_xor_nodes_and_choses, index_of_target)
        # rows = build_rows(list_of_xor_nodes_and_choses, target_name)
        build_csv_for_child_of_xor(rows, col_name_copy)
        command = 'ponyge.py'
        directory_path = 'C:/Users/עידו שפירא/PycharmProjects/play/PonyGE2/src'  # Replace with the actual path

        # Run the command in the specified directory
        result = subprocess.run(command, shell=True, cwd=directory_path, capture_output=True, text=True)
        fitness_str_copy = result.stdout
        phenotype_str_copy = result.stdout
        index_of_fitness = result.stdout.find("Fitness:")
        Fitness = fitness_str_copy[index_of_fitness + 10:]
        index_of_phenotype = phenotype_str_copy.find("Phenotype:")
        Phenotype = result.stdout[index_of_phenotype + 11:]
        index_of_end = Phenotype.find("\n")
        Phenotype = Phenotype[:index_of_end]
        if Fitness.startswith("0.0"):
            # stats = PonyGE2.src.ponyge.mane_2(list_argv)
            print_guard_of_target(target_name, Phenotype, col_name_copy)
            ApplyPonyGuard.apply_pony_guard(net, target_name, Phenotype, col_name_copy)



def import_csv(file_path):
    event_log = pd.read_csv(file_path, sep=';')
    event_log['case ID'] = event_log['case ID'].astype(str)
    event_log['activity'] = event_log['activity'].astype(str)
    event_log['timestamp'] = pd.to_datetime(event_log['timestamp'], format='mixed')
    return event_log




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
