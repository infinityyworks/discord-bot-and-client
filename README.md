# Discord bot and CLI client
A Discord bot which responds to basic user commands. It can be controlled by the operator through the terminal, where it can navigate servers, read and send messages through the bot.

## User commands:

$help: lists all the commands below

$pingself: replies to the user with "@username Hello World!"

$randfloat: sends a random float between 0 and 1

$eightball <question>: ambiguously responds to the user's question, similar to the 8ball  toy

$audit <n>: sends the last n entries in the server's audit log (up to 20)


## CLI commands

.all: prints a hierarchal list of all servers the bot belongs to, with the channels and members in each

.servers: prints all the servers the bot belongs to

.select server: selects a server

.members: prints all the members in the current server

.channels: prints all the channels in the current server

.select channel: selects a channel to enter, and prints the last 50 messages sent in that channel

.ping: repeatedly pings a user, with an optional message attached to each ping

.spam: repeatedly sends a message (split into 2000 character chunks)

.quit: safely disconnect the bot and close the CLI thread

Any other inputs will be sent as messages to the current channel. New messages in the channel will also be streamed to the terminal.
