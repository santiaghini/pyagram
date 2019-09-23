import inspect
import types

import utils

TERMINAL_HEIGHT = 60
TERMINAL_WIDTH = 80

def separator(title=''):
    """
    <summary>

    :param title:
    :return:
    """
    title = f'{title.upper()} ' if title else ''
    return f'{title}{"-" * (TERMINAL_WIDTH - len(title))}'

def prepend(prefix, text):
    """
    <summary> # prepend prefix to every line in text

    :param text:
    :param prefix:
    :return:
    """
    return prefix + text.replace('\n', f'\n{prefix}')

def get_binding(max_key_len, max_value_len):
    """
    <summary>

    :param max_key_len:
    :param max_value_len:
    :return:
    """
    return lambda key, value: f'|{key:>{max_key_len}}: {value_repr(value):<{max_value_len}}|'

def value_repr(object):
    """
    <summary>

    :param object:
    :return:
    """
    return f'*{id(object)}' if utils.is_referent_type(object) else repr(object)

def value_str(object, function_parents):
    """
    <summary>

    :param object:
    :return:
    """
    if isinstance(object, types.FunctionType):
        name = object.__name__
        args = ', '.join(
            name if param.default is inspect.Parameter.empty else f'{name}={value_repr(param.default)}'
            for name, param in inspect.signature(object).parameters.items()
        )
        parent = function_parents[object]
        return f'function {name}({args}) [p={repr(parent)}]'
    else:
        return repr(object)
