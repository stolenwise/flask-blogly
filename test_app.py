import unittest
from app import app
from models import db, Users

# Test
class BloglyTestCase(unittest.TestCase):
    """Tests for routes in Blogly."""

    # https://unsplash.com/photos/man-wearing-henley-top-portrait-7YVZYZeITc8

    # https://unsplash.com/photos/shallow-focus-photography-of-woman-outdoor-during-day-rDEOVtE7vOs

    def setUp(self):
        """Set up test database."""
     
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_blogly'
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Create tables and sample data
        with app.app_context():
            db.create_all()
            # user = Users(first_name = "John", last_name = "Smith", image_url="https://unsplash.com/photos/man-wearing-henley-top-portrait-7YVZYZeITc8")
            # db.session.add(user)
            # db.session.commit()


    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_homepage_redirect(self):
        with app.test_client() as client:
            response = client.get("/")
            self.assertEqual(response.status_code, 302)  # Assuming it redirects

    # Test GET request to /users
    def test_list_users(self):
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test User", response.data)

    # Test GET request to /users/new
    def test_show_new_user_form(self):
        response = self.client.get("/users/new")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Create a user", response.data)

    # Test POST request to add an new user
    def test_create_user(self):
        response = self.client.post("/users/new", data ={
            "first_name": "Jane",
            "last_name": "Doe",
            "image_url": "https://unsplash.com/photos/shallow-focus-photography-of-woman-outdoor-during-day-rDEOVtE7vOs"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Jane Doe", response.data)

        # Verify that the user was added to the data base
        user = Users.query.filter_by(first_name="Jane").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.last_name, "Doe")

    # Test GET request to display user details
    def test_show_user_details(self):
        response = self.client.get("/users/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"See user details", response.data)

if __name__ == "__main__":
    unittest.main()