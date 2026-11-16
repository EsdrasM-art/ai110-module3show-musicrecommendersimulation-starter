# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0**

---

## 2. Intended Use  

**Goal / Task:** VibeFinder suggests the top 5 songs from a small catalog that best fit one listener's stated taste: their favorite genre, favorite mood, how energetic they want the music to be, and whether they like acoustic or electronic sound. It also explains *why* each song was picked.

**Assumptions about the user:** it assumes the user can describe their taste with one genre, one mood and one energy number, and that this taste doesn't change. It does not know anything about what they actually listened to before.

**Intended use:** classroom exploration of how recommender systems turn data into suggestions, and a sandbox for seeing how weights create bias.

**Not intended for:** real users or a real music product. It shouldn't be used to decide which artists get promoted or paid, to judge someone's taste, or for any decision that matters. The catalog is tiny and made up, and the weights are hand-picked guesses, not learned from data.

---

## 3. How the Model Works  

**Algorithm summary (no code):** imagine a judge with a scorecard who looks at every song in the catalog one at a time.

- If the song's **genre** is the user's favorite genre, it gets **2 points**.
- If the song's **mood** is the user's favorite mood, it gets **1 point**.
- It gets **up to 1 more point** for **energy**, depending on how *close* the song's energy is to what the user wants. A perfect match gets the full point; a song at the opposite end of the scale gets nothing. Being louder isn't automatically better, being *closer* is.
- If the user said whether they like acoustic music, the song gets **up to half a point** for matching that (very acoustic songs for acoustic fans, very produced/electronic songs for everyone else).

After every song has a score, the judge **sorts** them from highest to lowest and hands back the top 5, along with the list of reasons ("genre match: pop (+2.00)", etc.).

**Changes from the starter logic:** the starter code returned nothing. I implemented CSV loading with number conversion, the scoring recipe above, sorting and top-k selection, an explanation string for every song, and case-insensitive matching so `"Jazz "` and `"jazz"` count as the same genre. I also added an "experiment" set of weights that can be switched on with a flag.

---

## 4. Data  

- **Size:** 20 songs in `data/songs.csv`. The starter had 10; I added 10 more.
- **Features per song:** genre, mood, energy (0–1), tempo in BPM, valence (0–1, how positive it sounds), danceability (0–1) and acousticness (0–1). The scoring only uses genre, mood, energy and acousticness.
- **Genres (16):** pop (3), lofi (3), and one each of rock, ambient, jazz, synthwave, indie pop, hip-hop, classical, metal, country, r&b, edm, folk, reggae and blues.
- **Moods (14):** happy, chill, intense, relaxed, moody, focused, confident, melancholic, angry, nostalgic, romantic, energetic, sad and uplifting.
- **What I added:** the 10 new songs cover genres and moods the starter data was missing entirely (e.g. no sad, angry or romantic songs existed before).
- **Limits:** the songs and numbers are invented, not real audio measurements. Most genres have only one song, so a fan of those genres gets one good match and then filler. There's nothing about lyrics, language, culture, decade, artist popularity or listening history. Musical taste that crosses labels (e.g. "sad but danceable") is hard to express.

---

## 5. Strengths  

- **Clear, specific profiles work really well.** Chill Lofi got all three lofi songs on top, with the two *chill* lofi songs at #1 and #2. Deep Intense Rock got *Storm Runner*, the only rock/intense song, with a near-perfect 4.44 out of 4.5.
- **Energy closeness behaves like a "vibe" slider.** The calm profiles only got calm songs and the intense profiles only got intense songs; there was zero overlap between Chill Lofi and Deep Intense Rock.
- **It's fully explainable.** Every point is listed, so it's easy to see exactly why a song ranked where it did.
- **Matched my intuition for the default pop/happy user.** *Sunrise City* ranked #1 because it was the only song that hit all three: pop (+2.0), happy (+1.0) and energy 0.82 vs. a 0.80 target (+0.98) = 3.98. That's the song I would have picked by hand.
- **Robust to messy input.** `"  Jazz "` and `"RELAXED"` still matched `jazz` / `relaxed`.

---

## 6. Limitations and Bias 

**Main weakness I found: genre is so heavy that it overrides everything else, which creates a filter bubble.** A genre match is worth 2 points, but a mood match is worth only 1 and energy at most 1. So a pop song with the *wrong* mood (*Gym Hero*, pop/intense) beats a non-pop song with the *right* mood and energy (*Rooftop Lights*, indie pop/happy) for a "happy pop" user. In the Conflicted test, the user asked for 0.9 energy but got a quiet 0.30-energy folk song at #1, because genre + mood (3 points) can never be beaten by energy (1 point). The system also treats "indie pop" and "pop" as totally unrelated, and a user whose favorite genre isn't in the catalog at all (k-pop) can never earn the biggest bonus. Their best score was only 2.29, compared with 4+ for users whose genre exists. In short, the system works best for users whose taste lines up with how the catalog happens to be labeled, and it quietly gives everyone else worse results without telling them.

