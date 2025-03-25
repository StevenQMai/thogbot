# Discord Task Manager Bot

A Discord bot that helps users manage their tasks and productivity within Discord servers.

## Features

- Create and manage tasks with titles, descriptions, and due dates
- Set task priorities (low, medium, high)
- Assign tasks to other users
- Track task status (pending, in progress, completed)
- View tasks with beautiful embed messages
- Delete tasks (creator only)
- Filter tasks by status

## Commands

- `/addtask` - Create a new task
  - Parameters: title, description, due_date (YYYY-MM-DD HH:MM), priority (low/medium/high), assignee (optional)
- `/tasks` - View your tasks
  - Optional parameter: status (pending/in_progress/completed)
- `/completetask` - Mark a task as completed
  - Parameter: task_id
- `/deletetask` - Delete a task
  - Parameter: task_id (creator only)

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Discord bot token:
   ```
   DISCORD_TOKEN=your_token_here
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

## Requirements

- Python 3.8+
- discord.py
- python-dotenv
- aiosqlite
- pytz

