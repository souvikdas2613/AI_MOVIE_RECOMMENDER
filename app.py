# Movie Recommender — TMDB movies + India OTT, then LLM top 3 recommendations

import os
import requests
from textwrap import dedent
from dotenv import load_dotenv
from openai import OpenAI

TMDB_BASE_URL = "https://api.themoviedb.org/3"


def PRINT_FUNCTION(title):
    print("\n" + ("─" * 60))
    print("  {}".format(title))
    print(("─" * 60) + "\n")


def load_config():
    PRINT_FUNCTION("STARTING: Loading environment variables")
    print("Reading values from .env file...")
    load_dotenv(override=True)
    print("[OK] Environment variables loaded.")
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "MODEL_NAME": os.getenv("MODEL_NAME"),
        "TMDB_API_KEY": os.getenv("TMDB_API_KEY"),
    }


def validate_config(config):
    PRINT_FUNCTION("STARTING: Validating configuration")
    print("Checking API keys and model name...")
    ok = True

    if not config["OPENAI_API_KEY"]:
        print("[ERROR] OPENAI_API_KEY not found. Check your .env file.")
        ok = False
    else:
        print("[OK] OPENAI_API_KEY loaded.")

    if not config["MODEL_NAME"]:
        print("[ERROR] MODEL_NAME not found. Check your .env file.")
        ok = False
    else:
        print("[OK] MODEL_NAME set to: {}".format(config["MODEL_NAME"]))

    if not config["TMDB_API_KEY"]:
        print("[ERROR] TMDB_API_KEY not found. Check your .env file.")
        ok = False
    else:
        print("[OK] TMDB_API_KEY loaded.")

    return ok


def fetch_genre_map(TMDB_API_KEY):
    """Fetch TMDB genres. Returns {tmdb_id: name}."""
    PRINT_FUNCTION("STARTING: Fetching genre list from TMDB")
    print("Calling TMDB /genre/movie/list ...")
    url = "{}/genre/movie/list".format(TMDB_BASE_URL)
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    genres = response.json().get("genres", [])
    genre_map = {}
    for g in genres:
        genre_map[g["id"]] = g["name"]
    print("[OK] Loaded {} genres.".format(len(genre_map)))
    return genre_map


def build_user_genre_menu(genre_map):
    """
    Build a simple menu for the user.
    Example: 1 -> Action (TMDB 28), 2 -> Adventure (TMDB 12), ...
    """
    PRINT_FUNCTION("STARTING: Building user genre menu")
    print("Mapping simple numbers (1, 2, 3...) to TMDB genre ids...")

    menu = {}
    choice = 1

    for tmdb_id in genre_map:
        name = genre_map[tmdb_id]
        menu[choice] = {
            "name": name,
            "tmdb_id": tmdb_id,
        }
        choice = choice + 1

    print("[OK] Menu ready with {} options.".format(len(menu)))
    return menu


def display_genre_menu(menu):
    PRINT_FUNCTION("STARTING: Showing genre menu to user")
    print("Please pick a number from the list below:\n")
    for choice, info in menu.items():
        print("{} - {}".format(info["name"].upper(), choice))
    print()


def ask_genre_choice(menu):
    """Ask user for a number. Returns selected genre info or None."""
    PRINT_FUNCTION("STARTING: Waiting for user genre choice")
    print("Type a number and press Enter.")
    raw = input("Enter genre number (example: 1 for ACTION): ").strip()

    if not raw.isdigit():
        print("[ERROR] Please enter a number.")
        return None

    choice = int(raw)
    if choice not in menu:
        print("[ERROR] Invalid choice. Pick a number from the list.")
        return None

    selected_genre = menu[choice]
    print(
        "[OK] You selected {} = {} (TMDB id {})".format(
            choice,
            selected_genre["name"].upper(),
            selected_genre["tmdb_id"],
        )
    )
    return selected_genre


def ask_movie_count():
    """Ask user how many movies to show (1 to 100). Returns a number or None."""
    PRINT_FUNCTION("STARTING: Waiting for movie count")
    print("How many movies do you want to see?")
    print("You can ask for 1 to 100 movies (maximum 100).")
    raw = input("Enter number of movies (example: 5): ").strip()

    if not raw.isdigit():
        print("[ERROR] Please enter a number.")
        return None

    count = int(raw)
    if count < 1:
        print("[ERROR] Please enter a number greater than 0.")
        return None

    if count > 100:
        print("[ERROR] Maximum is 100 movies. Please enter 100 or less.")
        return None

    print("[OK] You want {} movie(s).".format(count))
    return count


