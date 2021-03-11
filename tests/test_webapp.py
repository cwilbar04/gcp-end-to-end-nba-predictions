import requests

def web_response_ok(url):
    try:
        r = requests.head(url)
    except Exception: 
        assert False
    
    assert r.status_code == 200

if __name__ == '__main__':
    test_url = 'https://nba-predictions-test.uc.r.appspot.com/'
    web_response_ok(test_url)
