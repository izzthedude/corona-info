#!/bin/bash

printf "Creating a virtual environment... "
python -m venv venv || python3 -m venv venv
printf "Virtual environment created.\n"

printf  "\nActivating virtual environment... "
source venv/bin/activate
printf "Virtual environment created.\n"

printf "\nInstalling dependencies... "
venv/bin/pip install -r requirements.txt
printf "Dependencies installed.\n"

printf "\nDon't forget to run 'source venv/bin/activate' before running the program!\n"
