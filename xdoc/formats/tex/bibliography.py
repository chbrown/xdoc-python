from StringIO import StringIO
from xdoc.dom import Reference


def feed(input_alphabet, current_state, state_transition_function):
    '''Stateful transducer orchestrator with transition function, which
    defaults to a simple pass-through, appending non-transitional symbols to
    the current buffer, which is emitted when the next state begins'''
    state_buffer = StringIO()
    for symbol in input_alphabet:
        next_state, symbol = state_transition_function(current_state, symbol)
        # could do this pretty elegantly with an itertools.groupby, but this is easier for now
        # could be pretty easily functionalized with a foldl or something
        if current_state != next_state:
            # emit the current state
            yield current_state, state_buffer.getvalue()
            # move to the new state and put a blank new buffer on the stack
            current_state = next_state
            state_buffer = StringIO()
        state_buffer.write(symbol)
    else:
        yield current_state, state_buffer.getvalue()


def bibtex_transitions(state, symbol):
    '''
    NONE :: '@' -> MEDIUM
    MEDIUM :: '{' -> KEY
    KEY :: ',' -> INSIDE
    INSIDE :: ',' -> FIELD...

    (string representation of transition funciton in progress)
    '''
    # if anything is returned, it is the name of the new state
    if state == 'none':
        if symbol == '@':
            return 'medium', ''
    elif state == 'medium':
        if symbol == '{':
            return 'key', ''
    elif state == 'key':
        if symbol == ',':
            return 'inside', ''
    elif state == 'inside':
        if symbol.isalpha():
            return 'field', symbol
        elif symbol == '}':
            return 'none', ''
    elif state == 'field':
        if not symbol.isalpha():
            return 'eq', ''
    elif state == 'eq':
        if symbol == '{' or symbol == '"':
            # TODO: return value-{ or value-" depending on the actual trigger symbol
            return 'value', ''
    elif state == 'value':
        # TODO: be less flexible
        if symbol == '}' or symbol == '"':
            return 'inside', ''
    return state, symbol


def parse_bibtex(bibtex_string):
    '''
    yields Reference() objects
    '''
    print 'reading...'
    parser = feed(bibtex_string, 'none', bibtex_transitions)
    for state, token in parser:
        # stack/collapse specific fsm states
        if state == 'medium':
            medium_token = token
            for state, token in parser:
                if state == 'key':
                    reference = Reference(token, medium_token)
                elif state == 'field':
                    field_token = token
                    for state, token in parser:
                        if state == 'value':
                            reference.attrs[field_token] = token
                            break
                elif state == 'none':
                    yield reference
                    break
