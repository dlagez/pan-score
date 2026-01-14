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

    def test_popular_movie_default(self):
        endpoint = "/api/v1/tmdb/popular"
        resp = self.client.get(endpoint)
        self._save_response("tmdb_popular_movie.json", endpoint, resp.get_json())
        self.assertEqual(resp.status_code, 200, msg=resp.get_json())

    def test_popular_tv_with_language(self):
        endpoint = "/api/v1/tmdb/popular?media_type=tv&page=2&language=zh-CN"
        resp = self.client.get(endpoint)
        self._save_response("tmdb_popular_tv.json", endpoint, resp.get_json())
        self.assertEqual(resp.status_code, 200, msg=resp.get_json())

    def test_now_playing_movie_default(self):
        endpoint = "/api/v1/tmdb/now_playing"
        resp = self.client.get(endpoint)
        self._save_response("tmdb_now_playing_movie.json", endpoint, resp.get_json())
        self.assertEqual(resp.status_code, 200, msg=resp.get_json())

    def test_now_playing_tv_with_language(self):
        endpoint = "/api/v1/tmdb/now_playing?media_type=tv&page=3&language=zh-CN"
        resp = self.client.get(endpoint)
        self._save_response("tmdb_now_playing_tv.json", endpoint, resp.get_json())
        self.assertEqual(resp.status_code, 200, msg=resp.get_json())


if __name__ == "__main__":
    unittest.main()
