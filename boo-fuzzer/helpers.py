from boofuzz import Request, Bytes, Checksum, Session, Size, Block


def pj_checksum(data):
    """
    Calculate the checksum of the given data
    :param data:
    :return:
    """
    return bytes([sum(data) % 256])


def init_request_payload_for_handler(session: Session):
    """
    Initialize a request object with the given/known handlers and fuzz the payload and put it into the fuzzing queue.
    :param session:
    :return:
    """
    handler0 = Bytes('handler', b'\x00', max_len=1, fuzzable=False)
    handler1 = Bytes('handler', b'\x01', max_len=1, fuzzable=False)
    handler2 = Bytes('handler', b'\x02', max_len=1, fuzzable=False)
    handler3 = Bytes('handler', b'\x03', max_len=1, fuzzable=False)
    unknown = Bytes('unknown', b'\x00', max_len=1, fuzzable=False)
    padding = Bytes('padding', b'\x00\x00', max_len=2, fuzzable=False)
    length = Bytes('length', b'\x00', max_len=1, fuzzable=True)
    checksum = init_request_payload_with_checksum(length)
    payload = Bytes('payload', b'\x00', fuzzable=True)
    command0 = Block('command0', children=(handler0, unknown, padding, length, payload))
    command1 = Block('command1', children=(handler1, unknown, padding, length, payload))
    command2 = Block('command2', children=(handler2, unknown, padding, length, payload))
    command3 = Block('command3', children=(handler3, unknown, padding, length, payload))
    request0 = Request(name='specific', children=(command0, checksum))
    request1 = Request(name='specific', children=(command1, checksum))
    request2 = Request(name='specific', children=(command2, checksum))
    request3 = Request(name='specific', children=(command3, checksum))
    session.connect(request0)
    session.connect(request1)
    session.connect(request2)
    session.connect(request3)


def init_request_payload_with_checksum(length: Bytes):
    length_val = int.from_bytes(length.get_value(), 'big')
    Size('payload_size', block_name='payload', length=length_val)
    checksum = Checksum('checksum', block_name='checksum', algorithm=pj_checksum, length=1)
    return checksum


def init_request(session, func_name: str, module):
    """
    Initialize a request object with the given function name and put them into the fuzzing queue.
    :param module:
    :param session:
    :param func_name:
    :return:
    """
    function = getattr(module.Documented, func_name)
    # Call the function and get the result
    result = function()
    # Get the bytes from the result that can and should be fuzzed
    fuzzable_bytes = bytes(result[:-1])
    # Create a Bytes object that implements Fuzzable
    byte_obj = Bytes(func_name, fuzzable_bytes)
    # Create a Static object that are constant through calculation of the given command.
    checksum_obj = Checksum('checksum', block_name=func_name, algorithm=pj_checksum,
                            fuzzable=False)
    # Create a Request object with the Byte object as a child
    request = Request(name=func_name, children=(byte_obj, checksum_obj))
    # Connect the request to the session as a graph like object
    session.connect(request)


def init_requests(session, func_name: str, module):
    """
    Initialize a request object with the given function name and put them into the fuzzing queue.
    :param session:
    :param func_name:
    :param module:
    :return:
    """
    init_request(session, func_name, module)
    init_request_structure(session)
    init_request_payload_for_handler(session)


def iterate_over_functions(session, module):
    """
    Iterate over all functions in the Documented class and initialize request objects for the fuzzing queue.
    :return:
    """
    for func_name in dir(module.Documented):
        if callable(getattr(module.Documented, func_name)) and not func_name.startswith("__"):
            init_requests(session, func_name, module)


def init_request_structure(session: Session):
    """
    Initialize a request object with the given command structure and put it into the fuzzing queue.
    :param session:
    :return:
    """
    handler = Bytes('handler', b'\x00', max_len=1)
    unknown = Bytes('unknown', b'\x00', max_len=1)
    padding = Bytes('padding', b'\x00\x00', max_len=2)
    length = Bytes('length', b'\x00', max_len=1)
    payload = Bytes('payload', b'\x00')
    checksum = init_request_payload_with_checksum(length)
    request = Request(name='specific', children=(handler, unknown, padding, length, payload, checksum))
    session.connect(request)
