import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from settings import DB_USER, DB_PASSWORD
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_paginate_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))

    def test_invalid_pagination(self):
        res = self.client().get("./questions?page=1000")
        data = json.loads(res.data)
        self.assertEqual(data["error"], 404)
        self.assertEqual(data["error"], 404)

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    def test_delete_questions(self):
        res = self.client().delete("/questions/1")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id==1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 1)

    def test_delete_questions_invalid(self):
        res = self.client().delete("/questions/ywb")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["error"], 404)

    def test_search_questions_success(self):
        res = self.client().post("/questions", json={"searchTerm": "movie"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])

    def test_search_questions_empty_string(self):
        res = self.client().post("/questions", json={"searchTerm": ""})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])

    def test_search_questions_not_found(self):
        res = self.client().post("/questions", json={"searchTerm": "abcdxyz"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertFalse(len(data["questions"]))
        self.assertFalse(data["totalQuestions"])

    def test_get_questions_in_category_success(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])

    def test_add_question(self):
        new_question = {
            "question": "What is the color of the sky?",
            "answer": "Blue",
            "category": "1",
            "difficulty": "1"
        }

        res = self.client().post("/questions/add", json=new_question)
        data = json.loads(res.data)

        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])

    def test_add_bad_question(self):
        bad_que = {
            "question": "What is the color of the sky?",
            "answer": "",
            "category": "1",
            "difficulty": "1"
        }

        res = self.client().post("/questions/add", json=bad_que)
        data = json.loads(res.data)

        self.assertEqual(data["error"], 400)

    def test_get_question_for_quiz(self):
        input = {
            "previous_questions": [2, 6],
            "quiz_category": 6
        }

        res = self.client().post("/quizzes", json=input)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
   
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()