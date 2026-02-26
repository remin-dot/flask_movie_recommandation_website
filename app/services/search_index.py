"""In-memory search index for language-aware queries."""

from sqlalchemy.orm import joinedload
from app.models import Movie
from app.i18n import SUPPORTED_LANGUAGES, localize_text


class SearchIndex:
    """Cache searchable text to speed up multi-language queries."""

    def __init__(self):
        self._items = []
        self._last_count = 0

    def invalidate(self):
        """Clear cached items so they rebuild on next search."""
        self._items = []
        self._last_count = 0

    def _build(self):
        movies = Movie.query.options(joinedload(Movie.genres)).all()
        items = []

        for movie in movies:
            title_display = movie.title or ''
            title = title_display.lower()
            genres = ' '.join((genre.name or '').lower() for genre in movie.genres)
            descriptions = {}

            for lang in SUPPORTED_LANGUAGES:
                descriptions[lang] = (localize_text(movie.description, lang=lang) or '').lower()

            items.append({
                'id': movie.id,
                'title': title,
                'title_display': title_display,
                'genres': genres,
                'descriptions': descriptions,
                'year': movie.year,
            })

        self._items = items
        self._last_count = len(items)

    def _ensure_fresh(self):
        if not self._items or Movie.query.count() != self._last_count:
            self._build()

    def search_ids(self, query, lang):
        self._ensure_fresh()
        search_term = query.lower()
        matched = []

        for item in self._items:
            if search_term in item['title']:
                matched.append(item['id'])
                continue
            if search_term in item['genres']:
                matched.append(item['id'])
                continue
            if search_term in item['descriptions'].get(lang, ''):
                matched.append(item['id'])

        return matched

    def suggest(self, query, lang, limit=8):
        self._ensure_fresh()
        search_term = query.lower()
        results = []
        seen = set()

        for item in self._items:
            if search_term in item['title'] or search_term in item['genres']:
                title_key = item['title']
            elif search_term in item['descriptions'].get(lang, ''):
                title_key = item['title']
            else:
                continue

            if title_key in seen:
                continue
            seen.add(title_key)

            results.append({
                'title': item['title_display'],
                'year': item['year'],
                'id': item['id'],
            })

            if len(results) >= limit:
                break

        return results


search_index = SearchIndex()
