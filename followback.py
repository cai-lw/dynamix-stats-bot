import twitter
import os

api = twitter.Api(consumer_key=os.environ['CSMR_KEY'],
                  consumer_secret=os.environ['CSMR_SCRT'],
                  access_token_key=os.environ['ACSS_KEY'],
                  access_token_secret=os.environ['ACSS_SCRT'])

followback_ids = list(set(api.GetFollowerIDs()).difference(api.GetFriendIDs()))

if len(followback_ids) > 0:
    for batch in range((len(followback_ids) - 1) // 100 + 1):
        for user in api.UsersLookup(user_id=followback_ids[batch * 100:(batch + 1) * 100]):
            if not user.protected:
                print('Followed @' + user.screen_name)
                api.CreateFriendship(user_id=user.id)
