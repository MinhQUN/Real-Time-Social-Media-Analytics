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
            '#Cybersecurity', '#IoT', '#Blockchain', '#TechTrends', '#BigData', '#DigitalTransformation', '#Automation'
        ],
        'keywords': [
            'artificial intelligence', 'machine learning', 'programming',
            'software development', 'tech startup', 'innovation',
            'digital transformation', 'automation', 'technology trends',
            'cloud services', 'data analytics', 'cybersecurity threats','technology'
        ],
        'search_queries': [
            '#AI OR #MachineLearning OR #TechNews',
            'artificial intelligence lang:en',
            'software development trends',
            '#Innovation OR #TechTrends', 'digital transformation',
            'cloud computing OR cybersecurity',
        ]
    },
    
    'stock_market': {
        'hashtags': [
            '#StockMarket', '#Trading', '#Investing', '#Finance',
            '#WallStreet', '#Stocks', '#Investment', '#MarketNews',
            '#FinTech', '#Crypto', '#Bitcoin', '#NYSE', '#NASDAQ', '#FinancialNews', '#MarketAnalysis','#bitcoin', '#cryptocurrency'
        ],
        'keywords': [
            'stock market', 'trading', 'investing', 'financial markets',
            'bull market', 'bear market', 'portfolio', 'dividends',
            'earnings report', 'market analysis', 'bitcoin', 'cryptocurrency', 'financial news', 'investment strategies', 'stock analysis','xrp', 'ethereum', 'cryptocurrency trading', 'crypto market'
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
            '#MLB', '#FIFA', '#SportsNews', '#Athletics', '#Championship', '#TeamPerformance', '#SportsAnalysis', '#SportsUpdates', '#SportsHighlights', '#SportsEvents', '#SportsCommunity', '#SportsFans', '#soccer', '#football', '#basketball', '#tennis', '#olympics', '#championships', '#sportsnews', '#sportsupdates'
        ],
        'keywords': [
            'sports news', 'football', 'basketball', 'baseball',
            'soccer', 'tennis', 'olympic games', 'championship',
            'sports analysis', 'team performance','sports updates',
            'sports highlights', 'sports events', 'sports community','soccer news', 'football highlights', 'basketball scores', 'tennis tournaments', 'olympic results', 'sports fans'
        ],
        'search_queries': [
            '#Sports OR #Football OR #Basketball',
            'sports news lang:en',
            '#NFL OR #NBA OR #MLB',
            'championship OR tournament','sports analysis OR team performance', 'sports updates OR sports highlights'
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
