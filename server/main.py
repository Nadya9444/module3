from flask import Flask, jsonify, request
from flasgger import Swagger

from server.db import users, jobs
from server.schemas import BaseUser, BaseJob

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Todo'
}
swagger = Swagger(app)


@app.get("/")
def index():
    return jsonify({
        "message": "Welcome to my todo application, use the /apidocs/ route to proceed"
    })


@app.get("/user/")
def get_user_list():
    """Get all users
    This is using docstrings for specifications.
    ---
    tags:
      - User
    definitions:
      BaseUser:
        type: object
        properties:
          username:
            type: string
          jobs:
            type: integer
          jobs_complete:
            type: integer
      Users:
        type: object
        properties:
          id:
            $ref: '#/definitions/BaseUser'
    responses:
      200:
        schema:
          $ref: '#/definitions/Users'
    """
    return jsonify(users)


@app.post("/user/")
def create_user():
    """Create user
    This is using docstrings for specifications.
    ---
    tags:
      - User
    parameters:
      - name: username
        in: body
        required: true
        schema:
          $ref: '#/definitions/CreateUser'
    definitions:
      User:
        type: object
        properties:
          id:
            type: integer
          username:
            type: string
          jobs:
            type: integer
          jobs_complete:
            type: integer
      CreateUser:
        type: object
        properties:
          username:
            type: string
    responses:
      201:
        schema:
          $ref: '#/definitions/User'
    """
    user = BaseUser(**request.json)
    user_id = list(users.keys())[-1] + 1 if users else 1
    users[user_id] = user.dict()
    user = user.dict()
    user.update({'id': user_id})
    return jsonify(user), 201


@app.delete("/user/<int:user_id>")
def delete_user(user_id):
    """Delete user
    This is using docstrings for specifications.
    ---
    tags:
      - User
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          $ref: '#/definitions/DeleteUser'
    definitions:
      DeleteUser:
        type: object
        properties:
          id:
            type: integer
      Error:
        type: object
        properties:
          message:
            type: string
          code:
            type: integer
    responses:
      200:
        schema:
          $ref: '#/definitions/User'
      404:
        schema:
          $ref: '#/definitions/Error'
    """
    if user_id not in users.keys():
        return jsonify({
            "message": f"Not found user with id = {user_id}",
            "code": 404
        }), 404
    user = users.pop(user_id)
    user.update({"id": user_id})
    user_jobs = []
    for i, job in jobs.items():
        if job["user_id"] == user_id:
            user_jobs.append(i)
    for i in user_jobs:
        jobs.pop(i)
    return jsonify(user)


@app.get("/jobs/")
def get_all_jobs():
    """Get all jobs
    This is using docstrings for specifications.
    ---
    tags:
      - Jobs
    definitions:
      BaseJob:
        type: object
        properties:
          name:
            type: string
          user_id:
            type: integer
          description:
            type: string
          complete:
            type: boolean
      Jobs:
        type: object
        properties:
          id:
           $ref: '#/definitions/BaseJob'
    responses:
      200:
        schema:
          $ref: '#/definitions/Jobs'
    """
    return jsonify(jobs)


@app.get("/jobs/<int:user_id>/")
def get_jobs_for_user(user_id):
    """Get all user jobs
    This is using docstrings for specifications.
    ---
    tags:
      - Jobs
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          $ref: '#/definitions/DeleteUser'
    responses:
      200:
        schema:
          $ref: '#/definitions/Jobs'
      404:
        schema:
          $ref: '#/definitions/Error'
        """
    if user_id not in users.keys():
        return jsonify({
            "message": f"Not found user with id = {user_id}",
            "code": 404
        }), 404
    user_jobs = {}
    for i, job in jobs.items():
        if job["user_id"] == user_id:
            user_jobs[i] = job
    return jsonify(user_jobs)


@app.post("/jobs/")
def create_job():
    """Create job
    This is using docstrings for specifications.
    ---
    tags:
      - Jobs
    parameters:
      - name: job
        in: body
        required: true
        schema:
          $ref: '#/definitions/CreateJob'
    definitions:
      CreateJob:
        type: object
        properties:
          name:
            type: string
          user_id:
            type: integer
          description:
            type: string
      Job:
        type: object
        properties:
          id:
            type: integer
          name:
            type: string
          user_id:
            type: integer
          description:
            type: string
          complete:
            type: boolean
    responses:
      201:
        schema:
          $ref: '#/definitions/Job'
      404:
        schema:
          $ref: '#/definitions/Error'
    """
    job = BaseJob(**request.json)
    if job.user_id not in users.keys():
        return jsonify({
            "message": f"Not found user with id = {job.user_id}",
            "code": 404
        }), 404
    job_id = list(jobs.keys())[-1] + 1 if jobs else 1
    jobs[job_id] = job.dict()
    job = job.dict()
    job.update({"id": job_id})
    users[job["user_id"]]["jobs"] += 1
    return jsonify(job), 201


@app.put("/jobs/")
def update_jobs():
    """Update job
    This is using docstrings for specifications.
    ---
    tags:
      - Jobs
    parameters:
      - name: job
        in: body
        required: true
        schema:
          $ref: '#/definitions/UpdateJob'
    definitions:
      UpdateJob:
        type: object
        properties:
          id:
            type: integer
          name:
            type: string
          description:
            type: string
          complete:
            type: boolean
    responses:
      200:
        schema:
          $ref: '#/definitions/Job'
      404:
        schema:
          $ref: '#/definitions/Error'
    """
    job = request.json
    if job["id"] not in jobs.keys():
        return jsonify({
            "message": f"Not found job with id = {job['id']}",
            "code": 404
        }), 404
    job_id = job.pop("id")
    if "complete" in job and job["complete"] != jobs[job_id]["complete"]:
        users[jobs[job_id]["user_id"]]["jobs_complete"] += 1 if job["complete"] else -1
    jobs[job_id].update(job)
    job = jobs[job_id].copy()
    job.update({"id": job_id})
    return jsonify(job)


@app.delete("/jobs/<int:job_id>")
def delete_job(job_id):
    """Delete job
    This is using docstrings for specifications.
    ---
    tags:
      - Jobs
    parameters:
      - name: job_id
        in: path
        required: true
        schema:
          $ref: '#/definitions/DeleteJob'
    definitions:
      DeleteJob:
        type: object
        properties:
          id:
            type: integer
    responses:
      200:
        schema:
          $ref: '#/definitions/Job'
      404:
        schema:
          $ref: '#/definitions/Error'
    """
    if job_id not in jobs.keys():
        return jsonify({
            "message": f"Not found job with id = {job_id}",
            "code": 404
        }), 404
    job = jobs.pop(job_id)
    job.update({"id": job_id})
    users[job["user_id"]]["jobs"] -= 1
    if job["complete"]:
        users[job["user_id"]]["jobs_complete"] -= 1
    return job


if __name__ == '__main__':
    app.run(debug=True)
