import requests

# API token for API requests to GitHub
GIT_API_TOKEN = ""

# Header parameter with API token
HEADER = {
    "Authorization": f"token {GIT_API_TOKEN}"
} if GIT_API_TOKEN else {}

# URL for making api requests for repositories
BASE_URL = "https://api.github.com/search/repositories"

MAVEN_BASE_URL = "https://search.maven.org/solrsearch/select"

# Language for search results
LANG = "language:Java filename:pom.xml"

# Search criteria for Maven projects
MAVEN = "filename:pom.xml"

# Percentage threshold for the desired lanaguage
THRESHOLD = 50


def randomReposInit(sampleSize):
    # Parameters for the search query
    params = {
        "q": 'spring',  # Query string to search for in Maven Central
        "rows": sampleSize,  # Number of results to return
        "start": 0,  # Pagination: starting index for the results
        "wt": "json"  # Response format (JSON)
    }

    # Send GET request to Maven Central search API
    response = requests.get(MAVEN_BASE_URL, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        try:
            data = response.json()  # Try parsing the JSON
            artifacts = []
            for doc in data["response"]["docs"]:
                group = doc.get("g", "unknown")
                artifact = doc.get("a", "unknown")
                version = doc.get("latestVersion", "unknown")

                # Construct URLs for the artifact and the POM manually
                group_path = group.replace('.', '/')
                artifact_url = f"{MAVEN_BASE_URL}/{group_path}/{artifact}/{version}/{artifact}-{version}.jar"
                pom_url = f"{MAVEN_BASE_URL}/{group_path}/{artifact}/{version}/{artifact}-{version}.pom"

                artifact_data = {
                    "g": group,
                    "a": artifact,
                    "latestVersion": version,
                    "url": artifact_url,
                    "pom": pom_url
                }
                artifacts.append(artifact_data)

            return artifacts
        except ValueError as e:
            print(f"Error parsing JSON: {e}")
            return []
    else:
        print(f"Error: {response.status_code}")
        return []

# def randomReposInit(sampleSize):
#     printedRepos = set()
#     randomRepos(sampleSize, printedRepos)

# # Function for developing a random sample of github repositories with at least 75% Java composition
# def randomRepos(sampleSize, printedRepos):

#     # Make sure sampleSize is an integer
#     intSampleSize = int(sampleSize)

#     page = random.randint(1, 10) # Randomize the starting page
    
#     # Develop Git query parameters
#     searchParam = {
#         "q": LANG,  # Search query
#         "page": 1,  # Pagination: which page of results
#         "per_page": 30,  # Number of results per page
#         "sort": "stars",  # Sort by stars
#         "order": "desc"  # Order results in descending order
#     }

#     # Make response call
#     response = requests.get(BASE_URL, headers=HEADER, params=searchParam)
#     # Resposne error check
#     if response.status_code != 200:
#         print(f"Error: {response.status_code}, {response.json()}")
#         return []
    
#     print(f"Remaining requests: {response.headers['X-RateLimit-Remaining']}") # Debugging
    
#     # Initialize array for coding language checking
#     searchResponseRepositories = response.json().get("items", [])

#     # Go through and check for proper parameter meeting
#     for repo in searchResponseRepositories:
#         # # Save details for later commands
#         repo_url = repo["html_url"]
#         # langURL = repo["languages_url"]

#         # # Skip already printed repositories
#         # if repo_url in printedRepos:
#         #     continue

#         # # Get coding language distribution API
#         # lang_response = requests.get(langURL, headers=HEADER)
#         # # Error check and skip if there is an error
#         # if lang_response.status_code != 200:
#         #     print(f"Language Error: {lang_response.status_code}")
#         #     continue

#         # # Work with language json object which looks like the following example:
#         # # {
#         # #     "JavaScript": 12345,
#         # #     "Java": 997653,
#         # #     "Python": 67890,
#         # #     "CSS": 2345
#         # # }
#         # languages = lang_response.json()
#         # lineTotal = sum(languages.values())

#         # # Divide by zero check
#         # if lineTotal == 0:
#         #     continue

#         # # Convert to a percent
#         # javaPercent = (languages.get("Java", 0) / lineTotal) * 100

#         # # Add the repository name if it is large enough
#         # if javaPercent >  THRESHOLD:
#         #     printedRepos.add(repo_url)
#         #     intSampleSize -= 1
#         #     print(f"{repo_url}")

#         # Check if enough repositories have been accumulated

#         printedRepos.add(repo_url)
#         intSampleSize -= 1
#         print(f"{repo_url}")

#         if intSampleSize == 0:
#             return 0
        
#     # Recusivley call and return the function if not enough repositories are found
#     return randomRepos(intSampleSize, printedRepos)