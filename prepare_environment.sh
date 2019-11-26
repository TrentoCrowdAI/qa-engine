#!/bin/bash

mkdir actual_models
cd actual_models || exit
git clone https://github.com/chiayewken/bert-qa
mkdir squad_dir
cd squad_dir || exit
wget https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v1.1.json
wget https://raw.githubusercontent.com/allenai/bi-att-flow/master/squad/evaluate-v1.1.py
wget https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v1.1.json