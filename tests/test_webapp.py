import requests

url = 'https://nba-predictions-test.uc.r.appspot.com/'

def web_response_ok(url):
    try:
        r = requests.head(url)
    except:
        assert False
    
    assert r.status_code == 200

if __name__ == '__main__':
    web_response_ok(url)
