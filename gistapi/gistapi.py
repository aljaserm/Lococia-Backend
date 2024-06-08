import logging
import re

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)


@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


def gists_for_user(username: str, page: int = 1, per_page: int = 30):
    """Provides the list of gist metadata for a given user.

    This abstracts the /users/:username/gist endpoint from the Github API.
    See https://developer.github.com/v3/gists/#list-a-users-gists for
    more information.

    Args:
        username (string): the user to query gists for
        page (int): the page number to retrieve
        per_page (int): the number of gists per page

    Returns:
        The dict parsed from the json response from the Github API.  See
        the above URL for details of the expected structure.
    """
    gists_url = f"https://api.github.com/users/{username}/gists"
    params = {"page": page, "per_page": per_page}
    response = requests.get(gists_url, params=params, timeout=10)
    if response.status_code != 200:
        logging.error(
            f"Error fetching gists for user {username}: {response.status_code}"
        )
        return None
    return response.json()


def fetch_file_content(url):
    """Fetches the content of a file from a URL, handling large files by streaming.

    Args:
        url (str): The URL to fetch the file content from.

    Returns:
        str: The content of the file as a string.
    """
    try:
        with requests.get(url, stream=True, timeout=10) as r:
            r.raise_for_status()
            content = []
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    content.append(chunk.decode())
            return "".join(content)
    except requests.RequestException as e:
        logging.error(f"Error fetching file content from {url}: {e}")
        return None


@app.route("/api/v1/search", methods=["POST"])
def search():
    """Provides matches for a single pattern across a single user's gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json. The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    post_data = request.get_json()

    username = post_data.get("username")
    pattern = post_data.get("pattern")
    page = post_data.get("page", 1)
    per_page = post_data.get("per_page", 30)

    if not username or not pattern:
        return jsonify({"error": "username and pattern are required"}), 400

    try:
        regex = re.compile(pattern)
    except re.error:
        return jsonify({"error": "Invalid regex pattern"}), 400

    gists = gists_for_user(username, page, per_page)
    if gists is None:
        return jsonify({"error": "Error fetching gists from GitHub"}), 500

    matches = []

    for gist in gists:
        for file in gist["files"].values():
            raw_url = file["raw_url"]
            content = fetch_file_content(raw_url)
            if content and regex.search(content):
                matches.append(
                    {
                        "gist_id": gist["id"],
                        "file_name": file["filename"],
                        "url": gist["html_url"],
                    }
                )

    result = {
        "status": "success",
        "username": username,
        "pattern": pattern,
        "page": page,
        "per_page": per_page,
        "matches": matches,
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9876)

