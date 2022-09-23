from crypt import methods
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    important functions: paginate
    '''
    def paginate(request,selection):
        page = request.args.get("page", 1 , type=int)
        start = (page -1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        formatted_data = [item.format() for item in selection]

        return formatted_data[start:end]

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    app.after_request
    def after_request(response):
        '''
        set access control for headers
        '''
        response.headers.add("Access-Controls-ALlow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-COntrols-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")


        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=['GET'])
    def get_categories():
        categories = Category.query.all()

        try:
            formatted_categories = {
                category.id: category.type for category in categories
            }
            
            return jsonify({
                "success": True,
                "categories": formatted_categories
            })

        except:
            abort(404)        

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    def get_questions():
        '''
        get questions with pagination
        '''
        questions = Question.query.all()
        categories = Category.query.all()
        paginated_questions = paginate(request, questions)

        if not len(paginated_questions):
            abort(404)
        
        return jsonify({
            "success":True,
            "questions": paginated_questions,
            "total_questions": len(questions),
            "categories": {
                category.id: category.type for category in categories
            }
        })


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter_by(id=str(question_id))

            if question is None:
                abort(404)

            question.delete()

            questions = Question.query.all()
            formatted_questions = paginate(request, questions)

            return jsonify({
                'success': True,
                'deleted': question_id,
                "questions": formatted_questions,
                "total_questions": len(questions)
            })
           
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions/add", methods=["POST"])
    def add_question():
        try:
            data = request.get_json()

            new_question = data["question"]
            new_answer = data["answer"]
            new_category = data["category"]
            new_difficulty = data["difficulty"]

            if (len(new_question) == 0) or (len(new_answer) == 0) or (len(new_category) == 0) or (len(new_difficulty) == 0):
                abort(422)

                
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
            )

            question.insert()

            questions = Question.query.all()
            formatted_questions = paginate(request, questions)

            return jsonify({
                "success": True,
                "created": question.id,
                "question": formatted_questions,
                "total_questions": len(questions)
            })

        except:
            abort(400)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions", methods=["POST"])
    def search_question():

        try:
            data = request.get_json()

            search_term = data.get('searchTerm', None)

            questions = Question.query.filter(Question.question.ilike("%{}%".format(search_term))).all()

            formatted_questions = [question.format() for question in questions]

            return jsonify({
                "success": True,
                "questions": formatted_questions,
                "totalQuestions": len(questions),
            })

        except:

            abort(400)


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions")
    def get_question_in_category(category_id):
        category = Category.query.get(category_id)

        if (category is None):
            abort(404)
        
        try:
            questions = Question.query.filter_by(category=category_id).all()

            formatted_questions = paginate(request, questions)

            return jsonify({
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(questions)
            })
        except:
            abort(500)


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=['POST'])

    def get_questions_for_quiz():
        
        data = request.get_json()
        try:
            category = data["quiz_category"]
            previous_questions = data["previous_questions"]
        except:
            abort(400)
        
        if category:
            questions = Question.query.filter_by(category=Question.category).all()

        else:
            questions = Question.query.all()
        
        # to get random que
        def get_random_question():
            next_question = random.choice(questions).format()
            return next_question

        next_question = get_random_question()

        #boolean to check if it was asked
        asked = False
        if next_question['id'] in previous_questions:
            asked = True
        
        while asked:
            next_question = random.choice(questions).format()

            if (len(previous_questions) == len(questions)):
                return jsonify({
                    "success": True,
                    "message": "Game over"
                }), 200

        return jsonify({
            "success": True,
            "question": next_question
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": 404,
            "message": "The requested resource was not found."
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "error": 422,
            "message": "Your request was unprocessable."
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": 400,
            "message": "Bad request."
        }), 400

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "error": 500,
            "message": "Internal server error."
        })

    return app

