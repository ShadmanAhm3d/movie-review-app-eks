#!/bin/bash
cd /home/ubuntu/movie-review/movie-review-app/backend/
nohup python3 app.py > app.log 2>&1 &

