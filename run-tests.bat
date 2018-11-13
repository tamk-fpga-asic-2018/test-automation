@echo off
for /f %%g in ('dir /b firmware') do (
    python test_cases.py firmware/%%g 2>&1 | tee results_%%~ng.txt
)