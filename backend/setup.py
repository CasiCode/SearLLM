from setuptools import setup, find_packages


setup(
    name="src",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "wheel",
        "bar",
        "greek",
        "langchain-community",
        "langgraph",
        "langchain[openai]",
        "langchain-core",
        "fastapi",
        "uvicorn",
        "pydantic",
        "python-dotenv",
        "pyyaml",
        "python-box",
        "python-telegram-bot",
    ],
)
