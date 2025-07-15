# config/topics_config.py
"""
Configuration for different topics and their associated keywords/hashtags
"""

# Topic-specific hashtags and keywords
TOPICS_CONFIG = {
    'technology': {
        'hashtags': [
            '#AI', '#MachineLearning', '#TechNews', '#Innovation', 
            '#SoftwareDevelopment', '#DataScience', '#CloudComputing',
            '#Cybersecurity', '#IoT', '#Blockchain', '#TechTrends'
        ],
        'keywords': [
            'artificial intelligence', 'machine learning', 'programming',
            'software development', 'tech startup', 'innovation',
            'digital transformation', 'automation'
        ],
        'search_queries': [
            '#AI OR #MachineLearning OR #TechNews',
            'artificial intelligence lang:en',
            'software development trends',
            '#Innovation OR #TechTrends'
        ]
    },
    
    'stock_market': {
        'hashtags': [
            '#StockMarket', '#Trading', '#Investing', '#Finance',
            '#WallStreet', '#Stocks', '#Investment', '#MarketNews',
            '#FinTech', '#Crypto', '#Bitcoin', '#NYSE', '#NASDAQ'
        ],
        'keywords': [
            'stock market', 'trading', 'investing', 'financial markets',
            'bull market', 'bear market', 'portfolio', 'dividends',
            'earnings report', 'market analysis'
        ],
        'search_queries': [
            '#StockMarket OR #Trading OR #Investing',
            'stock market news lang:en',
            '#Finance OR #WallStreet',
            'market analysis OR trading tips'
        ]
    },
    
    'sports': {
        'hashtags': [
            '#Sports', '#Football', '#Basketball', '#Baseball',
            '#Soccer', '#Tennis', '#Olympics', '#NFL', '#NBA',
            '#MLB', '#FIFA', '#SportsNews', '#Athletics'
        ],
        'keywords': [
            'sports news', 'football', 'basketball', 'baseball',
            'soccer', 'tennis', 'olympic games', 'championship',
            'sports analysis', 'team performance'
        ],
        'search_queries': [
            '#Sports OR #Football OR #Basketball',
            'sports news lang:en',
            '#NFL OR #NBA OR #MLB',
            'championship OR tournament'
        ]
    }
}

# Collection settings for each topic
COLLECTION_SETTINGS = {
    'technology': {
        'tweets_per_collection': 200,
        'collection_frequency': 'hourly',
        'max_age_days': 7
    },
    'stock_market': {
        'tweets_per_collection': 150,
        'collection_frequency': 'every_30_minutes',
        'max_age_days': 3
    },
    'sports': {
        'tweets_per_collection': 250,
        'collection_frequency': 'every_2_hours',
        'max_age_days': 5
    }
}
