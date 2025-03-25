import discord
from discord.ext import commands
from discord import app_commands
import datetime
import pytz
from database import Database

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @app_commands.command(name="taskhelp", description="Get help on how to use the task manager")
    async def taskhelp(self, interaction: discord.Interaction):
        """Show help information about how to use the task manager."""
        embed = discord.Embed(
            title="📋 Task Manager Help Guide",
            description="Here's how to use the task manager commands:",
            color=discord.Color.blue()
        )

        # Add Task Command
        embed.add_field(
            name="📝 Adding Tasks",
            value="Use `/addtask` to create a new task:\n"
                  "• `title`: Name of your task\n"
                  "• `description`: What needs to be done\n"
                  "• `due_date`: When it's due (YYYY-MM-DD HH:MM)\n"
                  "• `priority`: low/medium/high\n"
                  "• `assignee`: (Optional) Who to assign it to\n\n"
                  "Example:\n"
                  "`/addtask title:\"Study Python\" description:\"Learn about async/await\" "
                  "due_date:\"2024-03-26 20:00\" priority:\"high\"`",
            inline=False
        )

        # View Tasks Command
        embed.add_field(
            name="👀 Viewing Tasks",
            value="Use `/tasks` to see your tasks:\n"
                  "• Shows all tasks you created or are assigned to\n"
                  "• Optional: Filter by status (pending/in_progress/completed)\n\n"
                  "Example:\n"
                  "`/tasks status:completed`",
            inline=False
        )

        # Complete Task Command
        embed.add_field(
            name="✅ Completing Tasks",
            value="Use `/completetask` to mark a task as done:\n"
                  "• `task_id`: The ID number of the task\n"
                  "• Only works for tasks you created or are assigned to\n\n"
                  "Example:\n"
                  "`/completetask task_id:1`",
            inline=False
        )

        # Delete Task Command
        embed.add_field(
            name="🗑️ Deleting Tasks",
            value="Use `/deletetask` to remove a task:\n"
                  "• `task_id`: The ID number of the task\n"
                  "• Only the task creator can delete tasks\n\n"
                  "Example:\n"
                  "`/deletetask task_id:1`",
            inline=False
        )

        # Tips Section
        embed.add_field(
            name="💡 Tips",
            value="• Use `/tasks` to find task IDs\n"
                  "• Tasks are sorted by due date\n"
                  "• You can only delete tasks you created\n"
                  "• Anyone assigned to a task can complete it",
            inline=False
        )

        embed.set_footer(text="Need more help? Contact the server administrator")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addtask", description="Add a new task")
    async def add_task(self, interaction: discord.Interaction, title: str, description: str, 
                      due_date: str, priority: str, assignee: discord.Member = None):
        """Add a new task with title, description, due date, priority, and optional assignee."""
        # Validate priority
        if priority.lower() not in ['low', 'medium', 'high']:
            await interaction.response.send_message("Priority must be 'low', 'medium', or 'high", ephemeral=True)
            return

        # Parse due date (expected format: YYYY-MM-DD HH:MM)
        try:
            due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d %H:%M")
            due_date = pytz.UTC.localize(due_date).isoformat()
        except ValueError:
            await interaction.response.send_message("Invalid date format. Please use YYYY-MM-DD HH:MM", ephemeral=True)
            return

        # Add task to database
        task_id = await self.db.add_task(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority.lower(),
            created_by=interaction.user.id,
            assigned_to=assignee.id if assignee else None
        )

        # Create embed for response
        embed = discord.Embed(
            title="Task Created",
            description=f"Task ID: {task_id}",
            color=discord.Color.green()
        )
        embed.add_field(name="Title", value=title, inline=False)
        embed.add_field(name="Description", value=description, inline=False)
        embed.add_field(name="Due Date", value=due_date, inline=True)
        embed.add_field(name="Priority", value=priority.capitalize(), inline=True)
        if assignee:
            embed.add_field(name="Assigned To", value=assignee.mention, inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tasks", description="View your tasks")
    async def view_tasks(self, interaction: discord.Interaction, status: str = None):
        """View all tasks assigned to you or created by you, optionally filtered by status."""
        if status and status.lower() not in ['pending', 'in_progress', 'completed']:
            await interaction.response.send_message("Status must be 'pending', 'in_progress', or 'completed", ephemeral=True)
            return

        tasks = await self.db.get_user_tasks(interaction.user.id, status.lower() if status else None)
        
        if not tasks:
            await interaction.response.send_message("No tasks found!", ephemeral=True)
            return

        embed = discord.Embed(
            title="Your Tasks",
            color=discord.Color.blue()
        )

        for task in tasks:
            status_emoji = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅'
            }.get(task['status'], '❓')

            value = f"**Description:** {task['description']}\n"
            value += f"**Due:** {task['due_date']}\n"
            value += f"**Priority:** {task['priority'].capitalize()}\n"
            value += f"**Status:** {status_emoji} {task['status'].replace('_', ' ').capitalize()}\n"
            
            if task['assigned_to']:
                value += f"**Assigned to:** <@{task['assigned_to']}>"

            embed.add_field(
                name=f"Task #{task['id']}: {task['title']}",
                value=value,
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="completetask", description="Mark a task as completed")
    async def complete_task(self, interaction: discord.Interaction, task_id: int):
        """Mark a task as completed."""
        task = await self.db.get_task(task_id)
        
        if not task:
            await interaction.response.send_message("Task not found!", ephemeral=True)
            return

        if task['created_by'] != interaction.user.id and task['assigned_to'] != interaction.user.id:
            await interaction.response.send_message("You don't have permission to complete this task!", ephemeral=True)
            return

        await self.db.update_task_status(task_id, 'completed')
        await interaction.response.send_message(f"Task #{task_id} marked as completed! ✅")

    @app_commands.command(name="deletetask", description="Delete a task")
    async def delete_task(self, interaction: discord.Interaction, task_id: int):
        """Delete a task."""
        task = await self.db.get_task(task_id)
        
        if not task:
            await interaction.response.send_message("Task not found!", ephemeral=True)
            return

        if task['created_by'] != interaction.user.id:
            await interaction.response.send_message("Only the task creator can delete this task!", ephemeral=True)
            return

        await self.db.delete_task(task_id)
        await interaction.response.send_message(f"Task #{task_id} deleted! 🗑️")

async def setup(bot):
    await bot.add_cog(Tasks(bot)) 