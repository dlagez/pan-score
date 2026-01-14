import json
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app


class TmdbEndpointsTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.tmp_dir = os.path.join(os.path.dirname(__file__), "..", "app", "tmp")
        os.makedirs(self.tmp_dir, exist_ok=True)

    def _save_response(self, filename, endpoint, payload):
        timestamp = self._timestamp()
        name, ext = os.path.splitext(filename)
        path = os.path.join(self.tmp_dir, f"{name}_{timestamp}{ext}")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(
                {"endpoint": endpoint, "data": payload},
                handle,
                ensure_ascii=True,
                indent=2,
            )

    @staticmethod
    def _timestamp():
        return __import__("datetime").datetime.now().strftime("%Y-%y-%d_%H-%M-%S")

    def _get_and_save(self, endpoint, filename):
        resp = self.client.get(endpoint)
        self._save_response(filename, endpoint, resp.get_json())
        self.assertEqual(resp.status_code, 200, msg=resp.get_json())
        return resp.get_json()

    def test_popular_movie_default(self):
        self._get_and_save("/api/v1/tmdb/popular", "tmdb_popular_movie.json")

    def test_popular_tv_with_language(self):
        self._get_and_save(
            "/api/v1/tmdb/popular?media_type=tv&page=1&language=zh-CN",
            "tmdb_popular_tv.json",
        )

    def test_now_playing_movie_default(self):
        self._get_and_save("/api/v1/tmdb/now_playing", "tmdb_now_playing_movie.json")

    def test_now_playing_tv_with_language(self):
        self._get_and_save(
            "/api/v1/tmdb/now_playing?media_type=tv&page=1&language=zh-CN",
            "tmdb_now_playing_tv.json",
        )

    def test_trending_all_day(self):
        self._get_and_save("/api/v1/tmdb/trending", "tmdb_trending_all_day.json")

    def test_trending_tv_week(self):
        self._get_and_save(
            "/api/v1/tmdb/trending?media_type=tv&time_window=week&page=1&language=zh-CN",
            "tmdb_trending_tv_week.json",
        )

    def test_search_multi(self):
        self._get_and_save(
            "/api/v1/tmdb/search?media_type=multi&query=Rental%20Family&language=zh-CN",
            "tmdb_search_multi.json",
        )

    def test_tv_detail(self):
        self._get_and_save("/api/v1/tmdb/tv/95479?language=zh-CN", "tmdb_tv_detail.json")

    def test_tv_credits(self):
        self._get_and_save("/api/v1/tmdb/tv/95479/credits?language=zh-CN", "tmdb_tv_credits.json")

    def test_tv_videos(self):
        self._get_and_save("/api/v1/tmdb/tv/95479/videos?language=zh-CN", "tmdb_tv_videos.json")

    def test_movie_detail(self):
        self._get_and_save("/api/v1/tmdb/movie/1208348?language=zh-CN", "tmdb_movie_detail.json")

    def test_movie_credits(self):
        self._get_and_save("/api/v1/tmdb/movie/1208348/credits?language=zh-CN", "tmdb_movie_credits.json")

    def test_movie_videos(self):
        self._get_and_save("/api/v1/tmdb/movie/1208348/videos?language=zh-CN", "tmdb_movie_videos.json")

# python -m unittest test.test_tmdb_endpoints.TmdbEndpointsTest.test_movie_detail
# python -m unittest test.test_tmdb_endpoints.TmdbEndpointsTest.test_tv_detail
if __name__ == "__main__":
    unittest.main()
