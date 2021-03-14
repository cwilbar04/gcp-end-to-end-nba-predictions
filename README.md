# NBA Predictions

[![CircleCI CI/CD Pipeline](https://circleci.com/gh/cwilbar04/nba-predictions.svg?style=shield)](https://circleci.com/gh/cwilbar04/nba-predictions)

## Overview

This repository created by Christopher Wilbar initially for submission as a Final Project in my Northwestern Unviversity Master of Science in Data Science class: MSDS 434 Analytics Application Engineering.

This project demonstrated building a serverless Cloud-native analytics application that is hosted on the Google Cloud Platform used to predict NBA point srpread in head to head match ups. This project also demonstrates using CircleCI for Continuous Integration and Continuous Deployment strategies. Please read through the README document for detailed information regarding each part of the project.

The following GCP products are used:
- Google Cloud Functions
- Google Cloud Scheduler
- Google BigQuery
- Google App Engine
- Google Cloud Storage
- Google IAM&Admin
- Google Firestore

The project is brokwn down in to folders per use-case to simplify navigation and deployment.

#### Folder Information  
  
- [.circleci]([/.circleci])
    - Contains app.yaml folder with all configuration necessary for CI\CD
    - See [Continuous Integration/Continuous Delivery](#continuous-integration/continuous-delivery) section in README for more information
- [data_model]([/data_model])
    - Contains files needed for Google Cloud Function nba_model_game_refresh
    - See [nba_model_game_refresh](#function-information)] in function information in README for more information
- [diagrams]([/diagrams])
    - Contains media displayed in this README such as diagrams from [App.Diagrams.Net](https://app.diagrams.net/) and video demonstrations
- [get_schedule]([/get_schedule])
    - Contains files needed for Google Cloud Function nba_get_upcoming_games
    - See [nba_get_upcoming_games](#function-information)] in function information section in README for more information
- [project_creation]([/project_creation])
    - Contains Jupyter Notebooks to create your own complete version of this Application after cloning this project
    - See [Create your Own Application](#create-your-own-application) section in README for more information
- [scraper]([/scraper])
    - Contains files needed for Google Cloud Function nba_basketball_reference_scraper
    - See [nba_basketball_reference_scraper](#function-information)] in function information in README for more information
- [tests]([/tests])
    - Contains test scripts to use for validation
    - Makefile command "make test" uses pytest to run all tests in this folder
    - See [Continuous Integration/Continuous Delivery](#continuous-integration/continuous-delivery) section in README for more information
- [webapp]([/webapp])
    - Contains all files needed for Google App Engine website application
    - See [My App Engine Hosted Website](#my-app-engine-hosted-website) section in README for more information

Included in the top-level directory is:
- .gcloudignore
    - List of files, folders, and file types to not deploy to google cloud when using the Google Cloud SDK for deployment
    - Also contained in each of the Function and Web App directories
- .gitignore
    - List of files, folders, and file types to not upload to Github orgin branches
- LICENSE
    - MIT License for unrestricted use
- Makefile
    - Use "make" commands to make common, repeatble commands easier to execute
- README.md
    - This document
- requirements.txt
    - File containing all python packages used throughout this repository
    - Run make install to download all of these requirements before interacting with any python script or notebook
    - Also contained in each of the Function and Web App directories for the specific libraries required for each function/web app


## My App Engine Hosted Website

#### Web Link Home Page
  
https://nba-predictions-prod.uc.r.appspot.com/

#### Web Page Routes Diagram  
  
<img src="/diagrams/Web Page Diagram.png" alt="Web Page Diagram"/>

The code for the webpage used in this project can be found in the [webapp](/webapp) folder.

The primary functionality of the webapp is definied in main.py and uses the Flask framework.

On the top of all pages is a header that allows you to navigate to the different routes available and also a link to this github repository in the top right.

The home page serves as a landing page that shows you the current options available on the web page. As of 3/14/21 these are to navigate to the "Choose Teams" page to get ML Prediction results or navigate to the "Upcoming Games" page to view upcoming games in the next 14 days.

Navigating to the "Choose Teams" page displays a form for the end user to choose a Home Team and an Away Team along with a specific Model to use. The Team names you can select are the list of document names in the team_model_data collection (see information on the [nba_model_game_refresh](#function-information) function below for more info). This ensures that there will be appropriate data for the team you selected because the PREDICT function uses the data stored in these documents. The Model list is created by calling the model_list function in the google-bigquery python function and displays the name of all models that exist in the NBA dataset. Future enhancements will replace the display name with a "friendly name" and display more information about the specifics of the model.

When you choose "Submit" on the "Choose Teams" page a "POST" request is sent that uses the form data as an input in to the predicted_pointspread function in the [model.py](/webapp/model.py) script. This function gets the list of features for the selected model using the ML.FEATURE_INFO function passed as a query using a BigQuery Client. It also gets the fields stored in the Firestore document for both the Home Team and Away Team selction. The function then has logic to get the predicted spread by dynamically creating a BigQuery statement using the ML.PREDICT function to the Model submitted on the form and passing the values from Firestore for each team for all of the features that are included in the chosen Model. The result is then interpreted as a win/loss for the home team and passed as a readable statment to display to the end user. Future enhancments will seek to include more information than just the predicted point spread to get a better understanding of the confidence of the prediction.

**Note:** The current models have relatively poor performance (around 10 mean absolute error) due to the complexity of the point spread prediction. These predictions are intended solely to demonstrate the capabilites of GCP and should not be used to make any actual bets.

When you navigate to the "Upcoming Games" page, app engine reaches out the default App Engine Cloud Storage bucket to get the static\upcoming.json file written by the nba_get_upcoming_games function (see information on the [nba_model_game_refresh](#function-information) below for more info). This data contains the date, time, and home/away team for all games in the next 14 days and is displayed to the end user. Future enhancements will provide a more "beautiful" display and allow the user to choose any game in the list and generate a prediction by calling the "POST" method to the /ChooseTeams route with the teams selected, ideally letting the user choose which model to use.

## Create your Own Application
Create and activate a [python virtual environment](https://docs.python.org/3/tutorial/venv.html).

To create your own application clone this repository to a local file path and navigate to nba-predictions folder.

Run "make install" to install all required packages. (See [best answer on StackOverflow](https://stackoverflow.com/questions/32127524/how-to-install-and-use-make-in-windows) for installing Make on Windows)

Launch jupyter notebook server and open the ["Project Creation Workbook"]((/project_creation/Project Creation Workbook.ipynb)) in the project_creation folder.

```cmd
cd project_creation; jupyter notebook "Project Creation Workbook.ipynb" 
```

Complete pre-requisites and follow all steps to create everything you need to host your own web page!

## Data Ingestion

#### Data Ingestion Diagram  
  
<img src="/diagrams/Data Ingestion Diagram.png" alt="Data Ingestion Architecture Diagram"/>

All data in this project is web scraped from [Basketball-Reference](https://www.basketball-reference.com/) using python's BeautifulSoup package. There are two Google Cloud Functions that scrape data directly from this website: nba_basketball_reference_scraper and nba_get_upcoming_games. A third Google Cloud function, nba_model_game_refresh, connects to create a "model" table that combines and enriches the data in the raw tables loaded by the nba_basketball_reference_scraper function.

#### Function Information:

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
    - Cloud Scheduler does not pass "ScheduleDays" so there are always 14 days worth of games uploaded to the storage bucket to later be displayed on the web page.

- **nba_model_game_refresh**
    - The code for this function is found in the [data_model](/data_model) folder and this folder is deployed to Google Cloud Functions using gcloud function deploy. The python script is in main.py and the packages required are in the requirements.txt file. There is also  very basic init file with a version number and a .gcloudignore file to not upload the init file to Google Cloud Functions.
    - This python function transforms the raw_basketballreference_game and raw_basketballreference_playerbox table by combining them and adding additional useful metrics such as incoming rest days and bench plus minus and loads the data in to the model_game table. The data is converted to team vs. opponent data with is_home_team as a field to indicate the home team, effectively doubling the data size. Additionally, all metrics have an incoming weighted moving average column added that is currently linearly weighted using a lookback value of W=20, which can be modified directly in the code. This allows the ML models to be trained on data that is available at the time of prediction.
    - This function also relies on the BigQuery view games_to_load_to_model to identify which games have been loaded in to the raw_basketballreference_game table but have not been loaded in to the model_game table and only loads the new data to model_game table. See Step 9 - Create BigQuery View in the [Project Creation Workbook](/project_creation/Project Creation Workbook.ipynb) for view DDL.
    - This function also loads a separate document with the most recent row per team to the team_model_data collection in Cloud Firestore in Native Mode. This data is used by the web page when a Home Team and Away team are chosen for score prediction.
    - This function ignores any input parameters.
    - Cloud Scheduler runs this every day to make sure this is always up to date.


## Model Building

Before model training, a view with time filter is created for transparency in to what data was used by any given model. See Step 12 - Create Static Model Training Data View in the [Project Creation Workbook](/project_creation/Project Creation Workbook.ipynb) for command to create this view. This uses the "EXECUTE IMMEDIATE" statement to create the View name dynamically using the date of execution.

All ML Models in this project were created directly in the Google Cloud Console using the CREATE MODEL statement. See Step 13 - Create Baseline Linear Model using View in the [Project Creation Workbook](/project_creation/Project Creation Workbook.ipynb) for the exact syntax used to create the Baseline Linear Model.

Currently, prediction results are returned to the end user by dynamically building a BigQuery query that utilizes the ML.PREDICT function to return results in real-time using a BigQuery Client (see [model.py](/webapp/model.py) for the python code). For small scale use this is easy to build/maintain and cost-effective. In order to scale to much more usage the model would need to be exported and hosted elsewhere. This is a possible future enhancment. 

## Continuous Integration/Continuous Delivery

#### CI/CD Diagram  
  
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

 

