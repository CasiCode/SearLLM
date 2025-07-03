from setuptools import setup, find_packages


setup(
    name="backend",
    version="0.1.0",
    packages=find_packages(),
    package_dir={"": "src"},
    install_requires=[
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
