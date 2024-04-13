import xml.etree.ElementTree as ET


class Transition:
    def __init__(self, input_symbol, from_state, to_state):
        self.input_symbol = input_symbol
        self.from_state = from_state
        self.to_state = to_state

class Automaton:
    def __init__(self):
        self.states = {}
        self.transitions = []
        self.initial_state = None
        self.final_states = set()

    def input_alphabet(self):
        return {transition.input_symbol for transition in self.transitions if transition.input_symbol != '#'}

def parse_xml(xml_string):
    automaton = Automaton()
    root = ET.fromstring(xml_string)

    # Parse das transições
    for trans_elem in root.findall('.//fsa_trans'):
        input_elem = trans_elem.find('input')
        input_symbol = input_elem.text.strip() if input_elem is not None and input_elem.text is not None else '#'
        from_state = trans_elem.find('from/id').text.strip() if trans_elem.find('from/id') is not None else ''
        to_state = trans_elem.find('to/id').text.strip() if trans_elem.find('to/id') is not None else ''
        transition = Transition(input_symbol, from_state, to_state)
        automaton.transitions.append(transition)

    # Parse dos estados
    for state_elem in root.findall('.//state'):
        state_id = state_elem.find('id').text.strip() if state_elem.find('id') is not None else ''
        state_name = state_elem.find('name').text.strip() if state_elem.find('name') is not None else ''
        automaton.states[state_id] = state_name

    # Parse dos estados iniciais
    initial_state_elem = root.find('.//structure[@type="start_state"]/state/id')
    automaton.initial_state = initial_state_elem.text.strip() if initial_state_elem is not None else ''

    # Parse dos estados finais
    final_state_elems = root.findall('.//structure[@type="final_states"]/state/id')
    automaton.final_states = {state_elem.text.strip() for state_elem in final_state_elems}

    return automaton


def parse_txt(txt_data):
    automaton = Automaton()

    # Separa as linhas do texto
    lines = txt_data.split('\n')

    # Parse do estado inicial
    initial_state_line = lines[0].split(': ')[1]
    automaton.initial_state = initial_state_line.strip()

    # Parse dos estados finais
    final_states_line = lines[1].split(': ')[1]
    final_states = final_states_line.strip()[1:-1].split(', ')
    automaton.final_states = set(final_states)

    # Parse das transições
    for line in lines[2:]:
        if line:
            parts = line.split()
            from_state = parts[2]
            to_state = parts[4]
            input_symbol = parts[6]
            transition = Transition(input_symbol, from_state, to_state)
            automaton.transitions.append(transition)

    return automaton


def load_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None


def convert_afnd_to_afd(afnd_automaton):
    afd_automaton = Automaton()
    epsilon_closures = {}

    for state_id in afnd_automaton.states:
        epsilon_closures[state_id] = calculate_epsilon_closure(afnd_automaton, state_id)

    initial_state = ','.join(sorted(epsilon_closures[afnd_automaton.initial_state]))
    afd_automaton.initial_state = initial_state
    afd_automaton.states[initial_state] = initial_state

    unprocessed_states = [initial_state]

    while unprocessed_states:
        current_afd_state = unprocessed_states.pop(0)
        current_afd_state_set = set(current_afd_state.split(','))

        for input_symbol in afnd_automaton.input_alphabet():
            reachable_states = set()

            for afnd_state_id in current_afd_state_set:
                for transition in afnd_automaton.transitions:
                    if (transition.from_state == afnd_state_id and
                            transition.input_symbol == input_symbol):
                        reachable_states |= epsilon_closures[transition.to_state]

            if reachable_states:
                new_afd_state_name = ','.join(sorted(reachable_states))

                if new_afd_state_name not in afd_automaton.states:
                    afd_automaton.states[new_afd_state_name] = new_afd_state_name
                    unprocessed_states.append(new_afd_state_name)

                afd_automaton.transitions.append(Transition(input_symbol, current_afd_state, new_afd_state_name))

                for final_state in afnd_automaton.final_states:
                    if final_state in reachable_states:
                        afd_automaton.final_states.add(new_afd_state_name)

    return afd_automaton


def save_afd(afd, filename):
    with open(filename, 'w') as file:
        file.write(f"Initial state: {afd.initial_state}\n")
        file.write(f"Final states: {afd.final_states}\n")
        file.write("\nStates:\n")
        for state_id, state_name in afd.states.items():
            # Transforma os números do state_id em uma string e remove os parênteses
            state_num = ''.join([str(num) for num in state_id if num.isdigit()])
            state_name = f"q{state_num}"  # Adiciona 'q' ao início da string de números do state_id
            file.write(f"State {state_id}: {state_name}\n")
        file.write("\nTransitions:\n")
        for transition in afd.transitions:
            file.write(f"From state {transition.from_state} to state {transition.to_state} with input {transition.input_symbol}\n")



def calculate_epsilon_closure(automaton, state_id):
    epsilon_closure = set()

    def epsilon_closure_helper(state_id):
        epsilon_closure.add(state_id)
        for transition in automaton.transitions:
            if (transition.from_state == state_id and
                    transition.input_symbol == '#'):
                if transition.to_state not in epsilon_closure:
                    epsilon_closure_helper(transition.to_state)

    epsilon_closure_helper(state_id)
    return epsilon_closure


def check_words(afd, words_filename, output_filename):
    recognized_words = set()

    # Carregar palavras do arquivo
    try:
        with open(words_filename, 'r') as file:
            words = file.read().splitlines()
    except FileNotFoundError:
        print(f"Error: File '{words_filename}' not found.")
        return

    # Verificar se as palavras são reconhecidas pelo AFD
    for word in words:
        current_state = afd.initial_state
        accepted = True
        for letter in word:
            found_transition = False
            for transition in afd.transitions:
                if transition.from_state == current_state and transition.input_symbol == letter:
                    current_state = transition.to_state
                    found_transition = True
                    break
            if not found_transition:
                accepted = False
                break
        if accepted and current_state in afd.final_states:
            recognized_words.add(word)

    # Escrever resultados no arquivo de saída
    with open(output_filename, 'w') as file:
        for word in words:
            if word in recognized_words:
                file.write(f"{word}: aceito\n")
            else:
                file.write(f"{word}: não aceito\n")


def main():
    filename = 'entrada.jflap'
    xml_data = load_file(filename)

    if xml_data:
        print("File loaded successfully.")
        automaton = parse_xml(xml_data)

        print(f"\nInitial state: {automaton.initial_state}")
        print(f"Final states: {automaton.final_states}\n")
        print("States:")
        for state_id, state_name in automaton.states.items():
            print(f"State {state_id}: {state_name}")

        print("\nTransitions:")
        for transition in automaton.transitions:
            print(f"From state {transition.from_state} to state {transition.to_state} with input {transition.input_symbol}")

        afd = convert_afnd_to_afd(automaton)

        print("\nAFD:")
        print(f"Initial state: {afd.initial_state}")
        print(f"Final states: {afd.final_states}")
        for transition in afd.transitions:
            print(f"From state {transition.from_state} to state {transition.to_state} with input {transition.input_symbol}")

        save_afd(afd, 'saida.txt')

        check_words(afd, 'palavras.txt', 'saida_palavras.txt')


if __name__ == '__main__':
    main()