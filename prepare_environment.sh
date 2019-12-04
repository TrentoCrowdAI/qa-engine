#!/bin/bash

mkdir -p actual_models
cd actual_models || exit

READY_MODELS_FILE=ready_models_file.txt

#This check if the ready_models_file.txt is present, so the models are already downloaded, and check if the user doesn't force the re-download
if [ "$1" = "true" ] ; then
  rm $READY_MODELS_FILE
fi

if ! test -f "$READY_MODELS_FILE";  then
  FILEID="1rDO41n4-XnkVlfK2Z1woX7pu1YdGKkLY"
  FILENAME="bert-model.zip"
  mkdir tmp
  touch tmp/cookies.txt
  wget --load-cookies tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id='$FILEID -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id="$FILEID -O $FILENAME || exit
  rm -r tmp
  unzip $FILENAME || exit

  git clone https://github.com/chiayewken/bert-qa || exit
  mkdir -p squad_dir
  cd squad_dir || exit
  wget https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v1.1.json || exit
  wget https://raw.githubusercontent.com/allenai/bi-att-flow/master/squad/evaluate-v1.1.py || exit
  wget https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v1.1.json || exit

  cd ..
  touch $READY_MODELS_FILE
  echo "true" > $READY_MODELS_FILE
fi
