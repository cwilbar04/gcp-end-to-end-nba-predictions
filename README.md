# nba_predictions
[![CircleCI CI/CD Pipeline](https://circleci.com/gh/cwilbar04/nba-predictions.svg?style=shield)](https://circleci.com/gh/cwilbar04/nba-predictions)


Cloud-native analytics application that is hosted on the Google Cloud Platform used to predict NBA scores in head to head match-ups.

https://nba-predictions-prod.uc.r.appspot.com/

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
 
Create static training data by executing the following query in the big query console (or progmatically using python): 

```SQL
EXECUTE IMMEDIATE CONCAT('CREATE OR REPLACE TABLE `nba.model_training_data_', FORMAT_DATE('%Y%m%d', CURRENT_DATE())
    ,'` AS SELECT game_key, spread, season,game_date,is_home_team,incoming_is_win_streak,incoming_wma_10_pace',
    ',incoming_wma_10_efg_pct,incoming_wma_10_tov_pct,incoming_wma_10_ft_rate,incoming_wma_10_off_rtg,incoming_wma_10_opponent_efg_pct',
    ',incoming_wma_10_opponent_tov_pct,incoming_wma_10_opponent_ft_rate,incoming_wma_10_opponent_off_rtg',
    ',incoming_wma_10_starter_minutes_played_proportion,incoming_wma_10_bench_plus_minus,incoming_wma_10_opponnent_starter_minutes_played_proportion',
    ',incoming_wma_10_opponent_bench_plus_minus FROM `nba.model_game` ');
``` 
 
Create AutoML Regression Model by running following code in big query console (or programatically using python): 

```SQL
CREATE OR REPLACE MODEL nba.automl_regression
  OPTIONS(model_type='AUTOML_REGRESSOR', BUDGET_HOURS = 1,
  OPTIMIZATION_OBJECTIVE = 'MINIMIZE_MAE',  input_label_cols=['spread'])
AS SELECT spread, is_home_team,incoming_is_win_streak,incoming_wma_10_pace
    ,incoming_wma_10_efg_pct,incoming_wma_10_tov_pct,incoming_wma_10_ft_rate,incoming_wma_10_off_rtg
    ,incoming_wma_10_opponent_efg_pct,incoming_wma_10_opponent_tov_pct,incoming_wma_10_opponent_ft_rate
    ,incoming_wma_10_opponent_off_rtg,incoming_wma_10_starter_minutes_played_proportion
    ,incoming_wma_10_bench_plus_minus,incoming_wma_10_opponnent_starter_minutes_played_proportion
    ,incoming_wma_10_opponent_bench_plus_minus FROM `nba.model_training_data_20210228`;
``` 
 

