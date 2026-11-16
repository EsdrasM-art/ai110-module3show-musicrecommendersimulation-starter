import csv
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional

# ---------------------------------------------------------------------------
# Algorithm Recipe (weights)
#
#   genre match      -> +2.0 points
#   mood match       -> +1.0 point
#   energy closeness -> up to +1.0 point:  weight * (1 - |song_energy - target|)
#   acoustic fit     -> up to +0.5 point:  rewards acoustic songs if the user
#                       likes acoustic, and electronic/produced songs if not
#
# Max possible score with default weights = 4.5
# ---------------------------------------------------------------------------
DEFAULT_WEIGHTS: Dict[str, float] = {
    "genre": 2.0,
    "mood": 1.0,
    "energy": 1.0,
    "acoustic": 0.5,
}

# Experiment from Phase 4: double energy, halve genre.
EXPERIMENT_WEIGHTS: Dict[str, float] = {
    "genre": 1.0,
    "mood": 1.0,
    "energy": 2.0,
    "acoustic": 0.5,
}

NUMERIC_FIELDS = {
    "id": int,
    "energy": float,
    "tempo_bpm": float,
    "valence": float,
    "danceability": float,
    "acousticness": float,
}


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

    def to_prefs(self) -> Dict:
        """Convert this profile into the user_prefs dict used by score_song."""
        return {
            "genre": self.favorite_genre,
            "mood": self.favorite_mood,
            "energy": self.target_energy,
            "likes_acoustic": self.likes_acoustic,
        }


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song], weights: Optional[Dict[str, float]] = None):
        """Store the song catalog and the scoring weights to use."""
        self.songs = songs
        self.weights = weights or DEFAULT_WEIGHTS

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for this user, highest score first."""
        prefs = user.to_prefs()
        scored = [
            (song, score_song(prefs, asdict(song), self.weights)[0])
            for song in self.songs
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why this song got its score."""
        score, reasons = score_song(user.to_prefs(), asdict(song), self.weights)
        return f"Score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Read the songs CSV into a list of dicts, converting numeric columns to numbers."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field, cast in NUMERIC_FIELDS.items():
                if field in row and row[field] != "":
                    row[field] = cast(row[field])
            songs.append(row)
    return songs


def _norm(text) -> str:
    """Lowercase and trim a label so 'Pop ' and 'pop' count as the same genre."""
    return str(text or "").strip().lower()


def score_song(
    user_prefs: Dict, song: Dict, weights: Optional[Dict[str, float]] = None
) -> Tuple[float, List[str]]:
    """Score one song against the user's preferences; return (score, reasons)."""
    w = weights or DEFAULT_WEIGHTS
    score = 0.0
    reasons: List[str] = []

    # 1. Genre match (categorical, all-or-nothing)
    if user_prefs.get("genre") and _norm(song.get("genre")) == _norm(user_prefs["genre"]):
        score += w["genre"]
        reasons.append(f"genre match: {song['genre']} (+{w['genre']:.2f})")

    # 2. Mood match (categorical, all-or-nothing)
    if user_prefs.get("mood") and _norm(song.get("mood")) == _norm(user_prefs["mood"]):
        score += w["mood"]
        reasons.append(f"mood match: {song['mood']} (+{w['mood']:.2f})")

    # 3. Energy closeness: reward being NEAR the target, not just high or low
    if user_prefs.get("energy") is not None:
        gap = abs(float(song["energy"]) - float(user_prefs["energy"]))
        pts = w["energy"] * max(0.0, 1.0 - gap)
        score += pts
        reasons.append(
            f"energy {song['energy']:.2f} vs target {float(user_prefs['energy']):.2f} (+{pts:.2f})"
        )

    # 4. Acoustic fit (only if the user told us their preference)
    if "likes_acoustic" in user_prefs and user_prefs["likes_acoustic"] is not None:
        acoustic = float(song["acousticness"])
        fit = acoustic if user_prefs["likes_acoustic"] else 1.0 - acoustic
        pts = w["acoustic"] * fit
        score += pts
        label = "acoustic" if user_prefs["likes_acoustic"] else "produced/electronic"
        reasons.append(f"{label} fit {fit:.2f} (+{pts:.2f})")

    return round(score, 4), reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Optional[Dict[str, float]] = None,
) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort highest to lowest, and return the top k as (song, score, explanation)."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights)
        scored.append((song, score, "; ".join(reasons)))
    # sorted() returns a new list and leaves the original catalog order untouched;
    # ties are broken by title so the output is deterministic.
    return sorted(scored, key=lambda item: (-item[1], item[0]["title"]))[:k]
