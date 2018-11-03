#!/bin/bash

python3 test_cases.py firmware/tamk_1.bin | tee test1_print.txt
python3 test_cases.py firmware/tamk_2.bin | tee test2_print.txt
python3 test_cases.py firmware/tamk_3.bin | tee test3_print.txt
python3 test_cases.py firmware/tamk_4.bin | tee test5_print.txt