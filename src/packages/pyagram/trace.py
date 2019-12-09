import bdb

from . import display
from . import enums
from . import state
from . import utils

class Tracer(bdb.Bdb):
    """
    <summary>
    """

    def __init__(self, debug):
        super().__init__()
        self.debug = debug
        self.state = None

    def user_call(self, frame, args):
        """
        <summary>

        :param frame: the frame that gets opened
        :param args: the arguments to the function call (pretty sure this is deprecated tho)
        :return:
        """
        self.step(frame, is_frame_open=True)
        self.snapshot(enums.TraceTypes.USER_CALL)

    def user_line(self, frame):
        """
        <summary>

        :param frame:
        :return:
        """
        self.step(frame)
        self.snapshot(enums.TraceTypes.USER_LINE)

    def user_return(self, frame, return_value):
        """
        <summary>

        :param frame:
        :param return_value:
        :return:
        """
        self.step(frame, is_frame_close=True, return_value=return_value)
        self.snapshot(enums.TraceTypes.USER_RETURN)

    def user_exception(self, frame, exception_info):
        """
        <summary>

        :param frame:
        :param exception_info:
        :return:
        """
        # TODO: Figure out how you want to address exceptions.
        # TODO: If there is an error, then don't do any of the flag banner nonsense.
        self.step(frame)
        self.snapshot(enums.TraceTypes.USER_EXCEPTION)

    def step(self, frame, *, is_frame_open=False, is_frame_close=False, return_value=None):
        """
        <summary>

        :param frame:
        :param is_frame_open:
        :param is_frame_close:
        :param return_value:
        :return:
        """
        if self.state is None:
            self.state = state.State(frame)
        self.state.step(frame, is_frame_open, is_frame_close, return_value)

    def snapshot(self, trace_type):
        """
        <summary>

        :return:
        """
        if trace_type is enums.TraceTypes.USER_CALL:
            take_snapshot = False
        elif trace_type is enums.TraceTypes.USER_LINE:
            take_snapshot = self.state.program_state.curr_line_no != utils.OUTER_CALL_LINENO \
                        and self.state.program_state.curr_line_no != utils.INNER_CALL_LINENO
        elif trace_type is enums.TraceTypes.USER_RETURN:
            take_snapshot = self.state.program_state.curr_line_no != utils.OUTER_CALL_LINENO
        elif trace_type is enums.TraceTypes.USER_EXCEPTION:
            take_snapshot = self.state.program_state.curr_line_no != utils.OUTER_CALL_LINENO
        else:
            raise enums.TraceTypes.illegal_trace_type(trace_type)

        # TODO: This isn't quite right ...

        if take_snapshot:
            if self.debug:
                self.display()
            self.state.snapshot()

    def display(self):
        """
        <summary>

        :return:
        """
        state_str = str(self.state)
        state_str_height = state_str.count('\n') + 1
        padding = display.TERMINAL_HEIGHT - (state_str_height + 1)
        print(state_str)
        if padding > 0:
            print('\n' * (padding - 1))
        input()
