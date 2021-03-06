# -*- coding: utf-8 -*-

# Copyright 2018 IBM.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

import argparse
import json
import pprint
from qiskit.aqua import QiskitAqua
from qiskit.chemistry import QiskitChemistryError
import logging

logger = logging.getLogger(__name__)


def run_algorithm_from_json(params, output_file):
    """
    Runs the Aqua Chemistry experiment from Qiskit Aqua json dictionary

    Args:
        params (dictionary): Qiskit Aqua json dictionary
        output_file (filename): Output file name to save results
    """
    qiskit_aqua = QiskitAqua(params)
    ret = qiskit_aqua.run()
    if not isinstance(ret, dict):
        raise QiskitChemistryError('Algorithm run result should be a dictionary {}'.format(ret))

    print('Output:')
    pprint(ret, indent=4)
    if output_file is not None:
        with open(output_file, 'w') as out:
            pprint(ret, stream=out, indent=4)


def main():
    from qiskit.chemistry import run_experiment, run_driver_to_json
    from qiskit.chemistry._logging import get_logging_level, build_logging_config, set_logging_config
    from qiskit.chemistry.preferences import Preferences
    parser = argparse.ArgumentParser(description='Qiskit Chemistry Command Line Tool')
    parser.add_argument('input',
                        metavar='input',
                        help='Qiskit Chemistry input file or saved JSON input file')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-o',
                       metavar='output',
                       help='Algorithm Results Output file name')
    group.add_argument('-jo',
                       metavar='json output',
                       help='Algorithm JSON Output file name')

    args = parser.parse_args()

    # update logging setting with latest external packages
    preferences = Preferences()
    logging_level = logging.INFO
    if preferences.get_logging_config() is not None:
        set_logging_config(preferences.get_logging_config())
        logging_level = get_logging_level()

    preferences.set_logging_config(build_logging_config(logging_level))
    preferences.save()

    set_logging_config(preferences.get_logging_config())

    # check to see if input is json file
    params = None
    try:
        with open(args.input) as json_file:
            params = json.load(json_file)
    except:
        pass

    if params is not None:
        run_algorithm_from_json(params, args.o)
    else:
        if args.jo is not None:
            run_driver_to_json(args.input, args.jo)
        else:
            result = run_experiment(args.input, args.o)
            if result is not None and 'printable' in result:
                print('\n\n--------------------------------- R E S U L T ------------------------------------\n')
                for line in result['printable']:
                    print(line)
