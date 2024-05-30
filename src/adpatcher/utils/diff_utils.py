from adpatcher.utils.stdout_utils import diff_output
from adpatcher.utils.process_utils import call_process

def call_diff(file1: str, file2: str, verbose: bool=False) -> None:
    diff_out, diff_err = call_process('diff', [
        '-a',
        #'-y',
        #'--left-column',
        '--suppress-common-lines',
        '-B', '-Z',
        file1,
        file2
    ])
    print(diff_out) # TODO da inserire qualche altra roba