import logging
import tweepy
import time
import os
import random
from send_to_me import send_to_me
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)


def main(n=200, target_followers=600):
    try:
        auth = tweepy.OAuthHandler(
            os.getenv("CONSUMER_KEY"), os.getenv("CONSUMER_SECRET"))
        auth.set_access_token(os.getenv("ACCESS_TOKEN"),
                              os.getenv("ACCESS_TOKEN_SECRET"))
        api = tweepy.API(auth)
        # Get followers first so we don't accidentally unfollow a new follow.
        followers = api.get_friend_ids()
        filename = "followings.txt"
        if os.path.isfile(filename):
            with open(filename, "r") as f:
                bot_followers = [int(x.strip())
                                 for x in f.read().split("\n") if x.strip()]
        else:
            bot_followers = []

        q = "podcast OR #PRPros OR #communications OR #prsa OR #prssa OR #prsaicon OR #publicrelations OR #comms"

        followed = []
        for page in range(1, 51):
            try:
                logging.info(f"Finding users - Page {page}")
                users = api.search_users(
                    q, page=page)
                user_ids = list(
                    set([user.id for user in users if user.id not in followers]))
                for user_id in user_ids:
                    time.sleep(2)
                    try:
                        api.create_friendship(user_id=user_id)
                    except Exception as e:
                        logging.error(e)
                        continue
                    logging.info(f"[twitter-bot] followed: {user_id}")
                    followed.append(user_id)
                    if len(followed) == n:
                        break
                if len(followed) == n:
                    break
            except Exception as e:
                logging.error(e)
                break

        if not user_ids:
            send_to_me(
                "#twitterbot Could not find any handles for the search query or an error occurred while searching for users"
            )
            return

        unfollowed = 0
        target_followers = random.randint(
            target_followers-10, target_followers)
        if len(followers) + len(followed) > target_followers:
            # Unfollow some.
            to_unfollow = len(followers) + len(followed) - target_followers
            while unfollowed < to_unfollow and len(bot_followers) > 0:
                u = random.choice(bot_followers)
                api.destroy_friendship(user_id=u)
                logging.info(f"[twitter-bot] unfollowed: {u}")
                bot_followers.remove(u)
                unfollowed += 1

        with open(filename, "w") as f:
            f.write(
                "\n".join([str(x) for x in bot_followers] + [str(x) for x in followed]))

        new_followers = api.get_friend_ids()

        send_to_me("Twitter Bot Daily Update\n\nFollowed Today: " +
                   str(len(followed)) + "\nUnfollowed Today: " + str(unfollowed) + "\nTotal Followings: " + str(len(new_followers)))
    except Exception as e:
        send_to_me("[twitter-bot] ran into an error: " + str(e))
        logging.info(e)


if __name__ == "__main__":
    main(60, 250)