**Other limitations:**

- **Catalog imbalance:** pop and lofi have 3 songs each, while 14 genres have just one. *Cardio Queen* shows up in 5 of the 7 test profiles and *Gym Hero* in 3, because they are high-energy, electronic, and pop.
- **Ignored features:** tempo, valence and danceability are loaded but not scored, so a "happy" user isn't steered toward high-valence songs unless the mood label literally says happy.
- **No learning or feedback:** it never finds out that you skipped a song, and it has no idea what other users like.
- **No diversity control:** nothing stops all 5 results from being the same genre or artist (Max Pulse has 2 songs in several lists).

---

## 7. Evaluation  

**How I tested it:**

1. Ran **7 profiles** with `python -m src.main`: Default Pop/Happy, High-Energy Pop, Chill Lofi and Deep Intense Rock (normal listeners), plus three adversarial ones: **Conflicted** (folk/sad but energy 0.9), **Ghost Genre** (k-pop, which isn't in the catalog) and **Middle-of-the-Road** (energy 0.5, messy capitalization, no acoustic preference).
2. Checked whether the #1 song matched what I would pick by hand, and read the reasons to see which rule was driving each result.
3. Ran a **weight-shift experiment** (genre 2.0 → 1.0, energy 1.0 → 2.0) with `--experiment` and compared the lists.
4. Wrote **8 pytest tests**: loading, numeric conversion, scoring math, energy closeness, case-insensitive labels, sorting and top-k, and the experiment.

Full terminal output for every profile is in the [README](README.md#stress-test-all-profiles).

**What surprised me:**

- *Gym Hero* (a pop workout song with an "intense" mood) keeps showing up for people who just want "Happy Pop." In plain language: the system gives a big reward just for being labeled "pop," and *Gym Hero* is pop and close in energy, so it only loses 1 point for the wrong mood. A happy non-pop song can't make up the 2-point head start. It's like a friend who only hears "you like pop" and ignores "I'm in a happy mood."
- The Conflicted profile didn't get a compromise. It got a sad, quiet song at #1 and loud, unrelated songs (rock, pop) at #3–5, so the list felt split in half.
- The k-pop user's list looked almost identical to the pop user's list, even though the system never matched their genre. Mood + energy happened to point at the same songs.
- In the experiment, the #1 song never changed for any profile. Changing the weights mostly shuffled positions 2–5.

**Profile-by-profile comparisons (what changed and why it makes sense):**

| Pair | Comment |
|---|---|
| Default Pop/Happy vs. High-Energy Pop | Nearly the same top 4. Raising energy to 0.9 and adding "not acoustic" boosts every score and swaps #5 from *Concrete Crown* (hip-hop, 0.78) to *Laser Tide* (EDM, 0.95, almost no acoustic sound). That makes sense: they asked for more energy and more electronic sound. |
| High-Energy Pop vs. Chill Lofi | No songs in common. Pop got loud, produced songs (0.76–0.95 energy); lofi got quiet, acoustic songs (0.28–0.42). The profile can clearly tell "workout" from "study" music. |
| High-Energy Pop vs. Deep Intense Rock | Both want 0.9 energy and electronic sound, so they share *Gym Hero*, *Cardio Queen* and *Laser Tide*. Only #1 differs (*Sunrise City* vs. *Storm Runner*), and the genre bonus decides it. |
| High-Energy Pop vs. Conflicted | Same energy target, but Conflicted's top 2 are quiet sad songs because folk + sad earn 3 points. Positions 3–5 drift back toward the pop list (*Storm Runner*, *Rooftop Lights*, *Cardio Queen*) because once genre and mood run out, energy is the only thing left. |
| High-Energy Pop vs. Ghost Genre | Very similar lists (*Sunrise City*, *Rooftop Lights*, *Cardio Queen*), but no genre points, so *Gym Hero* ("intense") drops out and *Concrete Crown* / *Night Drive Loop* come in on energy alone. The top score falls from 4.33 to 2.29. |
| High-Energy Pop vs. Middle-of-the-Road | No overlap. Middle gets its one jazz/relaxed song, then mid-energy songs (country, blues, r&b). That's expected for a 0.5 energy target. |
| Chill Lofi vs. Deep Intense Rock | Total opposites with zero overlap. Energy and the acoustic preference push the lists to opposite ends of the catalog, which is what should happen. |
| Chill Lofi vs. Conflicted | Both like acoustic music. Conflicted asked for 0.9 energy but got a 0.30-energy acoustic folk song at #1, which feels closer to the lofi list than to what they asked for. This shows genre + mood beating energy. |
| Chill Lofi vs. Ghost Genre | No overlap. Ghost Genre's happy + 0.7 energy + electronic preference sends it to upbeat pop, far from lofi. |
| Chill Lofi vs. Middle-of-the-Road | They share *Midnight Coding*, and *Coffee Shop Stories* is #1 for Middle and #5 for Lofi. A 0.5 energy target sits between "chill" and "upbeat", so it borrows the calmer end of the catalog. |
| Deep Intense Rock vs. Conflicted | *Storm Runner* is #1 for Rock (genre + mood + energy) but #3 for Conflicted, only because its energy is 0.91 (and it gets almost nothing for acoustic). Same song, very different reasons. |
| Deep Intense Rock vs. Ghost Genre | They share *Cardio Queen* (high energy, electronic). Rock leans "intense" (*Gym Hero*, *Iron Lung Choir*) while k-pop leans "happy" (*Sunrise City*, *Rooftop Lights*). Mood is doing its job. |
| Deep Intense Rock vs. Middle-of-the-Road | No overlap. 0.9 vs. 0.5 energy, and different genres and moods. |
| Conflicted vs. Ghost Genre | Both have a "broken" preference. Conflicted's genre exists, so it still gets a 3.85 top score; Ghost's doesn't, so it maxes out at 2.29. Users outside the catalog's labels are capped lower. |
| Conflicted vs. Middle-of-the-Road | They share *Rainy Day Ledger* (blues, sad, 0.45). For Conflicted it's there for the sad mood; for Middle it's there because 0.45 is close to 0.5. Same song, different reasons. |
| Ghost Genre vs. Middle-of-the-Road | After the first one or two picks, both lists are filler with scores around 1 that are decided almost entirely by energy. A thin match means the bottom of the list is basically "whatever is closest in energy." |

**Weight-shift experiment result:** the recommendations became *different*, not clearly *better*. Halving genre let good cross-genre matches climb (*Rooftop Lights* to #2 for pop/happy, *Spacewalk Thoughts* above *Focus Flow* for chill), which felt more accurate. But it also let a rock song into the High-Energy Pop list purely for being loud. The #1 song stayed the same for every profile. See the README's [Experiments](README.md#experiments-you-tried) section for the full table.

---

## 8. Future Work  

1. **Partial-credit similarity for labels:** give some points for related genres ("indie pop" ≈ "pop", "metal" ≈ "rock") and moods ("chill" ≈ "relaxed"), instead of all-or-nothing matches.
2. **Use more features and let users set them:** add valence, danceability and tempo closeness, and let the user say which features matter most to them (personal weights).
3. **Diversity in the top 5:** limit repeats of the same genre or artist, so a list isn't 3 Max Pulse / pop songs, and slip in one "discovery" pick outside the user's favorite genre to break the filter bubble.
4. **Warn on weak matches:** if the favorite genre isn't in the catalog or the top score is low, say so instead of quietly returning filler.

---

## 9. Personal Reflection  

**Biggest learning moment:** seeing that one number, the genre weight, decided the winner in almost every list. I went in thinking the system would balance all the features, but writing out the reasons showed me it was mostly a "genre filter with tie-breakers." Choosing weights is a design decision with consequences, not a neutral math step.

**How AI tools helped, and when I double-checked:** I used an AI coding assistant (Claude Code) to research collaborative vs. content-based filtering, expand the dataset, implement the loading/scoring/ranking functions, suggest adversarial profiles, and draft the documentation. I double-checked by running the program and reading the actual terminal output instead of trusting a description of it. Every score in this card comes from a real run. I also verified the scoring math by hand (e.g. *Sunrise City*: 2.0 + 1.0 + (1 − 0.02) = 3.98) and added pytest tests for it. One thing the assistant caught that I needed to verify was that `main.py`'s original import (`from recommender import ...`) would fail with `python -m src.main`, so it had to be fixed.

**What surprised me:** how much four features and a sort can "feel" like a real recommendation. For the normal profiles, the top pick was exactly what I'd choose, and the explanation made it feel trustworthy, even though the system has no idea what the songs actually sound like. That also made the bias feel sneakier: the confident explanation looks just as good when the recommendation is bad.

**What I'd try next:** add a tiny bit of collaborative filtering (fake "users who liked X also liked Y" data) and compare it to the content-based results, add partial genre similarity, and build a small interface where users can adjust the weights and watch the ranking change live.
