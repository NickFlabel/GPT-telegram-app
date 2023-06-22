Telegram Bot App
The Telegram GPT3.5 Bot is a Python-based application that allows users to access the power of GPT-3.5 through a Telegram bot. This application is divided into two services: the Telegram bot app and the database management app.
Features

Telegram Bot Service

    Conversation Creation: Users can create and choose conversations with the GPT-3.5 bot within the Telegram app.
    Message Exchange: Users can send messages to the GPT-3.5 bot and receive responses directly in the Telegram chat interface.
    Message History: The bot app keeps track of the conversation history, allowing users to review their previous interactions with the bot.

Database Management Service

    User and Conversation Management: The database app is responsible for saving and retrieving user information, including their conversations with the GPT-3.5 bot.
    Message Persistence: Messages exchanged between users and the GPT-3.5 bot are securely stored in the database, ensuring that conversation history is preserved.
Docker Compose Configuration

To easily run the application and its services, a docker-compose.yml file is provided.

The configuration sets up the two services (chatbot and db_api) along with a PostgreSQL database service (db) using the postgres:13 Docker image. The services are linked together, and the necessary environment variables are provided for each service.

Getting Started

To run the application, follow these steps:

    Clone the repository.

    Make sure you have Docker and Docker Compose installed on your system.

    Provide your own tokens.env file, which should contain your OpenAI API key and Telegram bot token.

    In the project directory, run the following command to start the services:

    docker-compose up

    This will build the necessary Docker images and start the services defined in the docker-compose.yml file.

Usage

Once the services are up and running, you can interact with the Telegram bot. The bot can be accessed via the Telegram application by searching for the bot using the provided bot token.

Testing

The application includes a test suite. To run the tests for each individual service, navigate to the respective service directory (./bot or ./db_api) and run the following command:

pytest

This will execute the test suite for the corresponding service and provide the test results.
