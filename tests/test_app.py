import unittest
from app import app
from models import db, Users, Post

class BloglyTestCase(unittest.TestCase):
    """Comprehensive tests for Blogly routes."""

    def setUp(self):
        """Configure test environment."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_blogly'
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Persistent application context
        self.app_context = app.app_context()
        self.app_context.push()

        db.create_all()

        # Create base test user
        self.user = Users(
            first_name="Jane",
            last_name="Doe",
            image_url="https://example.com/image.jpg"
        )
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_list_users(self):
        """Test user listing page."""
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Jane Doe", response.data)

    def test_show_new_user_form(self):
        """Test new user form rendering."""
        response = self.client.get("/users/new")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"First Name", response.data)  # Match actual form label
        self.assertIn(b"Last Name", response.data)

    def test_create_user(self):
        """Test user creation flow."""
        response = self.client.post("/users/new", data={
            "first_name": "John",
            "last_name": "Smith",
            "image_url": "https://example.com/avatar.jpg"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"John Smith", response.data)

        # Verify database entry
        user = Users.query.filter_by(first_name="John").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.last_name, "Smith")

    def test_show_user_details(self):
        """Test user detail page."""
        response = self.client.get(f"/users/{self.user.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Jane Doe", response.data)
        self.assertIn(b"https://example.com/image.jpg", response.data)

    def test_add_post(self):
        """Test post creation and title display."""
        response = self.client.post(
            f'/users/{self.user.id}/posts/new',
            data={'title': 'New Post', 'content': 'Test content'},
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"New Post", response.data)  # Title in user detail
        self.assertNotIn(b"Test content", response.data)  # Content not here

    def test_view_post(self):
        """Test post detail page."""
        # Create post directly
        post = Post(
            title="First Post",
            content="Content here",
            user_id=self.user.id
        )
        db.session.add(post)
        db.session.commit()

        response = self.client.get(f'/posts/{post.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"First Post", response.data)
        self.assertIn(b"Content here", response.data)

    def test_edit_post(self):
        """Test post editing functionality."""
        # Create initial post
        post = Post(
            title="Original Title",
            content="Original Content",
            user_id=self.user.id
        )
        db.session.add(post)
        db.session.commit()

        # Edit post
        response = self.client.post(
            f'/posts/{post.id}/edit',
            data={'title': 'Updated Title', 'content': 'New Content'},
            follow_redirects=True
        )

        # Verify changes
        self.assertIn(b"Updated Title", response.data)
        self.assertIn(b"New Content", response.data)

    def test_delete_post(self):
        """Test post deletion."""
        post = Post(
            title="Delete Me",
            content="Should disappear",
            user_id=self.user.id
        )
        db.session.add(post)
        db.session.commit()

        response = self.client.post(
            f'/posts/{post.id}/delete',
            follow_redirects=True
        )

        # Check post removed from user detail
        self.assertNotIn(b"Delete Me", response.data)
        
        # Verify database removal
        deleted_post = Post.query.get(post.id)
        self.assertIsNone(deleted_post)

if __name__ == "__main__":
    unittest.main()


