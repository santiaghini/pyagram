import bdb
import io
import sys

from . import enums
from . import state
from . import user_exception
from . import utils

class Tracer(bdb.Bdb):
    """
    <summary>
    """

    def __init__(self, encoder):
        super().__init__()
        self.encoder = encoder
        self.state = None
        self.old_stdout = sys.stdout
        self.new_stdout = io.StringIO()
        sys.stdout = self.new_stdout

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
        # TODO: Your code relies on a program that works; therefore if the code doesn't work, your code will throw some error that is different from the one thrown by the input code. If there's an error, perhaps run the student's code plain-out and scrape its error message?
        self.snapshot(enums.TraceTypes.USER_EXCEPTION)
        raise user_exception.UserException(*exception_info)

    def stop(self):
        sys.stdout = self.old_stdout

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
            self.state = state.State(frame, self.encoder, self.new_stdout)
        self.state.step(frame, is_frame_open, is_frame_close, return_value)

    def snapshot(self, trace_type):
        """
        <summary>

        :return:
        """
        if self.state.program_state.curr_element is None:
            take_snapshot = False
        elif trace_type is enums.TraceTypes.USER_CALL:
            take_snapshot = False
        elif trace_type is enums.TraceTypes.USER_LINE:
            take_snapshot = self.state.program_state.curr_line_no != utils.OUTER_CALL_LINENO \
                        and self.state.program_state.curr_line_no != utils.INNER_CALL_LINENO
        elif trace_type is enums.TraceTypes.USER_RETURN:
            take_snapshot = self.state.program_state.curr_line_no == utils.OUTER_CALL_LINENO \
                         or self.state.program_state.curr_line_no == utils.INNER_CALL_LINENO
        elif trace_type is enums.TraceTypes.USER_EXCEPTION:
            take_snapshot = False
        else:
            raise enums.TraceTypes.illegal_trace_type(trace_type)
        if take_snapshot:
            self.state.snapshot()
