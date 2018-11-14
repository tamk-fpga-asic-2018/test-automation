#!/bin/bash

python3 test_cases.py firmware/tamk_1.bin | tee log1.txt
python3 test_cases.py firmware/tamk_2.bin | tee log2.txt
python3 test_cases.py firmware/tamk_3.bin | tee log3.txt
python3 test_cases.py firmware/tamk_4.bin | tee log4.txt