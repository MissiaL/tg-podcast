#!/bin/sh

cd "/home/p.g.alekseev/work/tinkoff/podcasts"
. ../.venv/bin/activate

python main.py pull
python main.py push

