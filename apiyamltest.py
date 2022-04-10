###### Note this if for API testing without authentication (Unable to include header file in Yaml) 


from enum import unique
from re import A
from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse
import datetime
from flask_security import Security, SQLAlchemyUserDatastore,login_required, auth_required, hash_password, UserMixin, RoleMixin,logout_user
from flask_security.models import fsqla_v2 as fsqla
import os
from flask_cors import CORS
from prompt_toolkit import Application
from sqlalchemy import true


# Initialisations
app = Flask(__name__)
api= Api(app) 
CORS(app)



app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///testdb.sqlite3" 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
app.config["WTF_CSRF_ENABLED"]=False
app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]="Authentication-Token"


app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Create database connection object
db = SQLAlchemy(app)

# Define models
fsqla.FsModels.set_db_info(db)

class Role(db.Model, fsqla.FsRoleMixin):
    pass

class User(db.Model, fsqla.FsUserMixin):
    pass

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)



##########DataBase##############
class profile_db (db.Model):
  user_name = db.Column(db.String, primary_key = True ,nullable= False, unique=True)
  first_name = db.Column(db.String, nullable = False)
  email= db.Column(db.String, nullable = False)
  password=db.Column(db.String, nullable = False)
  # fs_uniquifier=db.Column(db.String(255),unique=True, nullable = False)


class deck (db.Model):
  word_id=db. Column(db.Integer, primary_key = True, autoincrement = True)
  deck_name = db. Column(db.String, nullable = False)
  Word = db.Column(db.String, nullable= False)
  Meaning = db.Column(db.String, nullable = False)
  last_access = db.Column(db.String, nullable = False)
  score = db.Column(db.Integer, nullable = False)
  user_name = db. Column(db.String, nullable=False)


db.create_all()


def datecalc():
  x = str(datetime.datetime.now())
  l=x.split(" ")
  return l[0]

def Avgscorecalcanddate(user,lang):
  data=deck.query.all()
  total=0
  count=0
  x="Never" #date of last access
  try:
    for i in data:
      if i.deck_name==lang and i.user_name==user and i.Word!="thisisacoompltelyrandomstringsoleaveitwhilegivingresponse":
        total+=i.score
        count+=1
        x=i.last_access
    avg=total/count
  except:
    return [lang,"Scores Can't be calculated",x]
  
  
  if avg>=1 and avg<1.6:
    return [lang,"Low",x]
  elif avg>=1.5 and avg<2.5:
    return [lang,"Medium",x]
  elif avg>=2.5 and avg<=3:
    return [lang,"High",x]
  else:
    return [lang,"Scores Can't be calculated",x]

####### API's#####
###parsers
login=reqparse.RequestParser()
login.add_argument('email')
login.add_argument('password')


signup=reqparse.RequestParser()
signup.add_argument('email',type=str,required=True)
signup.add_argument('username',type=str,required=True)
signup.add_argument('password',type=str,required=True)
signup.add_argument('f_name',type=str,required=True)

card=reqparse.RequestParser()
card.add_argument('name',type=str, required=True)
card.add_argument('Word',type=str)
card.add_argument('meaning',type=str)
# addcard.add_argument('username',type=str,Required=true)

cardwords=reqparse.RequestParser()
cardwords.add_argument('Word',type=str, required=True)
cardwords.add_argument('meaning',type=str, required=True)

profile_update=reqparse.RequestParser()
profile_update.add_argument('f_name',type=str)
profile_update.add_argument('email',type=str)
profile_update.add_argument('password',type=str)

word_update=reqparse.RequestParser()
word_update.add_argument('word',type=str)
word_update.add_argument('meaning',type=str)

score_up=reqparse.RequestParser()
score_up.add_argument('score',type=str)


#####Classes

class get_email(Resource):
  def get(self,username):
    data=profile_db.query.all()
    for i in data:
      if (i.user_name)==username:
        return {"email":i.email,"pass":i.password},200

    return {"message":"No such user"},409

