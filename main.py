if __name__ == '__main__':
    from utils import logutil, utils
    import os

    utils.load_config(os.environ["ENV_CONFIG"])
    logutil.setup_logger()
    import waitress
    from app.service import app

    waitress.serve(app, host=os.environ["DEFAULT_HOST"], port=int(os.environ["DEFAULT_PORT"]))
