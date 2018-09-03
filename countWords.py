import requests

def count_words_at_url(url):
    resp = requests.get(url)
    word_count = len(resp.text.split())
    print("I LIKE CHICKEN, GIVE ME CHICKEN")
    print("WORDS I COUNTED: " + word_count)
    return word_count
