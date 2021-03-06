from bson.objectid import ObjectId

thread1 = {
    "title": "Hello Chris! This is the title of a thread",
    "username": "Aaron, the creator of this thread",
    "first_message": "The first main message that starts the thread off goes here. Let me know if anything needs to be restructured to make it easier to display/ function, or if you want to display it a different way!",
    "likes": [],
    "messages": [{"message_id": "id I will generate for you to be referenced in replies", "username": "user who sent this message", "message": "Whatever could this be?",
    "replies": [
        {
        "reply_id": "987",
        "username": "user who sent this reply",
        "reply": "The first reply to this message",
        "reply_to": "Is this a reply to another user who has replied or is it just a reply to the original message in which case ''"
        },
        {
        "reply_id": "986",
        "username": "user",
        "reply": "The second reply to this message",
        "reply_to": ""
        }
    ]},
    {"message_id": '12345', "username": "user1", "message": "user1 has sent another message to view in the thread",
    "replies": [
        {
        "reply_id": "985",
        "username": "user2",
        "reply": "user2 has sent this reply to the main message from user1",
        "reply_to": ""
        },
        {
        "reply_id": "984",
        "username": "user3",
        "reply": "user3 has also sent this reply to the main message",
        "reply_to": ""
        },
        {
        "reply_id": "983",
        "username": "user1",
        "reply": "user1 has replied to user2's message",
        "reply_to": "user2"
        },
        {
        "reply_id": "982",
        "username": "user4",
        "reply": "user4 has replied to user3's message",
        "reply_to": "user3"
        },
        {
        "reply_id": "981",
        "username": "user5",
        "reply": "user5 has sent another reply to the original message not targeted at anyone",
        "reply_to": ""
        }
        
    ]}
    ]
}
thread2 = {
    "_id": ObjectId('62d739a2f981c7f9185af9b2'),
    "title": "A second thread",
    "username": "user1",
    "first_message": "What an original message this is",
    "likes": [],
    "messages": [{"message_id": '11111', "username": "user2", "message": "This is message 1",
    "replies": [
        {
        "reply_id": "887",
        "username": "user3",
        "reply": "The first reply to message 1",
        "reply_to": ""
        },
        {
        "reply_id": "886",
        "username": "user4",
        "reply": "The second reply to message 1",
        "reply_to": ""
        }
    ]},
    {"message_id": '22222', "username": "user5", "message": "This is message 2",
    "replies": [
        {
        "reply_id": "885",
        "username": "user1",
        "reply": "The first reply to message 2",
        "reply_to": ""
        },
        {
        "reply_id": "884",
        "username": "user3",
        "reply": "The second reply to message 2 which is also a reply to user1",
        "reply_to": "user1"
        },
        {
        "reply_id": "883",
        "username": "user5",
        "reply": "Third reply to message 2",
        "reply_to": ""
        }
    ]}
    ]
}
