import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import unicodedata
import re
import matplotlib.pyplot as plt
import json
import nltk
from statistics import mean
from numpy import arange

#Web crawl the given web page
def web_crawl_task1 (base_url):
    
    # Specify the initial page to crawl
    seed_item = 'index.html'
    seed_url = base_url + seed_item
    page = requests.get(seed_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # Object initializations
    visited = {}
    headline = {}
    visited[seed_url] = True
    headline[seed_url] = (soup.find("h1")).get_text()
    pages_visited = 1

    # Remove index.html
    links = soup.findAll('a')
    seed_link = soup.findAll('a', href=re.compile("^index.html"))
    to_visit_relative = [l for l in links if l not in seed_link]
    
    # Resolve to absolute urls
    to_visit = []
    for link in to_visit_relative:
        to_visit.append(urljoin(seed_url, link['href']))
    
    # Find all outbound links on succesor pages and explore each one 
    while (to_visit):
        # consume the list of urls
        link = to_visit.pop(0)

        # need to concat with base_url, an example item <a href="catalogue/sharp-objects_997/index.html">
        page = requests.get(link)

        # scraping code goes here
        soup = BeautifulSoup(page.text, 'html.parser')

        # Locate the Header, add to header list
        headline[link] = (soup.find("h1", class_="headline")).get_text()

        # mark the item as visited, i.e., add to visited list, remove from to_visit
        visited[link] = True
        to_visit
        new_links = soup.findAll('a')
        for new_link in new_links:
            new_item = new_link['href']
            new_url = urljoin(link, new_item)
            if new_url not in visited and new_url not in to_visit:
                to_visit.append(new_url)

        pages_visited = pages_visited + 1

    # create a series of the list of headlines and reset the index
    headlines = pd.Series(headline).reset_index()

    # rename column names to URL and Headline
    headlines.columns = ['url', 'headline']
    
    # write to csv excluding the index.html
    open('task1.csv','w').write(headlines[1:].to_csv(index=False))
    
    # Return list of URL and headlines excluding index.html
    return headlines


# Extract the name and score of the first player mentioned in the article
def web_scrape_task2 (url_list):
    
    # load Json file as dataframe
    data = pd.read_json('tennis.json', orient='records')
    
    # extract list of names from tennis data
    names = pd.Series(data['name'])
    names.name = 'player'
    
    # object initializations
    player_name = {}
    scores = {}
        
    # scraping goes here
    url = (url_list['url'])
    for i in range(len(url)):
        player = ''
        page = requests.get(url[i])
        soup = BeautifulSoup(page.text, 'html.parser')
        
        # Extract paragraphs in the article
        paragraph = ''
        result = soup.find_all('p')
        for res in range(0,len(result)):
            paragraph = paragraph + result[res].get_text()
        
        # Tokenize the message, add tags and create chunks of named entities
        sentList = nltk.sent_tokenize(paragraph)
        for sent in sentList:
            minimum = 1000
            for j in range(len(names)):
                # find the position of a name from json file from the chunk of persons
                pos = sent.upper().find(names[j].upper())
                if (pos > -1):
                    if pos > -1 and pos < minimum:
                        minimum = pos
                        player = names[j]
                         
            # if a player is found, store player name then break the loop to iterate sentences from the article
            if player:
                player_name[url[i]] = player
                break
        
        # process regular expression to extract game scores
        temp_scores = []
        score_pattern = r'(((\d+\-\d+)\s*)+\(\d+[\-/]\d+\)\s*)+((\d+\-\d+))*|(\d+\-\d+\s*){2,}'
        for sent in sentList:
            temp_score = re.search(score_pattern, sent)
            if temp_score:
                # remove excess space at the end, if any
                temp_score = re.sub('\s$','',temp_score.group())
                new_score = True
                same_score = False
                valid_score = True
                score1 = -1
                score2 = -1
                win = 0
                lose = 0
                tie = 0
                for rs in range(len(temp_score)):
                    if temp_score[rs] == ' ' or temp_score[rs] == '(' or temp_score[rs] == ')':
                        new_score = True
                        same_score = False
                    elif temp_score[rs] == '-' or temp_score[rs] == '/':
                        same_score = True
                        new_score = False
                    else:
                        # convert game scores to int type to get score value
                        if new_score == True:
                            if (rs-1 > 0) and temp_score[rs-1] != ' ' and temp_score[rs-1] != '(' and temp_score[rs-1] != ')':
                                score1 *= 10
                                score1 += int(temp_score[rs])
                            else:
                                score1 = int(temp_score[rs])
                        elif same_score == True:
                            score2 = int(temp_score[rs])
                            if (rs+1 < len(temp_score)) and (temp_score[rs+1] != ' ') and (temp_score[rs+1] != ')'):
                                    score2 *= 10
                                    score2 += int(temp_score[rs+1])
                                    rs += 1
                            same_score = False
                    
                    # check validity of game scores
                    if new_score == False and same_score == False:
                        if score1 >= score2+2 and (1 < abs(score1-score2) <= 6):
                            win += 1
                        elif score1+2 <= score2 and (1 < abs(score1-score2) <=6):
                            lose +=1
                        elif (score1 > score2 or score1 < score2) and abs(score1-score2) <=1:
                            tie +=1
                        else:
                            # invalid score
                            valid_score = False
                
                # check completeness of game scores, if winner cannot be decided (win==lose and no tie score)
                # discard score as invalid
                if win == lose and tie == 0:
                    # incomplete score
                    valid_score = False
                
                # store valid score then break the loop to iterate each sentence
                if valid_score:
                    scores[url[i]] = temp_score
                    break
                
    # rename column names to url and player
    players = pd.Series(player_name).reset_index()
    players.columns = ['url', 'player']
    
    # merge url_list with dataframe of player names
    url_headline_name = url_list.merge(players)
    # rename column names to url and score
    score_report = pd.Series(scores).reset_index()
    score_report.columns = ['url', 'score']
    
    # merge url_headline_name with dataframe of scores
    url_headline_name_score = url_headline_name.merge(score_report)
    
    # write to csv
    open('task2.csv','w').write(url_headline_name_score.to_csv(index=False))
    
    return url_headline_name_score

        
def ave_game_diff_task3 (records):
    
    game_scores = {}
    # extract the player and score columns from records
    player = records.iloc[:,2:]
    
   # group recorded scores by players
    player_record = player.groupby('player')
    
    # iterate through each player
    for player,score in player_record:
        score1 = -1
        score2 = -1
        game_diff = []
        # iterate the scores for each player
        for sc in score['score']:
            scores = str(sc)
            new_score = True
            same_score = False
            match_diff = 0
            # iterate through each character in the score and convert digits to integer
            for s in range(len(scores)):
                if scores[s] == ' ':
                    new_score = True
                    same_score = False
                elif scores[s] == '-' or scores[s] == '/':
                    if new_score == True:
                        same_score = True
                        new_score = False
                elif scores[s] == '(':
                    new_score = False
                    same_score = False
                else:
                    if new_score == True:
                        if (s-1 > 0) and scores[s-1] != ' ' and scores[s-1] != '(' and scores[s-1] != ')':
                            score1 *= 10
                            score1 += int(scores[s])
                        else:
                            score1 = int(scores[s])
                    elif same_score == True:
                        score2 = int(scores[s])
                        if (s+1 < len(scores)) and (scores[s+1] != ' ') and (scores[s+1] != ')'):
                            score2 *= 10
                            score2 += int(scores[s+1])
                            match_diff += score1 - score2
                        else:
                            match_diff += score1 - score2
            if sc:
                game_diff.append(abs(match_diff))
        
        # if there is a recorded score for the player, record the average game difference of the player
        if game_diff:
            game_scores[player] = pd.Series(game_diff).mean()
            
    col_name = ['player','avg_game_difference']    
    ave_game_diff = pd.Series(game_scores).reset_index()
    ave_game_diff.columns = col_name
    
    # write the record of average game differenct to task3.csv file
    open('task3.csv','w').write(ave_game_diff.to_csv(index=False))
    
    return ave_game_diff

    
def player_frequency_task4 (records):
    
    # extract the player and score columns from records
    player = records.iloc[:,2:]
    
    # group recorded scores by players
    player_record = player.groupby('player')
    
    count = {}
    
    # iterate each player and count the size of the recorded scores to be the frequency of articles for that player
    for player,score in player_record:
        count[player] = score['score'].count()
    
    # create a series and sort the frequencies in descending order to get the top 5 players
    col_name = ['player','number of articles']
    player_series = pd.Series(count).reset_index()
    player_series.columns = col_name
    player_count = player_series.sort_values(ascending = False, by = 'number of articles').head(5)
    
    # plot as a bar chart
    plt.title('Top '+str(len(player_count))+' Players Most Frequently Written About')
    plt.bar(arange(min(5,len(player_count))),player_count['number of articles'])
    plt.ylabel('Number of articles')
    plt.xticks(arange(min(5,len(player_count))),player_count['player'], rotation=30)
    plt.xlabel('Player name')
    plt.tight_layout()
    plt.savefig('task4.png',dpi=300)
    plt.show()
    plt.close()

    
def win_pct_task5 (records):
    
    # load Json file as dataframe
    data = pd.read_json('tennis.json', orient='records')
    
    # extract win percentage from the tennis.json data
    win_percentage = {}
    for player in records['player']:
        for i in range(len(data)):
            if player == data['name'][i]:
                win_percentage[player] = float(re.sub('\%$','',data['wonPct'][i]))
    
    win_percentage_pd = pd.Series(win_percentage).reset_index()
    win_percentage_pd.columns = ['player','win_percentage']
    
    agd_wp = win_percentage_pd.merge(records)
    avg_game_diff_win_pct = agd_wp.sort_values(by='win_percentage',ascending=False)
    
    fig, ax_win = plt.subplots()
    fig.suptitle('Win Rate and Avg Game Difference of Tennis Players')
    
    # define y-axis on the left
    ax_win.set_xlabel('Player name')
    ax_win.tick_params(axis='x', bottom=False, labelbottom=True, rotation=90)
    ax_win.set_ylabel('Win Percentage (%)',color=(0.2, 0.3, 0.8, 0.8),size='small')
    ax_win.tick_params(axis='y', labelcolor=(0.2, 0.3, 0.8, 0.8), labelsize='small')
    ax_win.bar(avg_game_diff_win_pct['player'],avg_game_diff_win_pct['win_percentage'],color=(0.2, 0.3, 0.8, 0.8))
    
    # create y-axis on the right
    ax_avg = ax_win.twinx()
    ax_avg.set_ylabel('Average Game Difference',color=(0.8, 0.1, 0.2, 0.8),size='small')
    ax_avg.tick_params(axis='y', labelcolor=(0.8, 0.1, 0.2, 0.8), labelsize='small')
    ax_avg.plot(avg_game_diff_win_pct['player'],avg_game_diff_win_pct['avg_game_difference'],color=(0.8, 0.1, 0.2, 0.8))
    fig.tight_layout()
    fig.subplots_adjust(top=0.9)
    fig.savefig('task5.png',dpi=300)
    fig.show()
    plt.close()
    
    
# Test function 
def test():
    
    #uncomment if error occurs
    #nltk.download('punkt')

    # Task1
    headlines = web_crawl_task1('http://comp20008-jh.eng.unimelb.edu.au:9889/main/')
    
    # Task2
    player_scores = web_scrape_task2(headlines)
    
    # Task3
    ave_game_diff = ave_game_diff_task3 (player_scores)
    
    # Task4
    player_frequency_task4 (player_scores)
    
    # Task5
    win_pct_task5 (ave_game_diff)

    
if __name__ == "__main__":
    test()