class loginapi(Resource):
  def post(self,):
    args=login.parse_args()
    mail=args["email"]
    password=args["password"]
    return args 


class Signup(Resource):
 
  def post(self):
    args=signup.parse_args()
    data=profile_db.query.all()
    l=[]
    newl=[]
    for i in data:
      l.append(i.user_name) 
      newl.append(i.email)
    if args["username"] in l:
      return {"message":"UserName already exists"},409

    if args["email"] in newl:
      return {"message":"Email already exists"}

    a = profile_db(user_name=args["username"],first_name=args["f_name"],email=args["email"],password=args["password"])
    db.session.add(a)
    user_datastore.create_user(email=args["email"], password=hash_password(args["password"]))
    db.session.commit()
    return {"message":args["username"]+" Added Successfully"} ,201

class dashboardapi(Resource):

  def get(self,username):
    deck_data=deck.query.all()
    #print(deck_data)
    
    deck_json=[]
    all_decks=[]
    for i in deck_data:
      deck_info={}
      if i.user_name==username:
        #a=scorecalc(userid,i.deck_name)
        #x=[i.deck_name,i.last_access,a]
        #print(i.Word)
        deck_info["deck_name"]=i.deck_name
        deck_info["last_access"]=i.last_access
        deck_info["score"]=i.score
        deck_json.append(deck_info)
        all_decks.append(i.deck_name)
    
    set_all_decks=set(all_decks)
    unique=list(set_all_decks)
    result=[]

   ############################ADD CODE LATER######
    deck_details=[]
    # #print(deck_json)
    for i in unique:
      deck_details.append(Avgscorecalcanddate(username,i))
    print(deck_details)

        


    
    if len(deck_json)>0:
      return {"name":username, "data":"today","deck":unique,"message":'Successfull',"details":deck_details}, 200
    elif len(deck_json)==0:
      return {"message":"No Deck"}, 404
    else:
      return {"message":"Error! Kindly check user_name"}, 404


  def post(self,username):
    args=card.parse_args()
    data=deck.query.all()
    l=[]
    for i in data:
      if (i.user_name==username):
        l.append(i.deck_name) 
    if args["name"] in l:
      return {"Message": "Deck exists"},409
    if args["Word"]=="" or args["meaning"]=="":
      a = deck(deck_name=args["name"],Word="",Meaning="",last_access="Never",score=0,user_name=username)
    else:
      a = deck(deck_name=args["name"],Word=args["Word"],Meaning=args["meaning"],last_access="",score=0,user_name=username)
    db.session.add(a)
    db.session.commit()
    return {"Message":  args["name"]+" deck added successfully"}, 200 
  def delete(self,username,deckname):
    flag=0
    a=deck.query.all()
    for i in a:
      if i.user_name==username and i.deck_name==deckname:
        db.session.delete(i)    
        db.session.commit()
        flag=1
    if (flag==1):
        return {"message":"deleted "+deckname}
    else:
        return {"message":"Deck Not found"}

   


    



class profileapi(Resource):
  def get(self,username):
    user_data=profile_db.query.all()
    
    user_info={}
    for i in user_data:
      if i.user_name==username:
        #a=scorecalc(userid,i.deck_name)
        #x=[i.deck_name,i.last_access,a]
        user_info["user_name"]=i.user_name
        user_info["first_name"]=i.first_name
        user_info["email"]=i.email
    
    if len(user_info.keys())>0:
      return user_info, 200
    else:
      return {'message':'check user name'}
 
  def post(self,username): 
    args=profile_update.parse_args()
    # args["username"]=username
    d=profile_db.query.filter_by(user_name=username).first()
    if args["f_name"]!="":
      d.first_name=args["f_name"]

  

    if args["email"]!="":   
      d.email=args["email"]
    
    if args["password"]!="":   
      d.password=args["password"]
    db.session.commit()

    return {"Message": "Success"}, 201




