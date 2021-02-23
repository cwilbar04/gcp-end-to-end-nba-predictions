# nba_predictions
[![CircleCI](https://circleci.com/gh/cwilbar04/nba-predictions.svg?style=shield)](https://circleci.com/gh/cwilbar04/nba-predictions)

![Python application test with Github Actions](https://github.com/cwilbar04/nba-predictions/workflows/Python%20application%20test%20with%20Github%20Actions/badge.svg)


MSDS 434 Final Project - Cloud-native analytics application that is hosted on the Google Cloud Platform used to predict NBA scores in head to head match-ups.

Account that runs Google Cloud Function must have: 
  Project - Editor 
  BigQuery Data Editor 
  Cloud Run Service Agent

  BigQuery Edit permissions


CircleCI needs following variables defined
CLOUD_REPO	
GCLOUD_PROJECT_ID	
GCLOUD_SERVICE_KEY

Need to setup Google Cloud Repository to Mirror Github - set this path as GLOUD_REPO

Must deploy Cloud Function using UI first
  - Show steps here

Basketball Data Loaded from BasketballReference.com 
Sports Reference LLC. Basketball-Reference.com - Basketball Statistics and History. https://www.basketball-reference.com/.

CD set up conditionally based on folder pushes
  - NOTE: This only works if push to folder path, not on MERGE commands