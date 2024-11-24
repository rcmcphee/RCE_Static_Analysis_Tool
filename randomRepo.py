import random
import requests

# API token for API requests to GitHub
GIT_API_TOKEN = ""

# Header parameter with API token
HEADER = {
    "Authorization": f"token {GIT_API_TOKEN}"
} if GIT_API_TOKEN else {}

# URL for making api requests for repositories
BASE_URL = "https://api.github.com/search/repositories"

# Language for search results
LANG = "language:Java"

# Percentage threshold for the desired lanaguage
THRESHOLD = 50

def randomReposInit(sampleSize):
    printedRepos = set()
    randomRepos(sampleSize, printedRepos)

# Function for developing a random sample of github repositories with at least 75% Java composition
def randomRepos(sampleSize, printedRepos):

    # Make sure sampleSize is an integer
    intSampleSize = int(sampleSize)

    page = random.randint(1, 10) # Randomize the starting page
    
    # Develop Git query parameters
    searchParam = {
        "q": LANG,
        "sort": random.choice(["stars", "updated", "forks"]),
        "order":"desc",
        "per_page": 200,
        "page": page
    }

    # Make response call
    response = requests.get(BASE_URL, headers=HEADER, params=searchParam)
    # Resposne error check
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.json()}")
        return []
    
    print(f"Remaining requests: {response.headers['X-RateLimit-Remaining']}") # Debugging
    
    # Initialize array for coding language checking
    searchResponseRepositories = response.json().get("items", [])

    # Go through and check for proper parameter meeting
    for repo in searchResponseRepositories:
        # Save details for later commands
        repo_url = repo["html_url"]
        langURL = repo["languages_url"]

        # Skip already printed repositories
        if repo_url in printedRepos:
            continue

        # Get coding language distribution API
        lang_response = requests.get(langURL, headers=HEADER)
        # Error check and skip if there is an error
        if lang_response.status_code != 200:
            print(f"Language Error: {lang_response.status_code}")
            continue

        # Work with language json object which looks like the following example:
        # {
        #     "JavaScript": 12345,
        #     "Java": 997653,
        #     "Python": 67890,
        #     "CSS": 2345
        # }
        languages = lang_response.json()
        lineTotal = sum(languages.values())

        # Convert to a percent
        javaPercent = (languages.get("Java", 0) / lineTotal) * 100

        # Add the repository name if it is large enough
        if javaPercent >  THRESHOLD:
            printedRepos.add(repo_url)
            intSampleSize -= 1
            print(f"{repo_url}")

        # Check if enough repositories have been accumulated
        if intSampleSize == 0:
            return 0
        
    # Recusivley call and return the function if not enough repositories are found
    return randomRepos(intSampleSize)