class specific_deck_words(Resource):

  def get(self,username,deckname):
    deck_data=deck.query.all()
    words=[]
    
    for i in deck_data:
      single_word={}
      if i.user_name==username and i.deck_name==deckname and i.Word!="thisisacoompltelyrandomstringsoleaveitwhilegivingresponse" :
        single_word["Word"]=i.Word
        single_word["Meaning"]=i.Meaning
        single_word["score"]=i.score
        words.append(single_word)
        i.last_access=datecalc()
        db.session.commit()

    return {'deckname':deckname,'username':username,"words":words}, 200    


  def post(self,username,deckname):
    
    args=cardwords.parse_args()
    data=deck.query.all()
    l=[]
    for i in data:
      if i.user_name==username and i.deck_name==deckname:
        l.append(i.Word)
    if args["Word"] in l:
      return {"Message":"Word exists"},409

    if len(l)==0:  ##Debug 
      return {"Message":"Deck Not found"},404
    
    a = deck(deck_name=deckname,Word=args["Word"],Meaning=args["meaning"],last_access="Never",score=0,user_name=username)
    db.session.add(a)
    db.session.commit()

    return {"Message":"Word "+args["Word"]+" added successfully to deck=> "+deckname},200
  

  def delete(self,username,deckname,word):
    a=deck.query.all()
    for i in a:
      if i.deck_name==deckname and i.Word==word and i.user_name==username:
        db.session.delete(i)    #debug this later
        db.session.commit()
        return {"message":"Successfully deleted"},200
        

    return {"message":"Word not found"}, 404



class update_word(Resource):  
  def post(self,username,deck_name,old_word):
  
    args=word_update.parse_args()
    d=deck.query.filter_by(user_name=username,deck_name=deck_name,Word=old_word).first()
    w_arg=args["word"]
    m_arg=args["meaning"]
    

    if (w_arg!=""):
      d.Word=w_arg
    if (m_arg!=""):  
      d.Meaning=m_arg

    db.session.commit()
    return {"Message":"Success"}, 200


class update_score(Resource):
  def post(self,username,deck_name,word):
    args=score_up.parse_args()
    scoredict={"Easy":3,"Medium":2,"Hard":1}
    if args["score"]=="":
      return {"Message":"null Value received"}
    if args["score"]=="Easy" or args["score"]=="Medium" or args["score"]=="Hard":
      d=deck.query.filter_by(user_name=username,deck_name=deck_name,Word=word).first()
      try:
        d.score=scoredict[args["score"]]
        db.session.commit()
        return {"Message":"Success"}, 200

      except:
        return {"Message":"Word or deck don't exist"}, 200
    else:
       return {"Message":"Wrong Arguments"}, 200


####API Pending----          

class report_deckspecific(Resource):
  def get(self,username,deckname):
    return {'deckname':deckname,'username':username,"Last review":"last reviewed","Deck_dcore":"deck score",'word_score':[{'word':"score"}]}, 200   

class report_alldeck(Resource):
  def get(self,username,deckname):
    return {'deckname':deckname,'username':username,"Last review":"last reviewed","deck":[{"Deck_dcore":"deck score"}]}, 200   

####Api resources
api.add_resource(loginapi, "/api/")
api.add_resource(get_email, "/api/getemail/<username>")
api.add_resource(Signup,"/api/signup/")
api.add_resource(dashboardapi,"/api/dashboard/<username>","/api/dashboard/<username>/<deckname>")
api.add_resource(profileapi,"/api/profile/<username>")
api.add_resource(specific_deck_words,"/api/<username>/<deckname>/words/","/api/<username>/<deckname>/words/delete/<word>")
api.add_resource(report_deckspecific,"/api/<username>/<deckname>/report")
api.add_resource(report_alldeck,"/api/<username>/alldeck/report")
api.add_resource(update_word,"/api/<username>/<deck_name>/update_word/<old_word>")
api.add_resource(update_score,"/api/<username>/<deck_name>/review/<word>")




if __name__ == '__main__':
    app.run()