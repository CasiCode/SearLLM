from setuptools import setup


setup(
    name="backend",
    version="0.1",
    packages=["backend"],
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
