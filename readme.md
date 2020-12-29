# StreamBot

StreamBot is an easy-to-use and low-resource consuming bot. It currently only supports Twitch, but there are plans in the future to extend it to other services (like Facebook and YouTube).

  - Base bot (bot.py) simply handles the starting of the service. Easily create new python script files and call them.
  - StreamBot comes out-of-the-box with support for...
     - Repeating messages (loops messages on a timer)
     - "!draw" command to track score of users who guess a drawing correctly.
     - "!ttt" command to spawn a tic-tac-toe game instance between two users.
     - "!discord" command to reply with a Discord link.
     - "!charity" command to reply with the link to a charity event.
     - "!commands" command to reply with a list of commands.

Configuration is easy, simply update the .env file with your Twitch channel information.

To see StreamBot in action live, visit our Twitch channel twitch.tv/4FeetApart.