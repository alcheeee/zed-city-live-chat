##### Zed City Live Chat

A simple script that will add a live chat to [Zed City](https://www.zed.city/).

Here's how it works.

People are able to change their username/faction that is sent to my server, accessing "private" faction chats, or using whatever username they want. As I do not have access to the Zed City servers, I cannot authenticate user data. 

How it works,

    Your username and faction id are intercepted from a Zed City response (am not including the original script that did this).
    My server takes in your username and faction id as authentication (though any authentication token could be used if it were part of the official game).
    Now your connected!

Notes:
- For faction chat to work, the message needs to be prefixed with /faction (like so: "`/faction Hey guys 1 more needed for raid.`", and the user must be in a faction.
- I was going to add admin commands such as timeout, mute, ban, but I never got around to doing it. It would be extremely easy to add if I had access to token authentication. With limited access a new database would be required.
- The Websocket Manager can be cleaned up, but I made this in about a day so leave me alone.

Features:
- WAS IN USER SCRIPT, NOT HERE -> Mention other users `@chee hello`
- Global chat (anyone with this script will be able to talk!)
- Global chat is cached up to 25 messages, though it's acting a bit weird right now -- will fix.
- "Private" faction chat

DISCLAIMER:
I'm making this repository public. The developers have released their own built-in live chat.
If the developers of Zed City have a problem with this script, please reach out to me on discord (@chee).
