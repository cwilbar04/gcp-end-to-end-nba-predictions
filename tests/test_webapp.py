import requests
import os

def web_response_ok(url):
    try:
        r = requests.head(url)
    except Exception:
        print("Invalid URL")
        return False
    
    return r.status_code == 200

def test_web():
    test_pages = ['','ChooseTeams','UpcomingGames'] # add to this list for every route in webapp/main.py
    project = os.environ.get('GCP_PROJECT_ID')
    for page in test_pages:
        result = web_response_ok(f'https://{project}.uc.r.appspot.com/{page}')
        assert result == True

if __name__ == '__main__':
    test_url = f'https://{os.environ.get("GCP_PROJECT_ID")}.uc.r.appspot.com/'
    web_response_ok(test_url)
