
from flask import Flask,jsonify,Response,request
from flask_swagger_ui import get_swaggerui_blueprint
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import requests
import random
import json
import os
import string
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exames.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
      SWAGGER_URL,
      API_URL,
      config={
            'app_name': "Test App"
      }
      )
# swagger
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
def makeUniqueCode():
      code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
      return code
migrate = Migrate(app, db)
# models
class Exame(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String(80), nullable=False)
      examCode = db.Column(db.String(120), unique=True, nullable=False)
      platform = db.Column(db.String(120))
      examHours = db.Column(db.Integer)
      examMinutes = db.Column(db.Integer)
      allowExamTimeForStudent = db.Column(db.Integer)
      
      def serialize(self):
            return {
                  'id': self.id,
                  'name': self.name,
                  'examCode': self.examCode,
                  'platform': self.platform,
                  'examHours': self.examHours,
                  'examMinutes': self.examMinutes,
                  'allowExamTimeForStudent': self.allowExamTimeForStudent
                  
            }
class Question(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      question = db.Column(db.String(80), nullable=False)
      questionImg = db.Column(db.String(120))
      examCode = db.Column(db.String(120), db.ForeignKey('exame.examCode'), nullable=False)
      answerCode = db.Column(db.String(120), nullable=False)
      questionType = db.Column(db.String(120), nullable=False)
      questionImg = db.Column(db.String(120))
      questionMark = db.Column(db.Integer)
      imgWithQuestions = db.Column(db.String(120))
      def serialize(self):
            return {
                  'id': self.id,
                  'question': self.question,
                  'examCode': self.examCode,
                  'answerCode': self.answerCode,
                  'questionType': self.questionType,
                  'questionImg': self.questionImg,
                  'questionMark': self.questionMark ,
                  'imgWithQuestions': self.imgWithQuestions               
            }
class MCQAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(120), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    answerCode = db.Column(db.String(120))
    imgWithAnswer = db.Column(db.String(120))
    def serialize(self):
        return {
            'id': self.id,
            'answer': self.answer,
            'is_correct': self.is_correct,
            'answerCode': self.answerCode,
            'imgWithAnswer': self.imgWithAnswer
        }
class TrueFalseAnswer(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      answer = db.Column(db.Boolean, nullable=False)
      answerCode = db.Column(db.String(120))
      def serialize(self):
            return {
                  'id': self.id,
                  'answer': self.answer,
                  'answerCode': self.answerCode
            }
class UsersMarks(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      email = db.Column(db.String(120), nullable=False)
      platform = db.Column(db.String(120), nullable=False)
      userPhone = db.Column(db.String(120), nullable=False)
      userParentPhone = db.Column(db.String(120), nullable=False)
      examCode = db.Column(db.String(120), nullable=False)
      mark = db.Column(db.Integer, nullable=False)
      def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'examCode': self.examCode,
            'mark': self.mark,
            'platform': self.platform,
            'userPhone': self.userPhone,
            'userParentPhone': self.userParentPhone
        }
# make a db for user answers
class UserAnswers(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      email = db.Column(db.String(120), nullable=False)
      examCode = db.Column(db.String(120), nullable=False)
      questionCode = db.Column(db.String(120), nullable=False)
      UserAnswers = db.Column(db.String(120), nullable=False)
      ActualAnswer = db.Column(db.String(120), nullable=False)
      isTrue = db.Column(db.Boolean, nullable=False)
      def serialize(self):
            return {
                  'id': self.id,
                  'email': self.email,
                  'examCode': self.examCode,
                  'questionCode': self.questionCode,                 
                  'UserAnswers': self.UserAnswers,
                  'ActualAnswer': self.ActualAnswer,
                  'isTrue': self.isTrue
            }

class Imega(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), nullable=False)
    img = db.Column(db.LargeBinary)

#APIs routes
# ================exam routes================
# add exam

@app.route('/api/v1/add_exame', methods=['POST'])
def add_exam():
      data = request.json
      examCode = makeUniqueCode()
      new_exame = Exame(name=data['name'], 
                        examCode=examCode, 
                        platform=data['platform'],
                        examHours=data['examHours'], 
                        examMinutes=data['examMinutes'], 
                        allowExamTimeForStudent=data['allowExamTimeForStudent']
                        )
      db.session.add(new_exame)
      db.session.commit()
      return jsonify({'examCode': examCode}), 201
# get all user marks
@app.route('/api/v1/get_all_user_marks', methods=['GET'])
def get_all_user_marks():
      user_marks = UsersMarks.query.all()
      return jsonify([user_mark.serialize() for user_mark in user_marks]), 200
# add question
@app.route('/api/v1/add_question', methods=['POST'])
def add_question():
      data = request.json
      answerCode = makeUniqueCode()
      new_question = Question(question=data['question'], 
                              examCode=data['examCode'], 
                              answerCode=answerCode, 
                              questionType=data['questionType'],
                              questionImg=data['questionImg'],
                              questionMark=data['questionMark'],
                              imgWithQuestions=data['imgWithQuestions']                              
                              )
      db.session.add(new_question)
      db.session.commit()
      return jsonify({'answerCode': new_question.answerCode}), 201

@app.route('/api/v1/add_mcq_answer', methods=['POST'])
def add_mcq_answer():
      data = request.json
      new_answer = MCQAnswer(answer=data['answer'], 
                              is_correct=data['is_correct'], 
                              answerCode=data['answerCode'],
                              imgWithAnswer=data['imgWithAnswer']
                              )
      db.session.add(new_answer)
      db.session.commit()
      return jsonify({'answerCode': new_answer.answerCode}), 201

@app.route('/api/v1/add_true_false_answer', methods=['POST'])
def add_true_false_answer():
      data = request.json
      new_answer = TrueFalseAnswer(answer=data['answer'], 
                              answerCode=data['answerCode']
                              )
      db.session.add(new_answer)
      db.session.commit()
      return jsonify({'answerCode': new_answer.answerCode}), 201
# get all exames
@app.route('/api/v1/get_all_exames', methods=['GET'])
def get_all_exames():
      exames = Exame.query.all()
      return jsonify([exame.serialize() for exame in exames]), 200
# get exame by code
@app.route('/api/v1/get_exame/<code>', methods=['GET'])
def get_exame(code):
      exame = Exame.query.filter_by(examCode=code).first()
      if exame is None:
            return jsonify({'error': 'Exame not found'}), 404
      return jsonify(exame.serialize()), 200
# get exam questions by code and type of question and if he mcq get the answers

@app.route('/api/v1/get_exam_questions/<code>', methods=['GET'])
def get_exam_questions(code):
      questions = Question.query.filter_by(examCode=code).all()
      if questions is None:
            return jsonify({'error': 'Questions not found'}), 404
      questions_data = []
      for question in questions:
            question_data = question.serialize()
            if question.questionType == 'mcq':
                  answers = MCQAnswer.query.filter_by(answerCode=question.answerCode).all()
                  question_data['answers'] = [answer.serialize() for answer in answers]
            elif question.questionType == 'true_false':
                  answer = TrueFalseAnswer.query.filter_by(answerCode=question.answerCode).first()
                  question_data['answer'] = answer.serialize()
            
            questions_data.append(question_data)
      return jsonify(questions_data), 200


@app.route('/api/v1/send_exam', methods=['POST'])
def send_exam():
    data = request.json

    exam_code = data.get('examCode')
    questions = Question.query.filter_by(examCode=exam_code).all()

    if not questions:
        return jsonify({'error': 'Questions not found for the given examCode'}), 404

    total_mark = 0
    exam_mark = 0

    for question_data in data.get('questions', []):
        question_type = question_data.get('questionType')
        answer_code = question_data.get('answerCode')
        user_answer = question_data.get('answer')

        question = next((q for q in questions if q.answerCode == answer_code), None)

        if not question:
            return jsonify({'error': f'Question with answerCode {answer_code} not found'}), 404

        exam_mark += question.questionMark

        if question_type == 'mcq':
            answer = MCQAnswer.query.filter_by(answerCode=answer_code, is_correct=True).first()
        elif question_type == 'true_false':
            answer = TrueFalseAnswer.query.filter_by(answerCode=answer_code).first()
        else:
            # Handle other question types if needed
            continue

        if answer and answer.answer == user_answer:
            total_mark += question.questionMark

        user_answers = UserAnswers(
            email=data.get('email'),
            examCode=exam_code,
            questionCode=answer_code,
            UserAnswers=user_answer,
            ActualAnswer=answer.answer if answer else None,
            isTrue=answer and answer.answer == user_answer
        )

        db.session.add(user_answers)
        db.session.commit()

    new_user_mark = UsersMarks(
        email=data.get('email'),
        examCode=exam_code,
        mark=total_mark,
        platform=data.get('platform'),
        userPhone=data.get('userPhone'),
        userParentPhone=data.get('userParentPhone')
    )

    db.session.add(new_user_mark)
    db.session.commit()

    exam_info = Exame.query.filter_by(examCode=exam_code).first()

    response_data = {
        'mark': total_mark,
        'examMark': exam_mark,
        'examInfo': exam_info.serialize(),
        'user': new_user_mark.serialize()
    }

    return jsonify(response_data), 200

# get user answers
@app.route('/api/v1/get_user_answers/<email>/<examCode>', methods=['GET'])
def get_user_answers(email, examCode):
    user_answers = UserAnswers.query.filter_by(email=email, examCode=examCode).all()
    if not user_answers:
        return jsonify({'error': 'User answers not found'}), 404
    return jsonify([user_answer.serialize() for user_answer in user_answers]), 200
# ================media routes================

@app.route('/api/v1/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    unique_code = makeUniqueCode()
    img_data = file.read()
    new_image = Imega(code=unique_code, img=img_data)
    db.session.add(new_image)
    db.session.commit()
    return jsonify({'code': unique_code}), 200


@app.route('/api/v1/get_image/<code>', methods=['GET'])
def get_image(code):
    img = Imega.query.filter_by(code=code).first()
    if img is None:
        return jsonify({'error': 'Image not found'}), 404
    return Response(img.img, mimetype='image/jpeg')


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True)