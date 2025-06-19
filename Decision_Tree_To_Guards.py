import csv
import subprocess
import ApplyPonyGuard
import LogSplit


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
def add_to_transition_enables_non_leaves(pointers, transitions_enabled):
    for pointer in pointers:
        name_of_pointer = pointer.label
        if name_of_pointer!= None and not transitions_enabled.__contains__(name_of_pointer):
            transitions_enabled.append(name_of_pointer)

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


def is_subtree_of(pointer, backup_pointer):
    if pointer == None:
        return False
    if pointer == backup_pointer:
        return True
    return is_subtree_of(pointer.parent, backup_pointer)


def add_loops_open(pointers, backup_pointers, backup_indexes, transitions_enabled):
    for i in range(len(backup_pointers)):
        backup_pointer = backup_pointers[i]
        backup_index = backup_indexes[i]
        if backup_pointer.operator.value == "*":
            contain_son_without_empty = False
            for pointer in pointers:
                contain_son_without_empty = contain_son_without_empty or (is_subtree_of(pointer,backup_pointer) and node_without_empty(pointer))
            if contain_son_without_empty == False:
                if backup_index == 0:
                    children = backup_pointer.children[0]
                    if has_empty_child(children):
                        add_to_transition_enables([backup_pointer], transitions_enabled)
                    else:
                        add_to_transition_enables([children], transitions_enabled)
                else:
                    right_side_has_empty = False
                    for child in backup_pointer.children[1:]:
                        right_side_has_empty = right_side_has_empty or has_empty_child(child)
                    if right_side_has_empty:
                        add_to_transition_enables([backup_pointer], transitions_enabled)
                    else:
                        for child in backup_pointer.children[1:]:
                            add_to_transition_enables([child], transitions_enabled)
def build_choices_of_train_log_3(pointers, backup_pointers, backup_indexes, transition, transitions_enabled, start):
    add_to_transition_enables(pointers, transitions_enabled)
    if start:
       add_loops_open(pointers,backup_pointers,backup_indexes,transitions_enabled)
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
    build_choices_of_train_log_3(pointers, backup_pointers, backup_indexes, transition, transitions_enabled, False)


def build_choices_of_train_log_with_non_leaves(pointers, backup_pointers, backup_indexes, transition, transitions_enabled):
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
            build_choices_of_train_log_3(pointers, list_backup_pointers, list_of_backup_indexes,transition, transitions_enabled, True)
            row_copy = row.copy()
            row_copy.append(trace[index])
            row_copy.append(transitions_enabled)
            if not rows.__contains__(row_copy):
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
        bnf_file.write('        np.equal(<e>,<e>)\n\n')

        bnf_file.write('<e> ::= x[:, 0]|\n')
        for i in range(1, number_of_transitions):
            bnf_file.write(f'        x[:, {i}]|\n')

        bnf_file.write('        np.subtract(<e>,<e>)|\n')
        bnf_file.write('        np.add(<e>,<e>)|\n')
        bnf_file.write('        <c>\n\n')

        bnf_file.write('<c> ::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12\n')


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

def de_morgan(string_guard):
    string_guard = string_guard[7:]
    first_index_of_open_bracket = string_guard.index("(")
    func_of_guard = string_guard[3:first_index_of_open_bracket]
    string_guard = string_guard[first_index_of_open_bracket:]
    left_right_string = ApplyPonyGuard.left_right(string_guard)
    left = left_right_string[0]
    right = left_right_string[1]
    if func_of_guard == "greater":
        string_guard = "np.less(" + left + "," + right + ")"
    if func_of_guard == "less":
        string_guard = "np.greater(" + left + "," + right + ")"
    if func_of_guard == "equal":
        left_bigger_string = "np.greater(" + left + "," + right + ")"
        right_bigger_string = "np.greater(" + right + "," + left + ")"
        string_guard = "np.logical_or(" + left_bigger_string + "," + right_bigger_string + ")"
    if func_of_guard == "logical_and":
        not_left_string = "np.not(" + left + ")"
        not_right_string = "np.not(" + right + ")"
        string_guard = "np.logical_or(" + not_left_string + "," + not_right_string + ")"
    if func_of_guard == "logical_or":
        not_left_string = "np.not(" + left + ")"
        not_right_string = "np.not(" + right + ")"
        string_guard = "np.logical_and(" + not_left_string + "," + not_right_string + ")"
    if func_of_guard == "not":
        string_guard = string_guard[7:len(string_guard) - 1]
    return string_guard

