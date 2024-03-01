import requests
import redis
import matplotlib.pyplot as plt
from collections import defaultdict
import json

class PostsDataFetcher:
    """
    This class is responsible for fetching post data from a provided API URL.
    """
    
    def __init__(self, api_url):
        """
        Initializes the PostsDataFetcher with an API URL.
        
        :param api_url: URL from which to fetch post data
        """
        self.api_url = api_url

    def fetch_data(self):
        """
        Fetches data from the API URL and returns it as JSON.
        
        :return: JSON data fetched from the API
        """
        response = requests.get(self.api_url)
        response.raise_for_status()  # Raises an exception for bad responses
        return response.json()

class RedisDataHandler:
    """
    This class handles interactions with a Redis database, storing and retrieving data.
    """
    
    def __init__(self, host='localhost', port=6379):
        """
        Initializes the RedisDataHandler with connection details.
        
        :param host: Redis server host
        :param port: Redis server port
        """
        self.db = redis.Redis(host=host, port=port, decode_responses=True)
        self.check_connection()

    def check_connection(self):
        """
        Verifies that the Redis server is accessible.
        """
        try:
            self.db.ping()
        except redis.exceptions.ConnectionError as e:
            print(f"Redis connection error: {e}")
            exit(1)

    def insert_data(self, key, json_data):
        """
        Inserts JSON data into Redis under a specified key.
        
        :param key: Key under which JSON data is stored
        :param json_data: JSON data to store
        """
        serialized_data = json.dumps(json_data)
        self.db.set(key, serialized_data)

    def retrieve_data(self, key):
        """
        Retrieves JSON data from Redis by key.
        
        :param key: Key corresponding to the data to retrieve
        :return: JSON data retrieved from Redis
        """
        serialized_data = self.db.get(key)
        if serialized_data:
            return json.loads(serialized_data)
        return None

class PostsDataProcessor:
    """
    This class processes post data, providing functionalities like plotting and searching.
    """
    
    def __init__(self, data):
        """
        Initializes the PostsProcessor with post data.
        
        :param data: Data to be processed
        """
        self.data = data

    def plot_posts_length(self):
        """
        Creates and saves a bar chart of post lengths.
        """
        post_lengths = [len(post['body']) for post in self.data]
        plt.figure(figsize=(12, 6))
        plt.bar(range(len(post_lengths)), post_lengths)
        plt.xlabel('Post Index')
        plt.ylabel('Length of Post Body')
        plt.title('Length of Posts')
        plt.savefig('length_of_posts.png')

    def count_posts_by_user(self):
        """
        Prints the number of posts created by each user.
        """
        user_post_counts = defaultdict(int)
        for post in self.data:
            user_post_counts[post['userId']] += 1
        for user_id, count in user_post_counts.items():
            print(f"User {user_id} has {count} posts")

    def search_posts_by_user_id(self, user_id):
        """
        Searches and prints posts made by a specific user ID.
        
        :param user_id: User ID for which to search posts
        """
        matched_posts = [post for post in self.data if post['userId'] == user_id]
        print(f"Found {len(matched_posts)} posts by user '{user_id}':")
        for post in matched_posts:
            print(f" - {post['title']}")


"""
Main function to fetch, store, retrieve, and process post data.
"""
API_URL = 'https://jsonplaceholder.typicode.com/posts'
REDIS_KEY = 'jsonplaceholder:posts'

# Fetch and store data
fetcher = PostsDataFetcher(API_URL)
posts_data = fetcher.fetch_data()

redis_handler = RedisDataHandler()
redis_handler.insert_data(REDIS_KEY, posts_data)

# Retrieve and process data
stored_data = redis_handler.retrieve_data(REDIS_KEY)
processor = PostsDataProcessor(stored_data)
processor.plot_posts_length()
processor.count_posts_by_user()
processor.search_posts_by_user_id(5)


