#Capstone Project: Analyzing Employer Trends
___
## Overview:
The goal of this project is to analyze topics in Glassdoor's employee reviews, in order to understand what employees like and dislike about their employers. To answer this question, I will need to accomplish a few things:
- Identify employers that have significantly high and low scores, and that have enough reviews to collect a large corpus.
- Collect employee review data for each of the employers that I have identified as a target for analysis.
- Analyze a corpus of positive feedback and a corpus of negative feedback using NLP techniques. Identify topics and their relative importances or frequency.

___
#### Gathering Data
In order to choose which employers to focus on for this analysis, I utilized Glassdoor's Employers API to pull all the employers in their database. In order to gather a large enough corpus of reviews, I chose to focus on companies with at least 100 reviews.

<p align="center">
  <img src="images/employers_with_at_least_100_reviews.png">
</p>

Since the goal of this project is to identify trends in what makes an employer especially great (or not so great), I chose to focus even further on companies with a score either below the 5th percentile or above the 95th percentile.

<p align="center">
  <img src="images/sig_scores.png">
</p>

___
#### Creating a Corpus
Once I identified which employers were good candidates for analysis, I needed to gather all the reviews for each company. Specifically, the "Pros" for each highly rated company as well as the "Cons" for each poorly rated company. Since Glassdoor does not have an API through which I could easily download reviews, it became a web scraping problem.

###### *Challenges*
Building a scraper to parse through each page for each employer and grab the relevant information was relatively straightforward; however, I did run into one major roadblock:

<p align="center">
  <img src="images/captcha_example.png"><br />
  <b>THE DREADED CAPTCHA</b>
</p>
