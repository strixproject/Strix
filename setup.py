from setuptools import setup, find_packages

setup(
    name="strix",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "google-generativeai",
        "colorama",
        "prompt_toolkit",
        "openai",
        "anthropic",
        "groq",
        "mistralai",
    ],
    extras_require={
        "dev": ["pytest", "black", "flake8"],
    },
    entry_points={
        "console_scripts": [
            "strix = strix.main:main",
        ],
    },
)