def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
def value_of(string_guard, row, columns):
    if string_guard.startswith("np"):
        first_index_of_open_bracket = string_guard.index("(")
        func_of_guard = string_guard[3:first_index_of_open_bracket]
        string_guard = string_guard[first_index_of_open_bracket:]
        left_right_string = ApplyPonyGuard.left_right(string_guard)
        left = left_right_string[0]
        right = left_right_string[1]
        if func_of_guard == "subtract":
            return value_of(left, row, columns) - value_of(right, row, columns)
        else:
            return value_of(left, row, columns) + value_of(right, row, columns)
    elif is_integer(string_guard):
        return int(string_guard)
    else:
        return row[columns.index(string_guard)]
def check_guards_on_row(row, string_guard, columns):
    if string_guard.startswith("np.not"):
        return check_guards_on_row(row, de_morgan(string_guard), columns)
    else:
        first_index_of_open_bracket = string_guard.index("(")
        func_of_guard = string_guard[3:first_index_of_open_bracket]
        string_guard = string_guard[first_index_of_open_bracket:]
        left_right_string = ApplyPonyGuard.left_right(string_guard)
        left = left_right_string[0]
        right = left_right_string[1]
        if func_of_guard == "greater":
            return value_of(left, row, columns) > value_of(right, row, columns)
        elif func_of_guard == "less":
            return value_of(left, row, columns) < value_of(right, row, columns)
        elif func_of_guard == "equal":
            return  value_of(left, row, columns) == value_of(right, row, columns)
        elif func_of_guard == "logical_and":
            return check_guards_on_row(row, left, columns) and  check_guards_on_row(row, right, columns)
        else:
            return check_guards_on_row(row, left, columns) or check_guards_on_row(row, right, columns)


def apply_guard(rows, string_guard, col_name_copy):
    if not string_guard.startswith("np"):
        return False
    for row in rows:
        if not check_guards_on_row(row, string_guard, col_name_copy) and row[-1] == 1:
            return False
    return True

def guard_translated(Phenotype, col_name_copy):
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
    return new_phenotype


def add_xor_guards_ponyG(tree, net, train_log, col_name, dicitionary_for_transitions):
    traces = LogSplit.build_traces_from_csv(train_log)
    nodes = []
    activities_enables_for_nodes = []
    build_xor_nodes(tree, nodes, activities_enables_for_nodes)
    list_of_xor_nodes_and_choses = build_list_of_xor_nodes_and_choses_2(tree, traces, nodes,
                                                                        activities_enables_for_nodes,
                                                                        col_name)
    # columns = builds_all_target(col_name)
    for index in range(len(col_name)):
        target_name = col_name[index]
        not_relevant_features_for_target = dicitionary_for_transitions[target_name]
        rows = build_rows_not_relevant(list_of_xor_nodes_and_choses, target_name, col_name,
                                       not_relevant_features_for_target)
        col_name_copy = col_name.copy()
        for not_relevant_feature_for_target in not_relevant_features_for_target:
            col_name_copy.remove(not_relevant_feature_for_target)
        # remove_unique_columns(rows,column)
        generate_bnf_file(len(col_name_copy))
        col_name_copy.append("choose")
        # build_rows_for_target(list_of_xor_nodes_and_choses, index_of_target)
        # rows = build_rows(list_of_xor_nodes_and_choses, target_name)
        build_csv_for_child_of_xor(rows, col_name_copy)
        command = ['python', 'ponyge.py']
        directory_path = 'C:/Users/עידו שפירא/PycharmProjects/play/PonyGE2/src'
        result = subprocess.run(
            command,
            cwd=directory_path,
            capture_output=True,
            text=True,
            encoding='utf-8' 
        )
        fitness_str_copy = result.stdout
        phenotype_str_copy = result.stdout
        index_of_fitness = result.stdout.find("Fitness:")
        Fitness = fitness_str_copy[index_of_fitness + 10:]
        index_of_phenotype = phenotype_str_copy.find("Phenotype:")
        Phenotype = result.stdout[index_of_phenotype + 11:]
        index_of_end = Phenotype.find("\n")
        Phenotype = Phenotype[:index_of_end]
        # print_guard_of_target(target_name, Phenotype, col_name_copy)
        apply = apply_guard(rows, guard_translated(Phenotype, col_name_copy), col_name_copy)
        if apply:
            print_guard_of_target(target_name, Phenotype, col_name_copy)
            ApplyPonyGuard.apply_pony_guard(net, target_name, Phenotype, col_name_copy)



