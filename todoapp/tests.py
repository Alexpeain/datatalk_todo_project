from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Todo


class TodoModelTests(TestCase):
	def test_default_values_and_str(self):
		t = Todo.objects.create(title="Test todo")
		self.assertFalse(t.resolved)
		self.assertIsNotNone(t.created_at)
		self.assertIsNotNone(t.updated_at)
		self.assertEqual(str(t), "Test todo")


class TodoViewTests(TestCase):
	def setUp(self):
		self.list_url = reverse("todo_list")
		self.create_url = reverse("todo_create")

	def test_list_view_empty(self):
		resp = self.client.get(self.list_url)
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, "No todos yet.")

	def test_create_view_post_valid(self):
		data = {
			"title": "Buy milk",
			"description": "2 liters",
			"due_date": timezone.now().date().isoformat(),
			"resolved": False,
		}
		resp = self.client.post(self.create_url, data, follow=True)
		self.assertEqual(resp.status_code, 200)
		self.assertTrue(Todo.objects.filter(title="Buy milk").exists())

	def test_create_view_post_invalid(self):
		# missing title -> invalid
		data = {"title": "", "description": "no title"}
		resp = self.client.post(self.create_url, data)
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, "This field is required.")
		self.assertEqual(Todo.objects.count(), 0)

	def test_update_view(self):
		todo = Todo.objects.create(title="Initial")
		url = reverse("todo_edit", args=[todo.pk])
		resp = self.client.post(url, {"title": "Updated", "description": "", "due_date": "", "resolved": False}, follow=True)
		self.assertEqual(resp.status_code, 200)
		todo.refresh_from_db()
		self.assertEqual(todo.title, "Updated")

	def test_delete_view(self):
		todo = Todo.objects.create(title="To delete")
		url = reverse("todo_delete", args=[todo.pk])
		# GET returns confirmation page
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		# POST should delete
		resp = self.client.post(url, follow=True)
		self.assertEqual(resp.status_code, 200)
		self.assertFalse(Todo.objects.filter(pk=todo.pk).exists())

	def test_toggle_view(self):
		todo = Todo.objects.create(title="Toggle me", resolved=False)
		url = reverse("todo_toggle", args=[todo.pk])
		resp = self.client.get(url, follow=True)
		self.assertEqual(resp.status_code, 200)
		todo.refresh_from_db()
		self.assertTrue(todo.resolved)

