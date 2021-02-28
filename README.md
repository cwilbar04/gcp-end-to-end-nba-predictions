# nba_predictions
[![CircleCI](https://circleci.com/gh/cwilbar04/nba-predictions.svg?style=shield)](https://circleci.com/gh/cwilbar04/nba-predictions)

![Python application test with Github Actions](https://github.com/cwilbar04/nba-predictions/workflows/Python%20application%20test%20with%20Github%20Actions/badge.svg)


MSDS 434 Final Project - Cloud-native analytics application that is hosted on the Google Cloud Platform used to predict NBA scores in head to head match-ups.

Account that runs Google Cloud Function must have: 
  - Project - Editor 
  - BigQuery Data Editor 
  - Cloud Run Service Agent
  - BigQuery Edit permissions

Need deployer service account set up with JSON saved as GCLOUD_SERVICE_KEY in CircleCI with following permissions:
  - App Engine Deployer
  - App Engine Service Admin
  - Cloud Functions Developer
  - Service Account User
  - Storage Object Admin
  - Cloud Build Service Account

Need to enable the following Google Cloud APIs:
  - App Engine Admin API
  - BigQuery API
  - Cloud Build API
  - Cloud Functions API
  - Cloud Logging API
  - Cloud Monitoring API
  - Cloud Resource Manager API
  - Cloud Scheduler API
  - Compute Engine API

CircleCI needs following variables defined
- CLOUD_REPO	
- GCLOUD_PROJECT_ID	
- GCLOUD_SERVICE_KEY

Basketball Data Loaded from BasketballReference.com:
Sports Reference LLC. Basketball-Reference.com - Basketball Statistics and History. https://www.basketball-reference.com/.

CD set up conditionally based on folder pushes
  - NOTE: This only works if push to folder path, not on MERGE commands
  - Need to set up anything that needs to be deployed in its own file path
  - Conditionally deploys when push in named file path in the deploy job in the .circleci\app.yaml setup
  - Only deploys if initial test (lint) phase passes

Create Bigquery View to identify games that need to be loaded to the model_game table with following code: 
 
```SQL
CREATE OR REPLACE VIEW nba.games_to_load_to_model AS

WITH model_load_games as (SELECT 
distinct left(game_key,length(game_key)-1) as game_key 
FROM `nba.model_game`
)

    SELECT distinct order_of_games_per_team.game_key, 
    CASE WHEN model_load_games.game_key is NULL THEN 1 ELSE 0 END as NEEDS_TO_LOAD_TO_MODEL
    FROM (
            SELECT team, game_key, row_number() OVER (PARTITION BY team ORDER BY game_date desc) as game_number
            FROM (
                    SELECT
                        home_team_name as team, game_date, game_key
                    FROM  `nba.raw_basketballreference_game`
    
                    UNION DISTINCT 

                    SELECT
                        visitor_team_name as team, game_date, game_key
                    FROM  `nba.raw_basketballreference_game`

                 ) games_per_team

            )order_of_games_per_team
            
    LEFT JOIN model_load_games ON model_load_games.game_key = order_of_games_per_team.game_key
    WHERE 
        game_number <= 11
        and team in (
                    SELECT 
                        distinct home_team_name as team_to_load
                    FROM `nba.raw_basketballreference_game`
                    WHERE 
                    game_date >= (SELECT date_sub(max(game_date), INTERVAL 1 YEAR) FROM `nba.raw_basketballreference_game` )
                    and game_key not in (SELECT game_key FROM model_load_games)

                    UNION DISTINCT

                    SELECT 
                        distinct visitor_team_name as team_to_load
                    FROM `nba.raw_basketballreference_game`
                    WHERE 
                    game_date >= (SELECT date_sub(max(game_date), INTERVAL 1 YEAR) FROM `nba.raw_basketballreference_game`)
                    and game_key not in (SELECT game_key FROM model_load_games)              
                    ) 
```