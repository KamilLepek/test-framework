#
# Copyright(c) 2019 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause-Clear
#


class Output:
    def __init__(self, output_out, output_err, return_code):
        self.stdout = output_out.decode('utf-8').rstrip() if type(output_out) == bytes else \
            output_out
        self.stderr = output_err.decode('utf-8').rstrip() if type(output_err) == bytes else \
            output_err
        self.exit_code = return_code
