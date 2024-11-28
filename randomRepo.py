import requests

# API token for API requests to GitHub
GIT_API_TOKEN = ""

# Header parameter with API token
HEADER = {
    "Authorization": f"token {GIT_API_TOKEN}"
} if GIT_API_TOKEN else {}

# URL for making api requests for repositories
BASE_URL = "https://repo.maven.apache.org/maven2"

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
                artifact_url = f"{BASE_URL}/{group_path}/{artifact}/{version}/{artifact}-{version}.jar"
                pom_url = f"{BASE_URL}/{group_path}/{artifact}/{version}/{artifact}-{version}.pom"

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
