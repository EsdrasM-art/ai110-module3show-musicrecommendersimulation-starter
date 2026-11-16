"""
Command line runner for the Music Recommender Simulation.

Usage:
    python -m src.main                 # run every profile with the default weights
    python -m src.main --experiment    # same profiles, energy x2 and genre x0.5
    python -m src.main --profile "Chill Lofi"
"""

import argparse

try:  # works for `python -m src.main`
    from src.recommender import load_songs, recommend_songs, DEFAULT_WEIGHTS, EXPERIMENT_WEIGHTS
except ImportError:  # works for `python src/main.py`
    from recommender import load_songs, recommend_songs, DEFAULT_WEIGHTS, EXPERIMENT_WEIGHTS


# --- Taste profiles ---------------------------------------------------------
# The first three are "normal" listeners. The last three are adversarial /
# edge-case profiles designed to see if the scoring logic can be tricked.
PROFILES = {
    "Default Pop/Happy": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
    # Edge case: conflicting signals -- sad mood but wants very high energy.
    "Conflicted (sad but 0.9 energy)": {"genre": "folk", "mood": "sad", "energy": 0.9, "likes_acoustic": True},
    # Edge case: a genre that does not exist in the catalog.
    "Ghost Genre (k-pop)": {"genre": "k-pop", "mood": "happy", "energy": 0.7, "likes_acoustic": False},
    # Edge case: dead-center energy, mixed-case labels, no acoustic preference.
    "Middle-of-the-Road": {"genre": "  Jazz ", "mood": "RELAXED", "energy": 0.5},
}


def format_prefs(prefs: dict) -> str:
    """Render a preference dict as a short one-line summary."""
    return ", ".join(f"{key}={value!r}" for key, value in prefs.items())


def print_recommendations(name: str, prefs: dict, songs: list, k: int, weights: dict) -> None:
    """Print a ranked, explained list of the top k songs for one profile."""
    print("=" * 72)
    print(f"Profile: {name}")
    print(f"Prefs:   {format_prefs(prefs)}")
    print("-" * 72)
    for rank, (song, score, explanation) in enumerate(recommend_songs(prefs, songs, k, weights), 1):
        print(f"{rank}. {song['title']} - {song['artist']}  [{song['genre']}, {song['mood']}]")
        print(f"   Score: {score:.2f}")
        for reason in explanation.split("; "):
            print(f"     * {reason}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--experiment", action="store_true", help="use EXPERIMENT_WEIGHTS (energy x2, genre x0.5)")
    parser.add_argument("--profile", help="run only the named profile")
    parser.add_argument("-k", type=int, default=5, help="number of recommendations per profile")
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    weights = EXPERIMENT_WEIGHTS if args.experiment else DEFAULT_WEIGHTS
    print(f"Weights: {weights}\n")

    profiles = PROFILES
    if args.profile:
        profiles = {args.profile: PROFILES[args.profile]}

    for name, prefs in profiles.items():
        print_recommendations(name, prefs, songs, args.k, weights)


if __name__ == "__main__":
    main()
