# NBA Predictions

[![CircleCI CI/CD Pipeline](https://circleci.com/gh/cwilbar04/nba-predictions.svg?style=shield)](https://circleci.com/gh/cwilbar04/nba-predictions)

## Overview

Cloud-native analytics application that is hosted on the Google Cloud Platform used to predict NBA point srpread in head to head match ups.

This project demonstrates building a completely serverless analytics application on Google Cloud Platform.

## My App Engine Hosted Website
https://nba-predictions-prod.uc.r.appspot.com/


## Create your Own Application
To create your own application clone this repository to a local file path.

Create a [python virtual environment](https://docs.python.org/3/tutorial/venv.html).

Launch jupyter notebook server and open the "Project Creation Workbook" in the project_creation folder ([link]())

Complete pre-requisites and follow all steps to create everything you need to host your own web page!


## Continuous Integration/Continuous Delivery

CircleCI needs following variables defined
- CLOUD_REPO	
- GCLOUD_PROJECT_ID	
- GCLOUD_SERVICE_KEY


CD set up conditionally based on folder pushes
  - NOTE: This only works if push to folder path, not on MERGE commands
  - Need to set up anything that needs to be deployed in its own file path
  - Conditionally deploys when push in named file path in the deploy job in the .circleci\app.yaml setup
  - Only deploys if initial test (lint) phase passes


## Benchmark Testing

To perform benchmark testing using apache beam run the following commands on Google Cloud Shell.
Check out this [website](https://www.datadoghq.com/blog/apachebench/) for more info on interpreting results.

Download and activate apache beam
```
sudo apt install apache2
sudo service apache2 start
```

Test the home page - replace url with your own url
```
ab -n 100 -c 10 https://nba-predictions-prod.uc.r.appspot.com/
```

Test the Upcoming Games page
```
ab -n 100 -c 10 https://nba-predictions-prod.uc.r.appspot.com/UpcomingGames
```

Test the Choose Teams page
```
ab -n 100 -c 10 https://nba-predictions-prod.uc.r.appspot.com/ChooseTeams
```

Create file to test Choose Teams POST method (prediction results)
```
cat > post_test.txt << EOF
--1234567890
Content-Disposition: form-data; name="AwayTeam"
Milwaukee Bucks
--1234567890
Content-Disposition: form-data; name="HomeTeam"
Chicago Bulls
--1234567890
Content-Disposition: form-data; name="Model"
baseline_linear_model
--1234567890--
EOF
```

Test post results using created file with form data
```cmd
ab -n 100 -c 10 -p ./post_test.txt -T 'multipart/form-data; boundary=1234567890' https://nba-predictions-prod.uc.r.appspot.com/ChooseTeams
```

 

