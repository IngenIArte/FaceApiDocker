import base64
import json
import logging
import os
import shutil
import tempfile
import time
import uuid
from datetime import datetime

import redis
import requests
import rq.timeouts
from flasgger import Swagger, swag_from
from flask import Flask, request, redirect, Response
from rq import Queue, Connection
from rq.job import Job
from rq.job import get_current_job

from app import exceptions
from app.models import TaskInput
from messages import messages
from processor import processor2
from processor.processor2 import DocType
from utils import utils

temp_path = os.environ["DEFAULT_TEMPPATH"]
tempfile.tempdir = temp_path

logger = logging.getLogger(__name__)
app = Flask(__name__)

swagger = Swagger(app, template={"info": {"version": str(datetime.utcnow())}})

SUCCESS_STATUS = "success"
ERROR_STATUS = "error"
FAIL_STATUS = "fail"


@app.route("/", methods=["GET"])
def swagger_home():
    return redirect("/apidocs/")


@app.route("/tasks", methods=["POST"])
@swag_from('specifications/newtask.yml')
def tasks():
    input_data = TaskInput(request.json)
    tempdir = tempfile.mkdtemp()
    taskid = str(uuid.uuid4())
    extra = {"taskid": taskid}
    try:
        #s input_data.write_files(tempdir)
        #s if utils.is_windows():
        if True:
            logger.info("Creando tarea en windows", extra=extra)
            data = create_task(input_data, tempdir)
        else:
            logger.info("Agregando tarea a las cola", extra=extra)
            try:
                with Connection(redis.from_url(os.environ['RQ_URL'])):
                    q = Queue(is_async=bool(os.environ["RQ_ASYNC"]))
                    timeout = int(os.environ['RQ_TASKTIMEOUT'])
                    logger.debug(f"Tarea agregada a la cola.", extra=extra)
                    job: Job = q.enqueue(create_task, input_data, tempdir, job_id=taskid, job_timeout=timeout)
                
                #sdata = {"origin": input_data.doc_type.value,
                #s        "task_id": taskid}
                data = {"origin": "input_data.doc_type.value",
                        "task_id": taskid}
            except Exception as e:
                raise exceptions.CannotAppendTaskToQueue from e

        body = create_success_body(data)
        return createresponse(body)
    except Exception as e:
        logger.info("Removiendo archivos temporales")
        shutil.rmtree(tempdir, ignore_errors=True)
        raise e


def rq_exception_handler(job, exc_type, exc_value, traceback):
    logger.exception(exc_value)
    job.meta["exc_value"] = exc_value
    job.meta["traceback"] = exceptions.get_traceback(exc_value)
    job.save_meta()
    logger.debug("SE ACTUALIZO EL META DEL JOB")


def create_task(input_data, tempdir):
    try:
        output_process_data = processor2.processa(input_data.files, input_data.doc_type, input_data.extract_meta,
                                                  tempdir)
        return output_process_data
    
    except rq.timeouts.JobTimeoutException as e:
        raise exceptions.TaskTimeout from e

    finally:
        logger.info("Removiendo archivos temporales")
        shutil.rmtree(tempdir, ignore_errors=True)
        logging.shutdown()



@app.route("/tasks/<task_id>", methods=["GET"])
@swag_from('specifications/gettask.yml')
def get_task(task_id):
    task = __get_task(task_id)
    body = get_body_from_task(task)
    logger.info(f"Resultado de tarea obtenido: {json.dumps(body)[:100]}")
    return createresponse(body)


def __get_task(task_id):
    logger.info(f"Obteniendo result para {task_id}")
    try:
        with Connection(redis.from_url(os.environ["RQ_URL"])):
            q = Queue()
            task: Job = q.fetch_job(task_id)
    except Exception as e:
        raise exceptions.CannotFetchTaskFromQueue() from e
    if not task:
        e = exceptions.FetchedTaskIsNull()
        raise e
    return task


def get_body_from_task(task):
    from rq.job import JobStatus
    task_status = task.get_status()
    task_result = task.result
    #s origin: TaskInput = task.args[0].doc_type.value
    origin: TaskInput = task.args[0].doc_type #.value
    if task_status == JobStatus.QUEUED or task_status == JobStatus.STARTED or task_status == JobStatus.FINISHED:
        data = {
            "origin": origin,
            "task_id": task.id,
            "task_status": task_status,
            "task_result": task_result
        }
        body = create_success_body(data)
    elif task_status == JobStatus.FAILED:
        exc_value = task.meta["exc_value"]
        if isinstance(exc_value, exceptions.BaseApiError):
            body = __get_body_main_error(exc_value)
        else:
            tb = task.meta["traceback"]
            body = __get_body_unhandled_exception(exc_value, tb)
        body["data"]["origin"] = origin
    else:
        raise Exception("Unsupported job status")
    return body


@app.route("/config", methods=["GET"])
@swag_from('specifications/getconfig.yml')
def config():
    def serialize(val):
        try:
            json.dumps(val)
            return val
        except:
            return str(val)

    body = create_success_body({k: serialize(v) for k, v in app.config.items()})
    return createresponse(body)




@app.errorhandler(exceptions.BaseApiError)
def main_error_handler(e: exceptions.BaseApiError):
    logger.exception(e)
    body = __get_body_main_error(e)
    return createresponse(body)


def __get_body_main_error(e):
    data = e.__dict__
    msg = messages.get(type(e))
    body = create_error_body(msg, type(e).__name__, data)
    return body


@app.errorhandler(Exception)
@app.errorhandler(exceptions.InternalError)
def any_unhandled_exception(e):
    logger.exception(e)
    body = __get_body_unhandled_exception(e)
    return createresponse(body)


def __get_body_unhandled_exception(e, traceback=None):
    data = e.__dict__.copy()
    data["stacktrace"] = traceback or exceptions.get_traceback(e)
    msg = ". ".join([messages.get(type(e), ""), str(e)])
    body = create_error_body(msg, "Unhandled", data)
    return body


def create_success_body(data):
    return {"status": SUCCESS_STATUS, "data": data}


def create_error_body(message, code=None, data=None):
    body = {"status": ERROR_STATUS, "message": message}

    def addifnotnone(key, value):
        if value is not None:
            body[key] = value

    addifnotnone("code", code)
    addifnotnone("data", data)
    return body


def create_fail_body(data):
    return {"status": FAIL_STATUS, "data": data}


def create_error_body_from_eyexception(e):
    return create_error_body(e.message, e.code, e.data)


def create_fail_body_from_eyexception(e):
    data = {e.data["key"]: e.message}
    return create_fail_body(data)


def createresponse(body):
    return Response(json.dumps(body), status=200, mimetype='application/json')
