# NBA Predictions

[![CircleCI CI/CD Pipeline](https://circleci.com/gh/cwilbar04/nba-predictions.svg?style=shield)](https://circleci.com/gh/cwilbar04/nba-predictions)

## Overview

Cloud-native analytics application that is hosted on the Google Cloud Platform used to predict NBA point srpread in head to head match ups.

This project demonstrates building a completely serverless analytics application on Google Cloud Platform.





## My App Engine Hosted Website
https://nba-predictions-prod.uc.r.appspot.com/


## Create your Own Application
Create and activate a [python virtual environment](https://docs.python.org/3/tutorial/venv.html).

To create your own application clone this repository to a local file path and navigate to nba-predictions folder.

Run "make install" to install all required packages. (See [best answer on StackOverflow](https://stackoverflow.com/questions/32127524/how-to-install-and-use-make-in-windows) for installing Make on Windows)

Launch jupyter notebook server and open the "Project Creation Workbook" in the project_creation folder ([link]())

Complete pre-requisites and follow all steps to create everything you need to host your own web page!

## Model Building

All ML Models in this project were created directly in the Google Cloud Console.

## Data Ingestion

<img src="/diagrams/Data Ingestion Diagram.png" alt="Data Ingestion Architecture Diagram"/>

All data in this project is web scraped from [Basketball-Reference](https://www.basketball-reference.com/) using python's BeautifulSoup package. There are two Google Cloud Functions that scrape data directly from this website: nba_basketball_reference_scraper and nba_get_upcoming_games. A third Google Cloud function, nba_model_game_refresh, connects to create a "model" table that combines and enriches the data in the raw tables loaded by the nba_basketball_reference_scraper function.

#### Function Information:
**
- **nba_basketball_reference_scraper**
    - The code for this function is found in the [scraper](/scraper) folder and this folder is deployed to Google Cloud Functions using gcloud function deploy. The python script is in main.py and the packages required are in the requirements.txt file. There is also  very basic init file with a version number and a .gcloudignore file to not upload the init file to Google Cloud Functions.
    - This python function takes a Start Date and End Date and loops through the Schedule&Results page for each Year/Month in the time period ([Example]https://www.basketball-reference.com/leagues/NBA_2021_games-march.htmlBox) and gets the list of box score pages to scrape. The scraper then loops through each of these box score pages ([Example](https://www.basketball-reference.com/boxscores/202103010ORL.html)) and scrapes data includes game date, home team, away team, line score, and Basketball Reference's ["Four Factors"](https://www.basketball-reference.com/about/factors.html) metrics in to a raw_basketballreference_game table in BigQuery. Next the "Basic Box Score" stats for the players on both teams are scraped in to a raw_basketballreference_playerbox table in BigQuery.
    - Start Date and End Date can be passed as a JSON payload in a PUT request with format {"StartDate":"YYYY-MM-DD","EndDate":"YYYY-MM-DD"}
    - If no Start Date is passed, then it will use one day greater than the max date in the raw_basketballreference_game table
    - If no End Date is passed, the it will use "yesterday"
    - Cloud Scheduler does not pass Start/End Date so that the table is always being kept up to date
    - The function also includes a de-duplication step at the end in case there were any errors and you end up loading the same date twice

- **nba_get_upcoming_games**
    - The code for this function is found in the [get_schedule](/get_schedule) folder and this folder is deployed to Google Cloud Functions using gcloud function deploy. The python script is in main.py and the packages required are in the requirements.txt file. There is also  very basic init file with a version number and a .gcloudignore file to not upload the init file to Google Cloud Functions.
    - This python function takes "ScheduleDays" as an input and loops the Schedule&Results page for each Year/Month ([Example]https://www.basketball-reference.com/leagues/NBA_2021_games-march.htmlBox) in the time period starting from the date the function is executed until "ScheduleDays" later. The scraper gets the game date and home/away team and creates a dictionary which is stored as an upcoming.json file which the function loads to the default app engine storage bucket.
    - The "ScheduleDays" parameter can be passed as a JSON payload in a PUT Request with format "{"ScheduleDays":"Number"}
    - If no "ScheduleDays" are passed, the function defaults to 14 days
    - Cloud scheduler does not pass "ScheduleDays" so there are always 14 days worth of games uploaded to the storage bucket to later be displayed on the web page.

- **nba_model_game_refresh**
    - The code for this function is found in the [data_model](/data_model) folder and this folder is deployed to Google Cloud Functions using gcloud function deploy. The python script is in main.py and the packages required are in the requirements.txt file. There is also  very basic init file with a version number and a .gcloudignore file to not upload the init file to Google Cloud Functions.
    - This python function transforms the raw_basketballreference_game and raw_basketballreference_playerbox table by combining them and adding additional useful metrics such as incoming rest days and bench plus minus and loads the data in to the model_game table.
  





## Continuous Integration/Continuous Delivery

<img src="/diagrams/CI_CD Diagram.png" alt="CI\CD Architecture Diagram"/>

For CI/CD with this project I choose to use [CiricleCI](https://circleci.com/)

See [Getting Started](https://circleci.com/docs/2.0/getting-started/) on how to create an account and link it to your Github Repository

You can find my configuration for this project in the .circleci folder in the config.yaml file

In order to use the same config file you will need to set up the following [project variables](https://circleci.com/docs/2.0/env-vars/#setting-an-environment-variable-in-a-project). Note that currently you hve to create a separate entry per project for many of these. In a future release I will look to use contexts and other techniques to reduce this overhead.
- GITHUB_USER_EMAIL
- GITHUB_USER_NAME
- GCLOUD_PROJECT_ID_DEV
    - Project ID for DEV project
- CIRCLE_CI_DEPLOYER_DEV
    - email adress for Circle CI Deployer Service Account in DEV project
- CIRCLE_CI_DEPLOYER_DEV_KEY
    - JSON Service Key for CirclleCI Deployer Service Account in DEV project
- CLOUD_FUNCTION_SERVICE_ACCOUNT_DEV
    - email adress for Cloud Function Run Service Account in DEV project
- CLOUD_STORAGE_BUCKET_DEV
    - Default Cloud Storage Bucket name for App Engine in DEV project where Upcoming Games file stored
- GCLOUD_PROJECT_ID_TEST
    - Project ID for TEST project
- CIRCLE_CI_DEPLOYER_TEST
    - email adress for Circle CI Deployer Service Account in TEST project
- CIRCLE_CI_DEPLOYER_TEST_KEY
    - JSON Service Key for CirclleCI Deployer Service Account  in TEST project
- CLOUD_FUNCTION_SERVICE_ACCOUNT_TEST
    - email adress for Cloud Function Run Service Account in TEST project
- CLOUD_STORAGE_BUCKET_TEST
    - Default Cloud Storage Bucket name for App Engine in TEST project where Upcoming Games file stored
- GCLOUD_PROJECT_ID_PROD
    - Project ID for PROD project
- CIRCLE_CI_DEPLOYER_PROD	
    - email adress for Circle CI Deployer Service Account in PROD project
- CIRCLE_CI_DEPLOYER_PROD_KEY
    - JSON Service Key for CirclleCI Deployer Service Account in PROD project
- CLOUD_FUNCTION_SERVICE_ACCOUNT_PROD
    - email adress for Cloud Function Run Service Account in PROD project
- CLOUD_STORAGE_BUCKET_PROD
    - Default Cloud Storage Bucket name for App Engine in PROD project where Upcoming Games file stored

Cuntinous Integration currently involves always running pylint on any python code before preceeding with any other steps in CirclCi. After deploying in test to see if code changes are ready for PROD there is currently only an App Engine test that makes sure there is a valid response for all web page routes. This is a great integration test to make sure that everything was setup but future release will have better tests. Testing is accomplished using the "make test" command which utilizes pytest to run the testing scripts in the tests folder. 

Continuous Delivery (CD) is set up to conditionally deploy based on pushes (updates) to the specific folder path where deployable code resides.
  - NOTE: This only works if push to folder path, not on MERGE commands
  - Need to set up anything that needs to be deployed in its own file path
  - Conditionally deploys when push in named file path in the deploy job in the .circleci\app.yaml setup
  - Only deploys if initial pylint tests phase pass.

See the diagram below for the full CI/CD pipeline setup:



## Benchmark Testing

To perform benchmark testing using apache beam run the following commands on Google Cloud Shell.
Check out this [website](https://www.datadoghq.com/blog/apachebench/) for more info on interpreting results.

Download and activate apache beam
```cmd
sudo apt install apache2
sudo service apache2 start
```

Test the home page - replace url with your own url
```cmd
ab -n 100 -c 10 https://nba-predictions-prod.uc.r.appspot.com/
```

Test the Upcoming Games page
```cmd
ab -n 100 -c 10 https://nba-predictions-prod.uc.r.appspot.com/UpcomingGames
```

Test the Choose Teams page
```cmd
ab -n 100 -c 10 https://nba-predictions-prod.uc.r.appspot.com/ChooseTeams
```

Create file to test Choose Teams POST method (prediction results)
```cmd
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

 

