# config/api_keys.py
"""
Twitter API credentials configuration
Store your API keys securely here
"""

# Twitter API Configuration
TWITTER_API_CONFIG = {
    'consumer_key': 'V8IXh2jTrolGv295W14JHIgP7',
    'consumer_secret': 'wHOcbthoEBgRauImFNzaBmcQixDnMnPIHjP9PbwcQB1srAaomA',
    'access_token': '1812368902867046400-xnn3nwl5Royb1yDQQDMwJt2vWkWcP9',
    'access_token_secret': 'ImIUOgy7TXZbD5p5uSlOqcFEjD3ZCRM42Hlg2FijKK5kE',
    'bearer_token': 'AAAAAAAAAAAAAAAAAAAAALVE3AEAAAAAbmtxdWcYOBbxccvhngxsjMxGd7g%3DBpl0HNVD3LNSw017YzkXDxQrCR86TPX1V4SewKZDoGvecHM75C'  # For API v2
}

# API Rate Limits
RATE_LIMITS = {
    'tweets_per_request': 100,
    'requests_per_15_min': 180,
    'daily_tweet_limit': 500000
}