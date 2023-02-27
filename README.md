# Interactive Brokers Web API with Telegram Bot
This app connects your IB account with telegram bot. It allows:
- Display open positions
- Close a position
- Close all positions
- Display open orders
- Cancel an order
- Cancel all orders


## Setup
### Prepare environment
- Clone the repository: `git clone https://github.com/zdytch/ib-web-telegram.git`
- Switch to the project directory: `cd /path/to/project/directory`
- Create a copy of environment file from the sample: `cp .env.sample .env`
- Open .env file with any text editor, e.g.: `nano .env`
- You will see variables with sample values. Replace the values with your own ones

### Prepare Telegram bot
- Register a new bot with [BotFather](https://t.me/botfather) and get a token

### Environment variables explained
- TELEGRAM_TOKEN: telegram bot token
- TELEGRAM_USER_ID: telegram user ID to communicate with the bot. For security reasons, messages from only single user ID are accepted, all others will be rejected. You can get your ID [here](https://t.me/username_to_id_bot)
- IB_ACCOUNT: account ID, usually displayed in the upper right corner of TWS app
- IB_USER: username of IB account
- IB_PASSWORD: password of IB account

- COMPOSE_PROJECT_NAME: used by docker engine to label images, doesn't affect the application

### Setup Docker
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

## Run
- Switch to the project folder: `cd /path/to/project/directory`
- Run: `docker compose up --build`

## Usage
In Telegram app, logged as user with permitted ID
Send `/start` command
Send `/positions` command to display open positions
Send `/orders` command to display open orders
Use buttons to display or cancel positions or orders
