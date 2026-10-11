import unittest
from app import app

class TestBooksAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_openapi_json(self):
        res = self.client.get("/openapi.json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("openapi", data)
        self.assertEqual(data["openapi"], "3.0.3")
        self.assertIn("/books", data["paths"])
        self.assertIn("/books/{bookId}", data["paths"])

    def test_swagger_ui_docs(self):
        res = self.client.get("/docs")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers["Content-Type"])
        self.assertIn("swagger-ui", res.get_data(as_text=True))

    def test_list_books_default(self):
        res = self.client.get("/v1/books")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertGreaterEqual(data["total"], 4)

    def test_list_books_filtering(self):
        res = self.client.get("/v1/books?genre=Technology&isAvailable=true")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        for item in data["items"]:
            self.assertEqual(item["genre"], "Technology")
            self.assertTrue(item["isAvailable"])

    def test_create_and_get_book(self):
        payload = {
            "title": "Refactoring: Improving the Design of Existing Code",
            "author": "Martin Fowler",
            "isbn": "9780134757599",
            "genre": "Technology",
            "price": 47.99,
            "publishedDate": "2018-11-20",
            "isAvailable": True
        }
        create_res = self.client.post("/v1/books", json=payload)
        self.assertEqual(create_res.status_code, 201)
        created_book = create_res.get_json()
        book_id = created_book["id"]
        self.assertIn("Location", create_res.headers)
        self.assertEqual(create_res.headers["Location"], f"/v1/books/{book_id}")

        # Get by ID
        get_res = self.client.get(f"/v1/books/{book_id}")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.get_json()["title"], payload["title"])

        # Patch book
        patch_res = self.client.patch(f"/v1/books/{book_id}", json={"price": 39.50, "isAvailable": False})
        self.assertEqual(patch_res.status_code, 200)
        self.assertEqual(patch_res.get_json()["price"], 39.50)
        self.assertFalse(patch_res.get_json()["isAvailable"])

        # Delete book
        del_res = self.client.delete(f"/v1/books/{book_id}")
        self.assertEqual(del_res.status_code, 204)

        # Verify 404 after delete
        not_found_res = self.client.get(f"/v1/books/{book_id}")
        self.assertEqual(not_found_res.status_code, 404)
        self.assertEqual(not_found_res.headers["Content-Type"], "application/problem+json")
        err = not_found_res.get_json()
        self.assertEqual(err["status"], 404)
        self.assertEqual(err["title"], "Book Not Found")

    def test_validation_error_rfc7807(self):
        # Missing required fields
        res = self.client.post("/v1/books", json={"title": "Missing Author"})
        self.assertEqual(res.status_code, 422)
        self.assertEqual(res.headers["Content-Type"], "application/problem+json")
        err = res.get_json()
        self.assertEqual(err["status"], 422)
        self.assertIn("Missing required fields", err["detail"])

    def test_bad_request_rfc7807(self):
        res = self.client.get("/v1/books?limit=-5")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.headers["Content-Type"], "application/problem+json")
        err = res.get_json()
        self.assertEqual(err["status"], 400)

if __name__ == "__main__":
    unittest.main()
