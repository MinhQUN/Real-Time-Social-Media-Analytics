# config/api_keys.py
"""
Twitter API credentials configuration
Store your API keys securely here
"""

# Twitter API Configuration
TWITTER_API_CONFIG = {
    'consumer_key': 'v9Vw82UI140alk6utWKMUD1uh',
    'consumer_secret': 'rsx3ANuLBEndkON6ULpo8NtNpc8QnvXviuU6lg264DxGRxNA8z',
    'access_token': '11812368902867046400-bHldS78ssABVusPNWOsV6e1in9EufV',
    'access_token_secret': 'm1jSqDc3LDrmCDjs8MiaK0wOR1qvrLsuUnuT4h27OMuHj',
    'bearer_token': 'AAAAAAAAAAAAAAAAAAAAALVE3AEAAAAAenugthFNc3zY1rFkDvz%2FPbw9H2E%3DrwtaePSajrn5cuK4pQ1niSEIozdfgn2RQA8H3yNpIyeDuRJ3uC'  # For API v2
}

# API Rate Limits
RATE_LIMITS = {
    'tweets_per_request': 100,
    'requests_per_15_min': 180,
    'daily_tweet_limit': 500000
}