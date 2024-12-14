# import os
# import time
# import tweepy
# from dotenv import load_dotenv
# from datetime import datetime, timedelta
# import logging

# # Set up logging
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()

# # Twitter API credentials with validation
# TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
# TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
# TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
# TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
# TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# # Validate credentials
# if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, 
#             TWITTER_ACCESS_TOKEN_SECRET, TWITTER_BEARER_TOKEN]):
#     logger.error("Missing Twitter API credentials. Please check your .env file.")
#     raise ValueError("Missing Twitter API credentials")

# # Rate limiting configuration
# RATE_LIMIT_WINDOW = 15 * 60  # 15 minutes in seconds
# MAX_REQUESTS_PER_WINDOW = 150  # Free tier: 150 requests per 15-min window
# last_request_time = {}
# request_count = {}

# def check_rate_limit(endpoint):
#     """
#     Check if we're within rate limits for the given endpoint
#     Returns True if request can proceed, False if we need to wait
#     """
#     current_time = time.time()
    
#     # Initialize tracking for new endpoints
#     if endpoint not in last_request_time:
#         last_request_time[endpoint] = current_time
#         request_count[endpoint] = 0
#         return True
    
#     # Reset counters if we're in a new window
#     time_elapsed = current_time - last_request_time[endpoint]
#     if time_elapsed >= RATE_LIMIT_WINDOW:
#         last_request_time[endpoint] = current_time
#         request_count[endpoint] = 0
#         return True
    
#     # Check if we're within limits
#     if request_count[endpoint] < MAX_REQUESTS_PER_WINDOW:
#         request_count[endpoint] += 1
#         return True
    
#     logger.warning(f"Rate limit exceeded for endpoint: {endpoint}")
#     return False

# def get_twitter_client():
#     """
#     Get an authenticated Twitter API client
#     """
#     try:
#         logger.info("Creating Twitter API v2 client")
#         client = tweepy.Client(
#             bearer_token=TWITTER_BEARER_TOKEN,
#             consumer_key=TWITTER_API_KEY,
#             consumer_secret=TWITTER_API_SECRET,
#             access_token=TWITTER_ACCESS_TOKEN,
#             access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
#             wait_on_rate_limit=True
#         )
        
#         # Test the client
#         if not client:
#             logger.error("Failed to create Twitter client")
#             return None
            
#         # Test authentication
#         try:
#             client.get_me()
#             logger.info("Twitter client authentication successful")
#             return client
#         except Exception as e:
#             logger.error(f"Twitter client authentication failed: {str(e)}")
#             return None
            
#     except Exception as e:
#         logger.error(f"Error creating Twitter client: {str(e)}")
#         return None

# def get_twitter_api():
#     """
#     Get authenticated Twitter API v1.1 instance (for some features not in v2)
#     """
#     try:
#         logger.info("Creating Twitter API v1.1 instance")
#         auth = tweepy.OAuth1UserHandler(
#             TWITTER_API_KEY,
#             TWITTER_API_SECRET,
#             TWITTER_ACCESS_TOKEN,
#             TWITTER_ACCESS_TOKEN_SECRET
#         )
#         api = tweepy.API(auth, wait_on_rate_limit=True)
        
#         # Test the API
#         if not api:
#             logger.error("Failed to create Twitter API")
#             return None
            
#         # Test authentication
#         try:
#             api.verify_credentials()
#             logger.info("Twitter API authentication successful")
#             return api
#         except Exception as e:
#             logger.error(f"Twitter API authentication failed: {str(e)}")
#             return None
            
#     except Exception as e:
#         logger.error(f"Error creating Twitter API: {str(e)}")
#         return None

# def safe_twitter_request(endpoint, func, *args, **kwargs):
#     """
#     Safely execute a Twitter API request with rate limiting
#     """
#     if not check_rate_limit(endpoint):
#         logger.warning(f"Rate limit exceeded for endpoint: {endpoint}")
#         raise Exception("Rate limit exceeded. Please try again later.")
    
#     try:
#         # Add small delay between requests
#         time.sleep(1)  # 1 second delay between requests
#         logger.info(f"Making Twitter API request to endpoint: {endpoint}")
#         response = func(*args, **kwargs)
#         logger.info(f"Twitter API request successful: {endpoint}")
#         return response
#     except tweepy.TooManyRequests:
#         logger.error(f"Twitter rate limit exceeded for endpoint: {endpoint}")
#         raise Exception("Twitter rate limit exceeded. Please try again in 15 minutes.")
#     except tweepy.TwitterServerError as e:
#         logger.error(f"Twitter server error for endpoint {endpoint}: {str(e)}")
#         raise Exception("Twitter is experiencing issues. Please try again later.")
#     except Exception as e:
#         logger.error(f"Twitter API error for endpoint {endpoint}: {str(e)}")
#         raise Exception(f"Twitter API error: {str(e)}")
