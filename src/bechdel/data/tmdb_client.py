"""TMDB client with caching, exponential backoff, DNS fallbacks, and character gender resolution."""

import json
import logging
import os
from pathlib import Path
import socket
import time
from typing import Any, Dict, Optional
import urllib.request
import urllib.parse
import urllib.error

logger = logging.getLogger(__name__)

# DNS sinkhole resolution for Indian ISP blocks (e.g., Reliance Jio)
_orig_getaddrinfo = socket.getaddrinfo


def _safe_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host == "api.themoviedb.org":
        try:
            res = _orig_getaddrinfo(host, port, family, type, proto, flags)
            # Check if resolved to Reliance Jio ISP sinkhole
            if any(r[4][0].startswith("49.44.") for r in res if len(r) > 4 and isinstance(r[4], tuple)):
                return _orig_getaddrinfo("3.175.86.37", port, family, type, proto, flags)
            return res
        except Exception:
            return _orig_getaddrinfo("3.175.86.37", port, family, type, proto, flags)
    return _orig_getaddrinfo(host, port, family, type, proto, flags)


socket.getaddrinfo = _safe_getaddrinfo


class TMDBClient:
    """Client for fetching supplementary movie metadata and cast gender from TMDB."""

    def __init__(self, cache_dir: str = "data/raw/tmdb_cache"):
        self.api_key = os.getenv("TMDB_API_KEY", "").strip()
        self.read_token = os.getenv("TMDB_READ_TOKEN", "").strip()

        # Load from .env if missing from environment
        if not self.api_key:
            for candidate in [Path(".env"), Path.home() / ".env"]:
                if candidate.exists():
                    try:
                        with open(candidate, "r", encoding="utf-8") as f:
                            for line in f:
                                line = line.strip()
                                if line.startswith("TMDB_API_KEY=") and not line.startswith("#"):
                                    self.api_key = line.split("=", 1)[1].strip().strip("'\"")
                                elif line.startswith("TMDB_READ_TOKEN=") and not line.startswith("#"):
                                    self.read_token = line.split("=", 1)[1].strip().strip("'\"")
                    except Exception:
                        pass

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.is_available = bool(self.api_key or self.read_token)

        if not self.is_available:
            logger.info("TMDB_API_KEY not set. TMDB enrichment will be skipped gracefully.")
        else:
            logger.info("TMDB credentials detected. TMDB client active.")

    def _get_json(self, url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Fetch JSON with retry and exponential backoff."""
        delay = 0.5
        headers = {
            "User-Agent": "BechdelDetector/1.0",
            "Accept": "application/json"
        }
        if self.read_token:
            headers["Authorization"] = f"Bearer {self.read_token}"

        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=8) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code == 429:  # Rate limited
                    retry_after = float(e.headers.get("Retry-After", delay * 2))
                    time.sleep(retry_after)
                elif e.code == 404:
                    return None
                else:
                    time.sleep(delay)
            except Exception:
                time.sleep(delay)
            delay *= 2
        return None

    def get_movie_metadata(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Fetch metadata and credits for a movie by IMDb ID."""
        if not self.is_available or not imdb_id:
            return None

        # Format IMDb ID (ensure 'tt' prefix)
        clean_imdb = imdb_id if imdb_id.startswith("tt") else f"tt{imdb_id.zfill(7)}"
        cache_file = self.cache_dir / f"{clean_imdb}.json"

        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # 1. Find TMDB ID from IMDb ID
        find_url = (
            f"https://api.themoviedb.org/3/find/{clean_imdb}"
            f"?api_key={self.api_key}&external_source=imdb_id"
        )
        find_res = self._get_json(find_url)
        if not find_res or not find_res.get("movie_results"):
            return None

        tmdb_movie = find_res["movie_results"][0]
        tmdb_id = tmdb_movie.get("id")
        if not tmdb_id:
            return None

        # 2. Get full details including credits
        details_url = (
            f"https://api.themoviedb.org/3/movie/{tmdb_id}"
            f"?api_key={self.api_key}&append_to_response=credits"
        )
        details = self._get_json(details_url)
        if not details:
            return None

        # Parse relevant features
        credits_data = details.get("credits", {})
        cast = credits_data.get("cast", [])
        crew = credits_data.get("crew", [])

        # Gender: 1=female, 2=male, 0/3=unknown/non-binary
        female_cast = sum(1 for c in cast if c.get("gender") == 1)
        male_cast = sum(1 for c in cast if c.get("gender") == 2)
        total_gendered_cast = female_cast + male_cast
        female_cast_share = (female_cast / total_gendered_cast) if total_gendered_cast > 0 else 0.0

        directors = [c for c in crew if c.get("job") == "Director"]
        female_directors = sum(1 for d in directors if d.get("gender") == 1)
        director_female_presence = 1 if female_directors > 0 else 0

        writers = [c for c in crew if c.get("job") in ["Writer", "Screenplay"]]
        female_writers = sum(1 for w in writers if w.get("gender") == 1)
        writer_female_share = (female_writers / len(writers)) if writers else 0.0

        genres = [g.get("name") for g in details.get("genres", [])]

        # Character to gender mapping for filling unknown characters
        char_gender_map = {}
        for c in cast:
            g = "f" if c.get("gender") == 1 else ("m" if c.get("gender") == 2 else None)
            char_name = str(c.get("character", "")).lower().strip()
            actor_name = str(c.get("name", "")).lower().strip()
            if g and char_name:
                char_gender_map[char_name] = g
                first_tok = char_name.split()[0]
                if len(first_tok) > 2:
                    char_gender_map[first_tok] = g
            if g and actor_name:
                char_gender_map[actor_name] = g

        parsed = {
            "tmdb_id": tmdb_id,
            "imdb_id": clean_imdb,
            "runtime": details.get("runtime"),
            "budget": details.get("budget"),
            "revenue": details.get("revenue"),
            "original_language": details.get("original_language"),
            "genres": genres,
            "female_cast_share": female_cast_share,
            "director_female_presence": director_female_presence,
            "writer_female_share": writer_female_share,
            "female_cast_count": female_cast,
            "male_cast_count": male_cast,
            "char_gender_map": char_gender_map,
        }

        # Cache response
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(parsed, f)
        except Exception as e:
            logger.warning(f"Could not cache TMDB response for {clean_imdb}: {e}")

        # Rate-limit throttle
        time.sleep(0.02)
        return parsed

    def prefetch_movies(self, imdb_ids: list, max_workers: int = 8) -> None:
        """Prefetch and cache movie metadata concurrently."""
        if not self.is_available or not imdb_ids:
            return

        from concurrent.futures import ThreadPoolExecutor

        uncached = []
        for imdb in imdb_ids:
            if not imdb:
                continue
            clean_imdb = str(imdb) if str(imdb).startswith("tt") else f"tt{str(imdb).zfill(7)}"
            cache_file = self.cache_dir / f"{clean_imdb}.json"
            if not cache_file.exists():
                uncached.append(imdb)

        if not uncached:
            logger.info("All requested TMDB movies already cached locally.")
            return

        logger.info(f"Prefetching {len(uncached)} movies from TMDB ({max_workers} threads)...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(self.get_movie_metadata, uncached))
        logger.info("TMDB prefetch completed successfully.")
