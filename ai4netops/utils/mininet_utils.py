import logging
from functools import wraps
from io import StringIO


# Rewrite the orignal functions in Mininet
def dumpNodeConnections(nodes):
    "Dump connections to/from nodes."

    def dumpConnections(node):
        "Helper function: dump connections to node"
        node_conn_dict = {}
        for intf in node.intfList():
            if intf.link:
                intfs = [intf.link.intf1, intf.link.intf2]
                intfs.remove(intf)
                node_conn_dict[intf.name] = intfs[0].name
            else:
                node_conn_dict[intf.name] = ""
        return node_conn_dict

    nodes_conn_dict = {}
    for node in nodes:
        nodes_conn_dict[node.name] = dumpConnections(node)
    return nodes_conn_dict


def dumpNetConnections(net):
    "Dump connections in network"
    nodes = net.controllers + net.switches + net.hosts
    net_conn_dict = dumpNodeConnections(nodes)
    return net_conn_dict


# Not used for now
def capture_output(logger, level=25):
    """
    Decorator to capture logger output from a function.

    Parameters:
    - logger: the logger instance to capture from (e.g., `lg`)
    - level: the log level to capture (default 25 for Mininet's output level)

    Returns:
    - Decorated function that returns a tuple: (result, captured_output)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log_stream = StringIO()
            handler = logging.StreamHandler(log_stream)
            handler.setFormatter(logging.Formatter("%(message)s"))
            handler.setLevel(level)

            logger.addHandler(handler)
            try:
                result = func(*args, **kwargs)
            finally:
                logger.removeHandler(handler)

            captured_output = log_stream.getvalue().strip()
            return result, captured_output

        return wrapper

    return decorator


# @capture_output()
# def dumpNetConnections_with_return(net):
#     dumpNetConnections(net)
