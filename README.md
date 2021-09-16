# COMP20008-EDP-Assignment-1
COMP20008 Elements of Data Processing 2020 Semester 1 - Project 1

## Background
A web server has been setup, containing a number of media reports on Tennis matches between 2004 and 2005. As data scientists, we would like to extract information from those reports and use that information to improve our understanding of player performance. A JSON data file containing player names and key statistics is also provided.

## The tasks
You are to perform a small data science project including some data processing and analysis using Python. Your responses to Tasks 1-5 must be contained in a single .py file. Specifically, you have the following tasks:

### Task 1
Crawl the website to find a complete list of articles available.
Produce a csv file containing the URL and headline of each the articles your crawler has found found. The CSV file should have two column headings url and headline and be called
task1.csv.

### Task 2
For each article found in Task 1, 

a) extract the name of the first player mentioned in the article. You can find a list of player names as part of the tennis.json file provided. We will assume the article is written about that player (and only that player).

b) extract the first complete match score identified in the article. You will need to use regular expressions to accomplish this. We will assume this score relates to the first named player in the article.

Produce a csv file containing the URL, headline, first player mentioned and first complete match score of each the articles your crawler has found. The csv file should have four column headings url, headline, player and score and be called task2.csv.

Note: Some articles may not contain a player name and/or a match score. These articles can be discarded.

### Task 3
For each article used in Task 2, identify the absolute value of the game difference. E.g. a 6-2 6-2 score has a game difference of 8, while a 6-4 4-6 6-4 score has a game difference of 2. The value is referred to as the `game difference`.
Produce a csv file containing the player name and average game difference for each player that at least one article has been written about. The csv file should have two column head-
ings player and avg game difference and be called task3.csv.

### Task 4
Generate a suitable plot showing five players that articles are most frequently written about and the number of times an article is written about that player.
Save this plot as a png file called task4.png.

### Task 5
Generate a suitable plot showing the average game difference for each player that at least one article has been written about and their win percentage. You can find a player’s win percentage in the tennis.json file.
Save this plot as a png file called task5.png.

### Task 6
Write a 3-4 page report to communicate the process and activities undertaken in the project, the analysis, and some limitations. Specifically, the report should contain the following information:

• A description of the crawling method and a brief summary the output for Task 1.

• A description of how you scraped data from each page, including any regular expressions used for Task 2 and a brief summary of the output.

• An analysis of the information shown in the two plots produced for Tasks 4 & 5, including a brief summary of the data used. The plots are to be shown (included) along with your analysis.

• A discussion of the appropriateness of associating the first named player in the article with the first match score.

• At least one suggested method for how you could figure out from the contents of the article whether the first named player won or lost the match being reported on.

• A discussion of what other information could be extracted from the articles to better understand player performance and a brief suggestion for how this could be done.