def fetch_top_movies_by_genre(TMDB_API_KEY, tmdb_genre_id, count):
    """Fetch movies for a TMDB genre id until we have 'count' movies (max 100)."""
    PRINT_FUNCTION(
        "STARTING: Fetching top {} movies for selected genre".format(count)
    )

    if count > 100:
        count = 100
        print("[WARN] Count was above 100. Using maximum 100.")

    print("Calling TMDB /discover/movie for genre id {} ...".format(tmdb_genre_id))
    print("\nSorting by vote_average (top rated).")
    print("\nFilters: rating >= 7 and votes >= 1000.")
    print("\nNeed {} movie(s). Will fetch more pages if required.".format(count))

    url = "{}/discover/movie".format(TMDB_BASE_URL)
    movies = []
    page = 1

    while len(movies) < count:
        params = {
            "api_key": TMDB_API_KEY,
            "with_genres": tmdb_genre_id,
            "sort_by": "vote_average.desc",
            "vote_average.gte": 7,
            "vote_count.gte": 1000,
            "page": page,
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])
        if not results:
            print("[WARN] No more movies on this page.")
            break

        for movie in results:
            movies.append(movie)
            if len(movies) >= count:
                break

        total_pages = data.get("total_pages", page)
        print(
            "\n[OK] Collected {} movie(s) so far (page {}/{}).".format(
                len(movies), page, total_pages
            )
        )

        if page >= total_pages:
            print("\n[WARN] Reached last TMDB page for this genre.")
            break

        page = page + 1

    print("\n[OK] Retrieved {} movies in total.".format(len(movies)))
    return movies


def display_top_movies(movies, genre_name, count):
    PRINT_FUNCTION(
        "STARTING: Showing top {} {} movies".format(count, genre_name.upper())
    )
    print("Preparing movie list...\n")

    selected_movies = movies[:count]
    i = 1
    for movie in selected_movies:
        title = movie.get("title", "Unknown")
        rating = movie.get("vote_average", "N/A")
        year = (movie.get("release_date") or "N/A")[:4]
        print("{}. {} ({}) — rating {}".format(i, title, year, rating))
        i = i + 1

    if len(selected_movies) < count:
        print(
            "\n[WARN] Only {} movie(s) available from TMDB.".format(
                len(selected_movies)
            )
        )

    print("\n[OK] Movie list displayed.")
    return selected_movies


def get_movie_ott_india(TMDB_API_KEY, movie_id):
    """Fetch OTT platforms for one movie in India from TMDB."""
    url = "{}/movie/{}/watch/providers".format(TMDB_BASE_URL, movie_id)
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    results = data.get("results", {})
    india = results.get("IN")

    if not india:
        return "not found"

    parts = []

    flatrate = india.get("flatrate", [])
    for item in flatrate:
        parts.append("{} (SUBSCRIPTION)".format(item.get("provider_name")))

    rent = india.get("rent", [])
    for item in rent:
        parts.append("{} (RENT)".format(item.get("provider_name")))

    buy = india.get("buy", [])
    for item in buy:
        parts.append("{} (BUY)".format(item.get("provider_name")))

    if not parts:
        return "not found"

    return ", ".join(parts)


def check_ott_for_movies(TMDB_API_KEY, movies):
    """Print OTT availability in India using TMDB. Returns list for LLM context."""
    PRINT_FUNCTION("STARTING: OTT availability in India")

    ott_results = []
    i = 1
    for movie in movies:
        title = movie.get("title", "Unknown")
        year = (movie.get("release_date") or "N/A")[:4]
        rating = movie.get("vote_average", "N/A")
        movie_id = movie.get("id")

        if not movie_id:
            ott_info = "not found"
        else:
            ott_info = get_movie_ott_india(TMDB_API_KEY, movie_id)

        print("{}. {} ({})".format(i, title, year))
        print("   Rating : {}".format(rating))
        print("   India  : {}".format(ott_info))
        print()

        ott_results.append(
            {
                "title": title,
                "year": year,
                "rating": rating,
                "ott": ott_info,
            }
        )
        i = i + 1

    print("[OK] OTT list ready.")
    return ott_results


def build_movie_context(ott_results):
    """Make a plain text summary of selected movies for LLM prompts."""
    lines = []
    for item in ott_results:
        lines.append(
            "- {} ({}), rating {}, India OTT: {}".format(
                item["title"],
                item["year"],
                item["rating"],
                item["ott"],
            )
        )
    return "\n".join(lines)


