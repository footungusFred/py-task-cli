import json
import tempfile
import unittest
from pathlib import Path
from taskcli.service import add_task, complete_task, delete_task, list_tasks, stats, update_task
from taskcli.storage import load_tasks, save_tasks

class TaskServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "tasks.json"
    def tearDown(self):
        self.tmp.cleanup()
    def test_add_and_persist(self):
        task = add_task("  Ship it  ", "high", "2026-12-31", self.path)
        self.assertEqual((task["id"], task["title"]), (1, "Ship it"))
        self.assertEqual(load_tasks(self.path)[0]["due"], "2026-12-31")
    def test_validation(self):
        with self.assertRaises(ValueError): add_task(" ", path=self.path)
        with self.assertRaises(ValueError): add_task("x", due="not-a-date", path=self.path)
    def test_filter_and_complete(self):
        add_task("Alpha", "high", path=self.path)
        add_task("Beta", "low", path=self.path)
        self.assertEqual([x["title"] for x in list_tasks(self.path, priority="high")], ["Alpha"])
        complete_task(1, self.path)
        self.assertEqual(len(list_tasks(self.path)), 1)
        self.assertEqual(len(list_tasks(self.path, include_done=True)), 2)
    def test_edit_delete_stats(self):
        add_task("Old", path=self.path)
        update_task(1, self.path, title="New", priority="high")
        self.assertEqual(load_tasks(self.path)[0]["title"], "New")
        self.assertEqual(stats(self.path), {"total": 1, "done": 0, "open": 1})
        delete_task(1, self.path)
        self.assertEqual(stats(self.path)["total"], 0)
    def test_corrupt_file_is_reported(self):
        self.path.write_text("{broken", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            load_tasks(self.path)
    def test_duplicate_ids_rejected(self):
        task = {"id": 1, "title": "A", "priority": "normal", "due": None, "done": False}
        save_tasks([task, dict(task)], self.path)
        with self.assertRaisesRegex(ValueError, "duplicate IDs"):
            load_tasks(self.path)

if __name__ == "__main__": unittest.main()