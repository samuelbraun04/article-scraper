#######################################################################################
#######################################################################################
#######################################################################################

search_query = 'Artificial Intelligence' #term to find articles about
number_of_words = 200 #very rough estimate
maximum_number_of_articles = 3 #max number of articles for the program to find

#######################################################################################
#######################################################################################
#######################################################################################

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import datetime
import openai
import requests
import time

client = openai.Client(api_key=(open('openai_key.txt').read()).strip())
options = webdriver.ChromeOptions()
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)
response = requests.get('https://newsapi.org/v2/everything?q='+search_query+'&apiKey='+(open('newsapi_key.txt').read()).strip())
metdata_of_articles = []

if response.status_code != 200:
    exit("Failed to retrieve data:"+ response.status_code)
else:
    data = response.json()

article_counter = 0
for article in data['articles']:
    
    driver.get(article['url'])
    time.sleep(5)

    article_content = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))).text
    article_response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        max_tokens=int(number_of_words*1.3333),
        messages=[
            {"role": "system", "content": "You are a helpful assistant that takes large amounts of text and summarizes the article interlaced within the text."},
            {"role": "user", "content": "Summarize the article found within the text: "+article_content}
        ]
    )
    article_summarized = article_response.choices[0].message.content

    metdata_of_articles.append([article['title'], article['publishedAt'], article['url'], article_summarized])
    article_counter+=1

    if (article_counter == maximum_number_of_articles):
        break

current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

with open(f"Summarized\summarized_articles_{formatted_datetime}.txt", "w") as file:
    for article in metdata_of_articles:
        file.write('Title: '+article[0]+ "\n")
        file.write('Date: '+article[1]+ "\n")
        file.write('URL: '+article[2]+ "\n")
        file.write('Summarized Content: '+article[3]+ "\n")
        file.write('\n\n\n')