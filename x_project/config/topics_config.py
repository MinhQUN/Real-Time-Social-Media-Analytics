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
            '#Cybersecurity', '#IoT', '#Blockchain', '#TechTrends', '#BigData', '#DigitalTransformation', '#Automation', '#Programming', '#TechStartup', '#Gadgets', '#5G', '#ARVR', '#QuantumComputing', '#EdgeComputing', '#DevOps', '#SaaS', '#FinTech', '#Robotics', '#technology'
        ],
        'keywords': [
            'artificial intelligence', 'machine learning', 'programming',
            'software development', 'tech startup', 'innovation',
            'digital transformation', 'automation', 'technology trends',
            'cloud services', 'data analytics', 'cybersecurity threats','technology', 'tech news', 'blockchain technology', 'internet of things', 'iot devices', 'quantum computing', '5g technology', 'augmented reality', 'virtual reality', 'vr ar', 'big data analytics', 'devops practices', 'saas solutions', 'fintech innovations', 'robotics advancements'
        ],
        'search_queries': [
            '#AI OR #MachineLearning OR #TechNews',
            'artificial intelligence lang:en',
            'software development trends',
            '#Innovation OR #TechTrends', 'digital transformation',
            'cloud computing OR cybersecurity', '#Blockchain OR #IoT', 'big data OR data analytics', 'automation OR programming', '#Robotics OR #FinTech'
        ]
    },
    
    'stock_market': {
        'hashtags': [
            '#StockMarket', '#Trading', '#Investing', '#Finance',
            '#WallStreet', '#Stocks', '#Investment', '#MarketNews',
            '#FinTech', '#Crypto', '#Bitcoin', '#NYSE', '#NASDAQ', '#FinancialNews', '#MarketAnalysis','#bitcoin', '#cryptocurrency', '#investing', '#trading', '#stocktrading', '#financialmarkets', '#forex', '#dividends', '#earningsreport', '#portfolio', '#bullmarket', '#bearmarket', '#stockanalysis', '#xrp', '#ethereum', '#cryptocurrencytrading', '#cryptomarket'
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
            'market analysis OR trading tips', '#Crypto OR #Bitcoin', 'financial news OR investment strategies', 'earnings report OR dividends'
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
            'championship OR tournament','sports analysis OR team performance', 'sports updates OR sports highlights', 'olympics OR fifa', 'sports events OR sports community', 'sports fans OR athletics'
        ]
    }
}

# Collection settings for each topic
COLLECTION_SETTINGS = {
    'technology': {
        'tweets_per_collection': 5,
        'collection_frequency': 'every_hour',
        'max_age_days': 7
    },
    'stock_market': {
        'tweets_per_collection': 10,
        'collection_frequency': 'every_30_minutes',
        'max_age_days': 3
    },
    'sports': {
        'tweets_per_collection': 5,
        'collection_frequency': 'every_2_hours',
        'max_age_days': 5
    }
}
