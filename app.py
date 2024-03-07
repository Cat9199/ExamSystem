
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
      def serialize(self):
            return {
                  'id': self.id,
                  'question': self.question,
                  'examCode': self.examCode,
                  'answerCode': self.answerCode,
                  'questionType': self.questionType                  
            }
class MCQAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(120), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    answerCode = db.Column(db.String(120))
    def serialize(self):
        return {
            'id': self.id,
            'answer': self.answer,
            'is_correct': self.is_correct,
            'answerCode': self.answerCode
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
    
class Imega(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), nullable=False)
    img = db.Column(db.LargeBinary)

#APIs routes
# ================exame routes================
# add exame
@app.route('/api/v1/add_exame', methods=['POST'])
def add_exame():
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
# add question
@app.route('/api/v1/add_question', methods=['POST'])
def add_question():
      data = request.json
      answerCode = makeUniqueCode()
      new_question = Question(question=data['question'], 
                              examCode=data['examCode'], 
                              answerCode=answerCode, 
                              questionType=data['questionType']
                              )
      db.session.add(new_question)
      db.session.commit()
      return jsonify({'answerCode': new_question.answerCode}), 201

@app.route('/api/v1/add_mcq_answer', methods=['POST'])
def add_mcq_answer():
      data = request.json
      new_answer = MCQAnswer(answer=data['answer'], 
                              is_correct=data['is_correct'], 
                              answerCode=data['answerCode']
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
            questions_data.append(question_data)
      return jsonify(questions_data), 200
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
# Api to get image
@app.route('/api/v1/get_image/<code>', methods=['GET'])
def get_image(code):
    img = Imega.query.filter_by(code=code).first()
    if img is None:
        return jsonify({'error': 'Image not found'}), 404
    return Response(img.img, mimetype='image/jpeg')

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True)
 