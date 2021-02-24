import pandas as pd
import numpy as np


def predicted_pointspread(form_dict):
    try:
        df = pd.DataFrame(form_dict, index=[0])
        pointspread = np.random.randint(-40,40)
        pointspread = 1 if pointspread == 0 else pointspread
        if pointspread > 0:
            winner = df['HomeTeam'][0]
            loser = df['AwayTeam'][0]
        else:
            winner = df['AwayTeam'][0]
            loser = df['HomeTeam'][0]
        return f'I predict the {winner} will beat the {loser} by {abs(pointspread)} points!'
    except Exception as e:
        return 'Sorry, there was a problem processing the data entered... Please go back and double check your entries, thanks!' from e
        