# Dave Hogue - Project Proposals:
***
### *Project 1: Employer Trends*
The goal of this project is to gather data on employers, analyze employee satisfaction, and identify trends and factors that correlate with high employee satisfaction. This would be an NLP/PCA/NMF problem.

Possible source(s):
- Glassdoor API
- Will need to crawl/scrape actual ratings (pros & cons . . . separate corpora)
- Possibly look at company reviews and predict approximate rating if feasible
- Scraping "Top Companies . . ." articles to compare?

#####Notes:
- Use lemmatizer
- Possible Neural Net - attention / recurrent
- Look at Keras datasets (IMDB, Yelp?)
- Handling Unicode?


### *Project 2: Restaurant Trends*
Similar to project 1, the idea is to identify trends in highly rated restaurants, looking for spikes in mentions of food items in reviews or common menu items across popular restaurants (e.g. the rise of brussels sprouts, bacon, and kale in the last few years). This would also be an NLP/PCA/NMF problem.

Possible sources:
- Yelp API
- TripAdvisor API(?)

### *Project 3: Twitter - Presidential Election Edition*
Use Twitter's API to create a real-time representation of what people are talking about. This project would focus on the ability to handle massive amounts of data as well as using NLP/PCA/NMF to cluster tweets into topics, possibly derive sentiment of users toward candidates.

Possible Sources:
- Twitter API
