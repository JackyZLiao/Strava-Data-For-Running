#!/bin/bash

cd "/Users/jackyliao/Desktop/Uni/Personal Projects/Strava-Data-For-Running"

git add .
git commit --allow-empty -m "Regular empty commit"
git push

if [ $? -eq 0 ]; then
    echo "Successfully made an empty commit and pushed."
else
    echo "Error making empty commit or pushing"
fi
