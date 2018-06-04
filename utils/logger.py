from datetime import datetime
import os
import json
from utils import IO


class Logger:

    @staticmethod
    def time_now():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def check_for_folder():
        """Check for logs folder and create it if it doesn't exist"""
        logs_f = "logs"

        if os.path.isdir(logs_f):
            return True
        else:
            os.makedirs(logs_f)
            if os.path.isdir(logs_f):
                return True
            return False

    @staticmethod
    def get_filename():
        data = IO.read_settings_as_json()
        if data is None:
            return None

        r_time = data['last-login-time']
        time = str(r_time).split(".")[0].replace(":", "-")

        file_name = "Log {}.txt".format(time)

        if not os.path.exists(os.path.join("logs", file_name)):
            with open(os.path.join("logs", file_name), "w") as f:
                f.write("Log start")

        return file_name

    @staticmethod
    def write(to_write):
        # TODO 
        if Logger.check_for_folder() is False:
            return False

        file = Logger.get_filename()
        if file is None:
            return "Failed to write error log, File is None"

        if isinstance(to_write, str):
            print("to write is a string")

        elif isinstance(to_write, Exception):
            print("to write is an exception")
            ex_type = type(to_write).__name__
            args = to_write.args

            err_line = to_write.__traceback__.tb_lineno
            err_file = to_write.__traceback__.tb_frame.f_code.co_filename

            cause = to_write.__traceback__.tb_frame.f_trace

            print(args, err_file, err_line)

        else:
            print("to write is something else")











