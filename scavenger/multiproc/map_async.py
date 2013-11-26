__author__ = 'marco'

import subprocess
import shlex

import multiprocessing

from scavenger.func_utilities.funcmore import grouper


def spawned_process_cmd(cmd_str):
    """Write command to pass to subprocess."""
    cmd_line = cmd_str or 'echo \'Cannot Run this one\''
    return cmd_line


def f_wrapper(cmd):
    """Wraps subprocess with pid."""
    process_echo = subprocess.call(
        shlex.split(cmd),
        stdout=subprocess.STDOUT,
        stderr=subprocess.STDOUT)
    retcode = process_echo.wait()

    return retcode


def log_result(result_list):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    for result in result_list:
        retcode = result[0]

        print retcode


def run_multi():
    count = multiprocessing.cpu_count()

    # Mockup a list of commands
    list_dir = [
        'echo \'toto\'',
        'echo \'tata\'',
        'echo \'titi\'',
        'echo \'tutu\'',

    ]
    spawned_list = grouper(list_dir, count)

    pool = multiprocessing.Pool(processes=count)
    for group_spawned in spawned_list:
        computation_cycle = [spawned_process_cmd(command) for command in
                             group_spawned]
        r = pool.map_async(f_wrapper, computation_cycle, callback=log_result)
        r.wait()
    pool.close()