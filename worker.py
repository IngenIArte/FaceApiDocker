def run_worker():
    redis_connection = redis.from_url(os.environ['RQ_URL'])
    with Connection(redis_connection):
        from app.service import rq_exception_handler
        worker = Worker(['default'], exception_handlers=rq_exception_handler, disable_default_exception_handler=True)
        worker.work()


if __name__ == '__main__':
    from utils import logutil, utils
    import os

    utils.load_config(os.environ["ENV_CONFIG"])
    logutil.setup_logger()
    import redis
    from rq import Connection, Worker
    # Hace que las tareas empiecen mas rapido
    from processor.processor2 import processa

    run_worker()
