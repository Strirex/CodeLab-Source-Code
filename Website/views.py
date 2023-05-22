from flask import Blueprint, render_template, request, url_for, redirect, jsonify, flash
from flask_login import login_required, current_user
from .models import *
import json
import sqlite3 as sql
from . import runcode
from . import chatgpt
conn=sql.connect('database.db')
c=conn.cursor()

views=Blueprint('views',__name__)


'''
routing
'''

@views.route('/',methods=['GET','POST'])
def home():
    return render_template("home.html",user=current_user)



@views.route("/projects",methods=['GET','POST'])
@login_required
def view_invitations():
    if request.method=='POST': #newroom
        room_name=request.form.get('room_name')
        concept_name=request.form.get('concept_name')
        if len(room_name)==0:
            flash('Please input a name for the room',category='error')
        if len(concept_name)==0:
            flash('Please input a valid concept ',category='error')
        room_language=request.form.get('room_language')
        
        RoomByName = Room.query.filter_by(room_name=room_name,owner_id=current_user.id).first()
        
        language_code={'python':default_python_code,'C':default_c_code,'Cpp':default_cpp_code}
        if RoomByName:
            flash('Room Name already exists.', category='error')
        else:
            introduction=chatgpt("Explain"+str(concept_name)+"with the aid of code written in"+room_language)
            question=chatgpt("Ask a question about" + str(concept_name) + "that requires me to write code, begin with Question")
            new_room=Room(room_name=room_name,
                          owner_id=current_user.id,
                          room_language=room_language,
                          room_concept=concept_name,
                          data=language_code[room_language],
                          introduction=introduction,
                          question=question)
            db.session.add(new_room)
            db.session.commit() 

    room=Room.query.filter_by(owner_id=current_user.id).all()
    
    #Project name #Room Langugae 
    return render_template('projects.html',user=current_user,room=room) 

@views.route('/projects', methods=['DELETE'])
@login_required
def deleteRoom():
    room = json.loads(request.data)
    roomId = room['roomId']
    room = Room.query.get(roomId)
    if room:
        if room.owner_id == current_user.id:
            db.session.delete(room)
            db.session.commit()  
    return jsonify({})


'''
code editor navigation
'''


default_c_code = """#include <stdio.h>

int main(int argc, char **argv)
{
    printf("Hello C World!!\\n");
    return 0;
}    
"""

default_cpp_code = """#include <iostream>

using namespace std;

int main(int argc, char **argv)
{
    cout << "Hello C++ World" << endl;
    return 0;
}
"""

default_python_code = """import sys
import os

if __name__ == "__main__":
    print ("Hello Python World!!")
"""

default_rows = "15"
default_cols = "60"




@views.route("/session/<room_id>/python",methods=['POST','GET'])
@login_required
def enter_room_python(room_id): 
    
    if(request.method=='POST'):
        if 'run' in request.form:
            print("Executed")
            code = request.form['code'] #preserves indentation
            run = runcode.RunPyCode(code)
            rescompil, resrun = run.run_py_code()
            if not resrun:
                resrun = 'No result!'
        elif 'save and exit' in request.form:
            room=Room.query.filter_by(id=room_id).first()
            code=request.form['code']
            room.data=code
            db.session.commit()
            redirect(url_for('views.view_invitations'))
        elif 'revert to default' in request.form:
            code=default_python_code
        
    else:
        room=Room.query.filter_by(id=room_id).first()
        code = room.data
        resrun = 'No result!'
        rescompil = 'No Compilation for Python'

    # room=Room.query.filter_by(id=room_id).first()
    # introduction=room.introduction
    # question=room.question
    
    
    return render_template('code_editor.html',
                           user=current_user,
                           code=code,
                           target=url_for('views.enter_room_python',room_id=room_id),
                           resrun=resrun,
                           rescomp=rescompil,
                           rows=default_rows,
                           cols=default_cols,
                           room_id=room_id,
                        #    introduction=introduction,
                        #    question=question,
                            h_reference=f'/session/{room_id}/python')

@views.route("/session/<room_id>/C",methods=['POST','GET'])
@login_required
def enter_room_C(room_id): 
    if(request.method=='POST'):
        code = request.form['code']
        run = runcode.RunCCode(code)
        rescompil, resrun = run.run_c_code()
        print("Printing resrun")
        print(resrun)
        if not resrun:
            resrun = 'No result!'
    else:
        code = default_c_code
        resrun = 'No result!'
        rescompil = ''
        
    return render_template('code_editor.html',
                           user=current_user,
                           code=code,
                           target=url_for('views.enter_room_C',room_id=room_id),
                           resrun=resrun,
                           rescomp=rescompil,
                           rows=default_rows,
                           cols=default_cols,
                           room_id=room_id,
                            h_reference=f'/session/{room_id}/C')

@views.route("/session/<room_id>/Cpp",methods=['POST','GET'])
@login_required
def enter_room_Cpp(room_id): 
    if(request.method=='POST'):
        code = request.form['code']
        run = runcode.RunCppCode(code)
        rescompil, resrun = run.run_cpp_code()
        if not resrun:
            resrun = 'No result!'
    else:
        code = default_cpp_code
        resrun = 'No result!'
        rescompil = ''
        
    return render_template('code_editor.html',
                           user=current_user,
                           code=code,
                           target=url_for('views.enter_room_Cpp',room_id=room_id),
                           resrun=resrun,
                           rescomp=rescompil,
                           rows=default_rows,
                           cols=default_cols,
                           room_id=room_id,
                           h_reference=f'/session/{room_id}/Cpp'
                           )
    

