import csv 
from datetime import datetime, timedelta 
import random
date_and_time = ['2024-01-01 09:19:45', '2024-01-17 14:02:27', '2024-01-21 06:38:27', 
                '2024-02-16 07:25:53', '2024-02-23 05:19:14', '2024-03-07 16:15:12', 
                '2024-03-09 14:11:03', '2024-04-04 19:20:56', '2024-04-16 19:08:41', 
                '2024-04-26 03:40:04', '2024-05-09 09:15:53', '2024-06-01 20:40:17', 
                '2024-06-04 15:40:04', '2024-06-14 21:39:45', '2024-06-25 21:03:02', 
                '2024-07-23 12:12:50', '2024-07-26 08:45:34', '2024-07-31 23:00:25', 
                '2024-08-20 05:33:43', '2024-08-28 21:50:29', '2024-09-04 11:17:50', 
                '2024-10-02 21:46:14', '2024-10-15 03:35:27', '2024-10-18 22:37:17', 
                '2024-11-05 21:39:15', '2024-11-06 09:49:58', '2024-11-26 17:50:05', 
                '2024-12-09 11:36:29', '2024-12-24 08:54:05', '2025-01-05 04:38:47', 
                '2025-01-23 20:39:38', '2025-01-29 18:28:08', '2025-02-05 21:08:44', 
                '2025-03-06 04:33:49', '2025-03-20 02:42:30', '2025-03-21 02:40:46', 
                '2025-04-04 15:41:18', '2025-04-19 20:32:44', '2025-05-10 11:24:37', 
                '2025-05-11 03:37:35', '2025-05-22 15:16:28', '2025-05-28 07:10:20', 
                '2025-06-18 08:56:57', '2025-07-16 06:45:18', '2025-08-08 19:25:14']

positive_feedbacks = [
    "The spicy miso ramen was absolutely perfect!",
    "Incredible broth, so rich and flavorful. I'll be dreaming about it tonight.",
    "Our server was so friendly and attentive. She really made our night.",
    "This is hands-down the best noodle spot in the city.",
    "The pork belly topping was melt-in-your-mouth delicious.",
    "Service was incredibly fast, even during the dinner rush.",
    "I love the ambiance here. The music and decor are fantastic.",
    "The presentation of the food was beautiful.",
    "Everything tasted so fresh and high-quality.",
    "We had a wonderful family dinner. Thank you for the great experience!",
    "The vegan ramen is outstanding. So glad you have great plant-based options.",
    "Great portion sizes for the price. Excellent value.",
    "The restaurant was spotlessly clean, which we really appreciate.",
    "Came for the noodles, and was blown away by the amazing appetizers.",
    "A perfect meal from start to finish. We will be back soon!",
    "The staff handled my food allergy with great care and professionalism.",
    "The online ordering process was smooth and my food was ready right on time.",
    "Your new seasonal special is a huge hit. Loved it!",
    "The noodles had the perfect texture and chewiness.",
    "A truly authentic and wonderful dining experience.",
    "The chicken was so tender and juicy.",
    "We were seated immediately and the service was prompt.",
    "The gyoza were crispy and delicious.",
    "A cozy and welcoming atmosphere.",
    "Worth every penny. A fantastic meal.",
    "The staff were knowledgeable and gave great recommendations.",
    "The spicy level was just right - flavorful with a good kick.",
    "My kids loved their food, which is a huge win!",
    "The cocktails pair perfectly with the ramen.",
    "Consistently excellent every time we visit.",
    "The soft-boiled egg was cooked to perfection.",
    "I brought a friend here for the first time and they were so impressed.",
    "Quick, delicious, and satisfying. The perfect lunch.",
    "The attention to detail is evident in every dish.",
    "Easily a 5-star experience.",
    "The manager stopped by our table to check on us, which was a nice touch.",
    "The chili oil on the table is amazing.",
    "Best ramen I've had since my trip to Japan.",
    "The takeaway packaging was great and kept the food hot.",
    "You have a new regular customer!"
]

negative_feedbacks = [
    "My noodles arrived cold. Very disappointing.",
    "The broth was completely bland and tasted like water.",
    "Service was incredibly slow. We waited over 45 minutes for our food.",
    "Our server was rude and seemed like they didn't want to be there.",
    "The portion size was tiny for the price. I left hungry.",
    "The music was so loud we couldn't even have a conversation.",
    "The table was sticky and clearly hadn't been wiped down properly.",
    "They got my order completely wrong and didn't even apologize.",
    "The chicken in my ramen was dry and overcooked.",
    "This place is way too expensive for the quality you get.",
    "The wait time was an hour, and the food was not worth it.",
    "The noodles were overcooked and mushy.",
    "It was freezing inside the restaurant. We had to keep our coats on.",
    "The 'spicy' ramen had zero heat at all.",
    "I found a hair in my food.",
    "The bathroom was dirty and had no paper towels.",
    "I used to love this place, but the quality has seriously gone downhill.",
    "The staff seemed overwhelmed and disorganized.",
    "The vegetables in my dish were not fresh.",
    "The broth was far too salty, I couldn't finish it.",
    "I made a reservation and still had to wait 30 minutes to be seated.",
    "The server forgot to bring our drinks until we were halfway through our meal.",
    "The online menu is different from the in-store menu. Very confusing.",
    "The vegetarian options are very limited and uninspired.",
    "There was a long delay between getting our appetizers and our main courses.",
    "The whole experience felt rushed and impersonal.",
    "The pork was all fat and barely any meat.",
    "The restaurant smelled like old cleaning solution.",
    "I tried calling to place an order and no one ever picked up the phone.",
    "This was a really disappointing birthday dinner.",
    "The egg was hard-boiled, not soft-boiled as described.",
    "The bill was incorrect and it was a hassle to get it fixed.",
    "The noodles were all stuck together in a clump.",
    "The ambiance is gone. It just feels like a generic cafeteria now.",
    "I won't be coming back."
]

neutral_feedbacks = [
    "The food was delicious, but the service was quite slow.",
    "The portion sizes are fair.",
    "It was an okay experience, but nothing special.",
    "The noodles were great, but I thought the music was a bit too loud.",
    "The restaurant was busy when we arrived.",
    "The flavor was good, but the soup could have been hotter.",
    "It's a decent place for a quick lunch.",
    "The service was friendly, but they seemed a little understaffed.",
    "The broth is good, but I wish you had more topping options.",
    "The experience was pretty much what I expected.",
    "The prices are a little high, but the food quality is good.",
    "The ambiance is nice, although my dish was just average.",
    "It would be helpful if you had nutritional information on your menu.",
    "The food was fine, but the wait was longer than I would have liked.",
    "Your restaurant is conveniently located.",
    "The menu has a good variety of options.",
    "The dish was good, just not exactly what I was expecting from the description.",
    "The seating is a little cramped.",
    "It was a standard noodle restaurant experience.",
    "I liked my meal, but my friend didn't enjoy hers.",
    "The spice level was more intense than I anticipated.",
    "It gets very crowded on weekends.",
    "The server was efficient but not overly friendly.",
    "The food came out at different times for everyone at our table.",
    "It's a reliable option, though not my absolute favorite."
]


n = 0

while n < 500:
    with open("./feedback.csv", "a+") as file:
        all_feedbacks = positive_feedbacks + negative_feedbacks + neutral_feedbacks
        customer_feedback = random.choice(all_feedbacks)
        date_time = random.choice(date_and_time)
        input_inventory = f"Date and time: {date_time} | customer feedback: {customer_feedback}\n"
        file.write(input_inventory)
        n += 1




    

