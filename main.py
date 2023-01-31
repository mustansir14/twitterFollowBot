import tweepy
import time
import os
import random
from send_to_me import send_to_me
from dotenv import load_dotenv
load_dotenv()


def main(n=200):
    try:
        auth = tweepy.OAuthHandler(
            os.getenv("CONSUMER_KEY"), os.getenv("CONSUMER_SECRET"))
        auth.set_access_token(os.getenv("ACCESS_TOKEN"),
                              os.getenv("ACCESS_TOKEN_SECRET"))
        api = tweepy.API(auth)
        # Get followers first so we don't accidentally unfollow a new follow.
        followers = api.get_friend_ids()

        q = "podcast OR #PRPros OR #communications OR #prsa OR #prssa OR #prsaicon OR #publicrelations OR #comms"

        followed = 0
        for page in range(1, 51):
            try:
                users = api.search_users(
                    q, page=page)
                user_ids = list(
                    set([user.id for user in users if user.id not in followers]))
                for user_id in user_ids:
                    try:
                        api.create_friendship(user_id=user_id)
                    except:
                        continue
                    print(f"[twitter-bot] followed: {user_id}")
                    followed += 1
                    if followed == n:
                        break
                if followed == n:
                    break
            except Exception as e:
                print(e)
                break

        if not user_ids:
            send_to_me(
                "#twitterbot Could not find any handles for the search query or an error occurred while searching for users"
            )
            return

        unfollowed = 0
        if len(followers) + followed >= n*3:
            # Unfollow some.

            while unfollowed < n and len(followers) > 0:
                u = random.choice(followers)
                api.destroy_friendship(user_id=u)
                print(f"[twitter-bot] unfollowed: {u}")
                followers.remove(u)
                unfollowed += 1

        new_followers = api.get_friend_ids()

        send_to_me("Twitter Bot Daily Update\n\nFollowed Today: " +
                   str(followed) + "\nUnfollowed Today: " + str(unfollowed) + "\nTotal Followings: " + str(len(new_followers)))
    except Exception as e:
        send_to_me("[twitter-bot] ran into an error: " + str(e))
        print(e)


if __name__ == "__main__":
    main(200)
