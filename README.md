# AI_MOVIE_RECOMMENDER

A practice AI project that combines **TMDB APIs** (movies + India OTT) with an **OpenAI LLM** (smart top-3 recommendations).

You pick a genre → get top-rated movies → see where they stream in India → get an AI-written top 3 with *About / Best things / Why watch*.

---

## Live demo

Watch a full run of the program:

[recording.mp4 (Google Drive)](https://drive.google.com/file/d/15IrMsTjJvOQclTbSS_r92T13aBW_Brja/view?usp=drive_link)

---

## What it does

1. Loads secrets from `.env`
2. Shows all TMDB genres as simple numbers (`ACTION - 1`, `COMEDY - 4`, …)
3. Asks how many movies you want (**1–100**)
4. Fetches **top-rated** movies for that genre from TMDB  
   (rating ≥ 7, votes ≥ 1000)
5. Shows **India OTT** availability for each movie (subscription / rent / buy)
6. Calls the **LLM once** to recommend the **top 3** from that list
7. Saves everything to `OUTPUT.md` in the current directory

---

## Architecture (simple)

```text
                    ┌──────────────┐
                    │     User     │
                    └──────┬───────┘
                           │
                 Genre + Movie Count
                           │
                           ▼
                    ┌──────────────┐
                    │     TMDB     │
                    │              │
                    │ • Genres     │
                    │ • Top Rated  │
                    │ • India OTT  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  OpenAI LLM  │
                    │              │
                    │ Top 3 Picks  │
                    │ + Reasons    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  OUTPUT.md   │
                    │              │
                    │ Final Report │
                    └──────────────┘
```

**Rule of thumb used in this project**

| Job | Who does it |
|-----|-------------|
| Facts (movies, ratings, OTT) | **TMDB API** |
| Opinion / storytelling (why watch) | **LLM** |

---

## Requirements

- Python 3.7+ (this app uses simple syntax; `.format()`, no f-strings)
- [OpenAI API key](https://platform.openai.com/)
- [TMDB API key](https://www.themoviedb.org/settings/api) (free)

---

## How to create a TMDB API key (free)

TMDB gives you movie data (genres, ratings, India OTT). The API key is free for learning projects.

1. Open [https://www.themoviedb.org/](https://www.themoviedb.org/) and **create an account** (or log in).
2. Prefer a **desktop browser** (TMDB’s API signup works better on desktop than mobile).
3. Click your **profile icon** (top right) → **Settings**.
4. In the left sidebar, open **API**.
5. If you do not have a key yet:
   - Click the link to **request an API key**
   - Choose **Developer** (fine for personal / learning use)
   - Accept the terms
   - Fill the short form (app name can be `AI_MOVIE_RECOMMENDER`; website can be your GitHub repo URL or any personal site)
6. After approval, open **Settings → API** again.
7. Copy the **API Key (v3 auth)** — this is the value this project needs for `TMDB_API_KEY`.

Put it in your `.env` file:

```env
TMDB_API_KEY=paste_your_tmdb_v3_key_here
```

**Note:** TMDB may also show an **API Read Access Token (v4)**.  
This app uses the older-style **v3 API Key**, not the v4 token.

Official help: [TMDB API Getting Started](https://developer.themoviedb.org/docs/getting-started)

---

## How to create an OpenAI API key

OpenAI gives you the LLM that writes the top-3 recommendations.

1. Open [https://platform.openai.com/](https://platform.openai.com/) and **sign up / log in**.  
   (This is the **API platform**, not the regular ChatGPT chat website.)
2. Complete email / phone verification if asked.
3. Create or select a **project** (Default project is fine for learning).
4. Go to **API keys**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
5. Click **Create new secret key**.
6. Give it a name like `movie-recommender`.
7. Click create, then **copy the key immediately** (OpenAI shows it only once).  
   It usually starts with `sk-` or `sk-proj-`.
8. Add billing / credits under **Settings → Billing** if your account requires it (API usage is paid; set a low monthly limit while learning).

Put it in your `.env` file:

```env
OPENAI_API_KEY=sk-your-key-here
MODEL_NAME=gpt-4.1-nano
```

`MODEL_NAME` is which model the app calls. You can change it later to another model available on your OpenAI account.

**Safety tips**

- Never commit `.env` to GitHub.
- Never paste your key in public chats, screenshots, or README.
- If a key leaks, revoke it on the API keys page and create a new one.

Official page: [OpenAI API keys](https://platform.openai.com/api-keys)

---

## Setup

```bash
git clone https://github.com/<your-username>/AI_MOVIE_RECOMMENDER.git
cd AI_MOVIE_RECOMMENDER

python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```env
OPENAI_API_KEY=sk-your-key-here
MODEL_NAME=gpt-4.1-nano
TMDB_API_KEY=your-tmdb-key-here
```

---

## Run

```bash
python app.py
```

Example flow:

```text
Enter genre number (example: 1 for ACTION): 1
Enter number of movies (example: 5): 10
```

Then check `OUTPUT.md` in the same folder.

---

## Project files

| File | Purpose |
|------|---------|
| `app.py` | Full application |
| `requirements.txt` | Python dependencies |
| `.env.example` | Safe template for keys |
| `.env` | Your real keys (**never commit**) |
| `OUTPUT.md` | Generated report (**gitignored**) |
| `.gitignore` | Keeps secrets / junk out of git |
| `README.md` | This guide |

---

## Notes

- India OTT data comes from TMDB watch providers. It can lag behind real apps (catalogs change often).
- The LLM only recommends from **your fetched list** — it does not invent new titles.
- Keep `.env` private. Only commit `.env.example`.
- Run the app from the project folder so `OUTPUT.md` is saved next to `app.py`.

---

## Code walkthrough (beginner-friendly)

This section is written for someone learning AI for the first time.  
You do **not** need to know advanced Python. Read it like a story of how the app thinks.

### Words you will see a lot

| Word | Simple meaning |
|------|----------------|
| **API** | A website that answers computer requests. Your code asks TMDB/OpenAI, they reply with data. |
| **API key** | Like a password that proves “this request is allowed.” Kept secret in `.env`. |
| **TMDB** | The Movie Database — real movie facts (title, rating, OTT). |
| **LLM** | Large Language Model (like ChatGPT). It reads text and writes helpful text back. |
| **Prompt** | The instructions + information you send to the LLM. |
| **System message** | Rules for the AI: “Behave like this… reply in this format…” |
| **User message** | The actual request + data for this run: genre, movie list, OTT. |
| **Function** | A small named block of code that does one job. |

### The most important idea in this project

```text
TMDB  = facts   (what movies exist, ratings, where to watch in India)
LLM   = advice  (which 3 to watch and why)
```

We do **not** ask the LLM “Where can I stream Parasite in India?”  
That kind of live catalog data is better from TMDB.  

We **do** ask the LLM: “From these real movies, pick top 3 and explain why.”  
That is judgment + writing — what LLMs are good at.

---

### Big picture: the pipeline

`main()` is the manager. It calls functions one after another:

```text
1. load_config              → read secrets from .env
2. validate_config          → make sure keys exist
3. fetch_genre_map          → get genres from TMDB
4. build_user_genre_menu    → turn TMDB ids into easy numbers 1, 2, 3...
5. display_genre_menu       → show the list on screen
6. ask_genre_choice         → user picks a genre
7. ask_movie_count          → user picks how many movies
8. fetch_top_movies_by_genre→ get top-rated movies from TMDB
9. display_top_movies       → print the movie list
10. check_ott_for_movies    → for each movie, get India OTT
11. llm_recommend_top3      → AI picks top 3 + reasons
12. save_output_md          → write OUTPUT.md
```

Think of it like a kitchen:

- TMDB brings ingredients (facts)
- LLM cooks the recommendation (story)
- `OUTPUT.md` is the finished plate you can reopen later

---

### 1) `PRINT_FUNCTION(title)`

**What it does:** Prints a nice banner in the terminal.

**Why it exists:** When you run the app, many steps happen. Banners make it easy to see:

```text
────────────────────────────────────────────────────────────
  STARTING: Loading environment variables
────────────────────────────────────────────────────────────
```

**Input:** a short title string  
**Output:** nothing returned — it only prints

This is not AI. It is just UI for humans reading the terminal.

---

### 2) `load_config()`

**What it does:** Reads your secret values from a `.env` file.

**Why `.env`?**  
API keys should never be typed into code (and never uploaded to GitHub).  
`.env` is a private file on your computer. The app loads it at start.

It uses `load_dotenv(override=True)` so values from `.env` become available as environment variables.

Then it builds a Python dictionary (like a labeled box):

```text
{
  "OPENAI_API_KEY": "...",
  "MODEL_NAME": "gpt-4.1-nano",
  "TMDB_API_KEY": "..."
}
```

**Input:** none  
**Output:** that config dictionary

---

### 3) `validate_config(config)`

**What it does:** Checks that the important values are not empty.

If OpenAI key / model name / TMDB key is missing, it prints `[ERROR]` and returns `False`.  
If all good, it prints `[OK]` for each and returns `True`.

**Why this matters:** Better to stop early with a clear message than crash later with a confusing API error.

**Input:** config dictionary  
**Output:** `True` or `False`

---

### 4) `fetch_genre_map(TMDB_API_KEY)`

**What it does:** Asks TMDB: “What movie genres do you support?”

It calls:

```text
GET https://api.themoviedb.org/3/genre/movie/list
```

TMDB replies with JSON (data structured like nested lists/dicts).  
The function converts that into a simple map:

```text
{28: "Action", 12: "Adventure", 35: "Comedy", ...}
```

Here `28` is TMDB’s official id for Action.  
Your app needs that id later when searching movies.

**Input:** TMDB API key  
**Output:** `genre_map` dictionary `{tmdb_id: name}`

---

### 5) `build_user_genre_menu(genre_map)`

**What it does:** Makes genres friendly for beginners.

People should not need to remember “Action = 28”.  
So this function creates a simple menu:

```text
1 → Action   (keeps TMDB id 28 inside)
2 → Adventure (keeps TMDB id 12 inside)
3 → ...
```

Internally each option looks like:

```text
menu[1] = {"name": "Action", "tmdb_id": 28}
```

**Input:** `genre_map` from TMDB  
**Output:** `menu` with easy numbers for humans

This is a common pattern in apps: **show simple UI, keep real IDs behind the scenes**.

---

### 6) `display_genre_menu(menu)`

**What it does:** Prints the menu on screen.

Example:

```text
ACTION - 1
ADVENTURE - 2
ANIMATION - 3
...
```

**Input:** menu  
**Output:** nothing returned — only printing

---

### 7) `ask_genre_choice(menu)`

**What it does:** Waits for you to type a number (example: `1`).

Then it checks:

1. Is it a number? (not `"abc"`)
2. Is that number in the menu?

If invalid → prints error and returns `None` (meaning “no valid choice”).  
If valid → returns the selected genre info:

```text
{"name": "Action", "tmdb_id": 28}
```

**Input:** menu  
**Output:** selected genre dict, or `None`

---

### 8) `ask_movie_count()`

**What it does:** Asks how many movies you want (1 to 100).

It validates:

- must be a number
- must be at least 1
- must be at most 100

Why max 100? Keeps the app fast and keeps LLM context smaller (you don’t send hundreds of movies to the model).

**Input:** none (reads from keyboard)  
**Output:** integer count, or `None`

---

### 9) `fetch_top_movies_by_genre(TMDB_API_KEY, tmdb_genre_id, count)`

**What it does:** Asks TMDB for high-quality movies in your genre.

It calls Discover:

```text
GET /3/discover/movie
```

Important filters (this is how we get “good” movies, not random ones):

| Filter | Meaning in plain English |
|--------|--------------------------|
| `with_genres` | Only this genre |
| `sort_by=vote_average.desc` | Highest rating first |
| `vote_average.gte=7` | Rating at least 7 |
| `vote_count.gte=1000` | At least 1000 votes (so one person cannot fake a 10/10) |

**Pagination (important beginner concept):**  
TMDB sends about **20 movies per page**.  
If you asked for 50 movies, one page is not enough.  
So the function loops: page 1, page 2, page 3… until it has enough (or TMDB runs out).

**Input:** API key, genre id, count  
**Output:** list of movie dictionaries from TMDB

This step is still **not** AI. It is data fetching.

---

### 10) `display_top_movies(movies, genre_name, count)`

**What it does:** Shows the selected movies in a readable list:

```text
1. The Dark Knight (2008) — rating 8.5
2. ...
```

It also keeps only the first `count` movies (`movies[:count]`) and returns that list for the next steps.

**Input:** raw movie list + genre name + count  
**Output:** the final selected movie list

---

### 11) `get_movie_ott_india(TMDB_API_KEY, movie_id)`

**What it does:** For **one movie**, asks TMDB: “Where can people watch this in India?”

It calls:

```text
GET /3/movie/{movie_id}/watch/providers
```

TMDB returns many countries. This app only reads India:

```python
india = results.get("IN")
```

Then it combines three kinds of platforms:

| TMDB field | Shown as | Meaning |
|------------|----------|---------|
| `flatrate` | `SUBSCRIPTION` | Included with Netflix / Prime / etc. |
| `rent` | `RENT` | Pay once to rent |
| `buy` | `BUY` | Pay to own |

Example output string:

```text
Netflix (SUBSCRIPTION), Amazon Prime Video (RENT)
```

If nothing found → `"not found"`.

**Input:** API key + one movie id  
**Output:** one text string of India OTT info

---

### 12) `check_ott_for_movies(TMDB_API_KEY, movies)`

**What it does:** Loops through **all** selected movies and calls `get_movie_ott_india` for each.

For every movie it prints:

```text
1. The Dark Knight (2008)
   Rating : 8.5
   India  : Amazon Prime Video (SUBSCRIPTION), ...
```

And builds `ott_results` — a clean list we will later:

1. send to the LLM as context
2. save into `OUTPUT.md`

Each item looks like:

```text
{
  "title": "...",
  "year": "2008",
  "rating": 8.5,
  "ott": "Netflix (SUBSCRIPTION), ..."
}
```

**Input:** API key + movie list  
**Output:** `ott_results` list

---

### 13) `build_movie_context(ott_results)`

**What it does:** Turns the movie/OTT list into plain text for the LLM.

LLMs understand text best. So instead of sending raw Python objects, we create lines like:

```text
- The Dark Knight (2008), rating 8.5, India OTT: Amazon Prime Video (SUBSCRIPTION)
- Inception (2010), rating 8.4, India OTT: ...
```

**Why this matters:** This text becomes part of the **user prompt**.  
Good context in → better answer out.

**Input:** `ott_results`  
**Output:** one multi-line string

---

### 14) `llm_recommend_top3(...)`  ← the AI step

**What it does:** Sends one chat request to OpenAI and prints the reply.

This is the heart of the “AI” part.

#### What goes into the LLM

Two messages:

1. **System message (rules)**  
   Tells the model:
   - you are a movie recommendation expert
   - pick only from the given list (do not invent titles)
   - write About / Best things / Why watch
   - use a fixed Markdown format
   - bold movie names with `**...**`

2. **User message (this run’s data)**  
   Includes:
   - selected genre
   - the movie list + ratings + India OTT
   - the request: recommend top 3

#### How the call looks (conceptually)

```text
Your app  ──messages──►  OpenAI model (MODEL_NAME)
Your app  ◄──reply────  “1. **Movie** … About: … Best things: …”
```

Code uses:

```python
OPENAI_CLIENT.chat.completions.create(
    model=MODEL_NAME,
    messages=messages,
)
```

Then it reads:

```python
reply = response.choices[0].message.content
```

That `reply` is normal text (Markdown). No magic — just generated language based on your prompt + list.

#### Why only one LLM call?

Because we already collected facts from TMDB.  
The model only needs to **rank + explain**. One good prompt is enough.

**Input:** OpenAI client, model name, ott_results, genre name  
**Output:** recommendation text (string)

---

### 15) `clean_md_text(text)`

**What it does:** Tidies the LLM reply before saving.

LLMs sometimes add trailing spaces or too many blank lines.  
This function:

- removes spaces at the end of lines
- keeps at most one blank line in a row
- removes blank lines at the very start/end

**Input:** raw LLM text  
**Output:** cleaned Markdown text

Not AI — just cleanup so `OUTPUT.md` looks neat.

---

### 16) `save_output_md(genre_name, ott_results, llm_reply)`

**What it does:** Writes a report file named `OUTPUT.md` in the current folder.

Structure:

1. **TMDB section** — every movie with rating + India OTT (facts)
2. **LLM section** — top 3 recommendations (AI advice)

Path used:

```python
os.path.join(os.getcwd(), "OUTPUT.md")
```

So it saves where you ran the command from (usually the project folder).

**Input:** genre name, ott list, LLM reply  
**Output:** file path of saved Markdown

---

### 17) `main()`

**What it does:** Runs the whole story from start to finish.

Step by step:

1. Load + validate config
2. Create OpenAI client (`OpenAI()`)
3. Fetch genres and show menu
4. Ask genre + movie count
5. Fetch movies from TMDB
6. Fetch India OTT for each movie
7. Ask LLM for top 3
8. Save `OUTPUT.md`
9. Print “DONE”

If something required fails (missing key, bad genre, no movies), it stops early with a clear error. That is intentional.

At the bottom of the file:

```python
if __name__ == "__main__":
    main()
```

means: “When someone runs `python app.py`, start `main()`.”

---

### End-to-end example (one mental movie)

```text
You type: genre 1 (Action), count 10
   │
   ▼
TMDB returns 10 top-rated Action movies
   │
   ▼
TMDB returns India OTT for each
   │
   ▼
App builds a text list and sends it to the LLM
   │
   ▼
LLM replies with top 3 + About / Best things / Why watch
   │
   ▼
Everything is saved in OUTPUT.md
```

If you remember only one sentence from this README:

> **APIs give facts. The LLM turns those facts into a helpful recommendation.**

---

## Example `OUTPUT.md` shape

```markdown
# Movie Recommender Output — Action

## TMDB response — movies and India OTT

### 1. The Dark Knight (2008)

- **Rating:** 8.5
- **India OTT:** Amazon Prime Video (SUBSCRIPTION), ...

## LLM response — top 3 recommendations

1. **The Dark Knight (2008)**

About: ...

Best things: ...

Why watch: ...
```

---

## License

Free to use for learning and practice.