def llm_recommend_top3(OPENAI_CLIENT, MODEL_NAME, ott_results, genre_name):
    """Ask LLM to recommend top 3 movies from the list and explain why."""
    PRINT_FUNCTION("STARTING: AI top 3 recommendations")

    context = build_movie_context(ott_results)

    messages = [
        {
            "role": "system",
            "content": dedent("""
                You are a passionate movie recommendation expert.
                From the given movie list only, pick the top 3 to watch.
                Also consider India OTT availability when useful.
                Do not invent movies outside the list.

                For each movie, write a short but useful recommendation:
                - what the movie is about (1-2 lines, no big spoilers)
                - the best things about it (story, acting, visuals, music, emotion, etc.)
                - why the user should watch it now

                Reply in this exact Markdown format only:

                1. **Movie Name (Year)**

                About: short spoiler-free overview.

                Best things: 2-3 standout points.

                Why watch: one clear reason.

                2. **Movie Name (Year)**

                About: short spoiler-free overview.

                Best things: 2-3 standout points.

                Why watch: one clear reason.

                3. **Movie Name (Year)**

                About: short spoiler-free overview.

                Best things: 2-3 standout points.

                Why watch: one clear reason.

                Put the movie name in bold using ** like shown.
                Use exactly one blank line between each block.
                Do not add extra spaces at the end of lines.
            """).strip(),
        },
        {
            "role": "user",
            "content": dedent("""
                Genre: {genre_name}

                My movie list with ratings and India OTT:
                {context}

                From this list only, recommend the top 3 movies I should watch.
                For each one, tell me a bit about the movie, the best things in it,
                and why I should watch it. Keep it engaging and spoiler-free.
            """).format(genre_name=genre_name, context=context).strip(),
        },
    ]

    response = OPENAI_CLIENT.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
    )
    reply = response.choices[0].message.content
    print(reply)
    return reply


def clean_md_text(text):
    """Make spacing consistent in Markdown text."""
    if not text:
        return ""

    lines = []
    for line in text.splitlines():
        lines.append(line.rstrip())

    cleaned = []
    blank_count = 0
    for line in lines:
        if line == "":
            blank_count = blank_count + 1
            if blank_count <= 1:
                cleaned.append("")
        else:
            blank_count = 0
            cleaned.append(line)

    while len(cleaned) > 0 and cleaned[0] == "":
        cleaned.pop(0)
    while len(cleaned) > 0 and cleaned[-1] == "":
        cleaned.pop()

    return "\n".join(cleaned)


def save_output_md(genre_name, ott_results, llm_reply):
    """Save TMDB OTT list and LLM recommendations to a Markdown file."""
    PRINT_FUNCTION("STARTING: Saving output Markdown file")

    lines = []
    lines.append("# Movie Recommender Output — {}".format(genre_name))
    lines.append("")
    lines.append("## TMDB response — movies and India OTT")
    lines.append("")

    i = 1
    for item in ott_results:
        lines.append("### {}. {} ({})".format(i, item["title"], item["year"]))
        lines.append("")
        lines.append("- **Rating:** {}".format(item["rating"]))
        lines.append("- **India OTT:** {}".format(item["ott"]))
        lines.append("")
        i = i + 1

    lines.append("## LLM response — top 3 recommendations")
    lines.append("")

    if llm_reply:
        lines.append(clean_md_text(llm_reply))
    else:
        lines.append("_No LLM response_")

    lines.append("")

    content = "\n".join(lines)
    output_path = os.path.join(os.getcwd(), "OUTPUT.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("[OK] Saved output to: {}".format(output_path))
    return output_path


def main():
    PRINT_FUNCTION("STARTING: Movie Recommender App")
    print("Welcome! TMDB for movies/OTT, then AI picks top 3 with reasons.\n")

    config = load_config()
    if not validate_config(config):
        print("[ERROR] Configuration failed. Stopping app.")
        return

    TMDB_API_KEY = config["TMDB_API_KEY"]
    MODEL_NAME = config["MODEL_NAME"]

    OPENAI_CLIENT = OpenAI()

    genre_map = fetch_genre_map(TMDB_API_KEY)
    menu = build_user_genre_menu(genre_map)
    display_genre_menu(menu)

    selected_genre = ask_genre_choice(menu)
    if not selected_genre:
        print("[ERROR] No valid genre selected. Stopping app.")
        return

    count = ask_movie_count()
    if not count:
        print("[ERROR] No valid movie count. Stopping app.")
        return

    movies = fetch_top_movies_by_genre(TMDB_API_KEY, selected_genre["tmdb_id"], count)
    if not movies:
        print("[ERROR] No movies found for this genre.")
        return

    selected_movies = display_top_movies(movies, selected_genre["name"], count)
    ott_results = check_ott_for_movies(TMDB_API_KEY, selected_movies)

    llm_reply = llm_recommend_top3(
        OPENAI_CLIENT, MODEL_NAME, ott_results, selected_genre["name"]
    )
    save_output_md(selected_genre["name"], ott_results, llm_reply)

    PRINT_FUNCTION("DONE: Movie Recommender finished")


if __name__ == "__main__":
    main()
