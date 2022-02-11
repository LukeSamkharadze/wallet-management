# Design-Patterns-Final-Project

Setup:

```bash
pip install -r requirements.txt
pre-commit install
mypy --install-types
```

Run project:

* Navigate to the folder where the app folder is stored and run:
  * `uvicorn app.runner.asgi:app --reload`
* Or, in Pycharm, setup execution configuration:
  * Module name: `uvicorn`
  * Parameters: `app.runner.asgi:app --reload`
  * Working directory: Path to the folder, where the app folder is stored
    * So if path to app folder is `C:\Users\lashu\Desktop\desfinal\app`, we set `C:\Users\lashu\Desktop\desfinal` as working directory

Go to `http://127.0.0.1:8000/docs/` to call api
