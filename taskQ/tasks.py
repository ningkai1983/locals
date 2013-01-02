from celery.task.http import URL
import urllib2, urllib
from celery import task
from main.models import *
from bson.objectid import ObjectId  

import json, logging
import sys, traceback, datetime
from sets import Set

logger = logging.getLogger("impression.applog")

FB_PREFIX = 'FB_'

def getProfileKey(fbId):
    return FB_PREFIX + fbId
 
#@task(name="taskQ.tasks.addContentFollowerTask")
#def addContentFollowerTask(impression):
#    try:
#        action = Action.objects.create(fromKey=impression.creator,toKey=impression.target,isAnonymous=impression.isAnonymous,actionKey=impression.id,actionType=ActionType.CreateImpression, content=impression.content)
#        targetProfile = impression.target
#    
#        if impression.isAnonymous:
#            # add it to target followers only
#            action.newsFeed = targetProfile.followerIndex.keys
#        else:
#            # add to both source and target
#            sourceProfile = impression.creator
#            action.newsFeed = set.union(set(sourceProfile.followerIndex.keys), set(targetProfile.followerIndex.keys))
#        action.activityFeed = set([impression.creator.key, impression.target.key])
#        action.save()
#    except Exception as e:
#        traceback.print_exc(file=sys.stdout)
#    
#    return 
#    #return urllib2.urlopen(LOCAL_URL + ADD_TO_FOLLOWER_ENDPOINT + '/?impressionId=' + str(impressionId)).read()
#    #res = URL('http://example.com/multiply').get_async(x=10, y=10)
#
#@task(name="taskQ.tasks.addLikeFollowerTask")
#def addLikeFollowerTask(impressionId, creatorId):
#    try:
#        impression = Impression.objects.get(id=ObjectId(impressionId))
#        targetProfile = impression.target#Profile.objects.get(_id=term['targetKey'])
#        likeCreatorProfile = Profile.objects.get(key=creatorId)
#        action = Action.objects.create(fromKey=likeCreatorProfile,toKey=impression.target,isAnonymous=False,actionKey=impressionId,actionType=ActionType.Like,content=impression.content)
#        action.newsFeed = set.union(targetProfile.followerIndex.keys, [impression.creator.key, likeCreatorProfile.key])
#        action.activityFeed = set([impression.creator.key, impression.target.key])
#        action.save()
#    except Exception as e:
#        traceback.print_exc(file=sys.stdout)
#    return 
#
## sourceId input promo code of targetId
#@task(name="taskQ.tasks.applyCodeTask")
#def applyCodeTask(sourceId, targetId):
#    try:
#        sourceProfile = Profile.objects.get(key=sourceId)
#        targetProfile = Profile.objects.get(key=targetId)
#        action = Action.objects.create(fromKey=sourceProfile,toKey=targetProfile,isAnonymous=False,actionKey="",actionType=ActionType.PromoCode,content="")
#        action.newsFeed = set([targetProfile.key])
#        action.activityFeed = set([sourceProfile.key])
#        action.save()
#    except Exception as e:
#        traceback.print_exc(file=sys.stdout)
#    return
##    return wrapHttpResponse({"status":"success"})
##
##    return urllib2.urlopen(LOCAL_URL + ADD_LIKE_TO_FOLLOWER_ENDPOINT + '/?impressionId=' + str(impressionId) + '&creatorId=' + str(creatorId)).read()
#
#@task(name="taskQ.tasks.addToNewsFeedV2Task")
#def addToNewsFeedV2Task(sourceId, targetId):
#    try:
#        Action.objects.raw_update({"targetId": targetId}, {"$addToSet": {"newsFeed": sourceId}})
#        Action.objects.raw_update({"sourceId": targetId, "isAnonymous": False}, {"$addToSet": {"newsFeed": sourceId}})
#    except Exception as e:
#        traceback.print_exc(file=sys.stdout)
#    return
#
## add A to B's action's newsFeed
#@task(name="taskQ.tasks.addToNewsFeed")
#def addToNewsFeed(sourceId, targetId):
#    try:
#        Action.objects.raw_update({"activityFeed": targetId}, {"$addToSet": {"newsFeed": sourceId}})
#    except Exception as e:
#        traceback.print_exc(file=sys.stdout)
#    return 
##    return urllib2.urlopen(LOCAL_URL + ADD_TO_NEWSFEED_ENDPOINT + '/?fbId=' + str(sourceId) + '&targetId=' + str(targetId)).read()
#
## add A to B's action's newsFeed
#@task(name="taskQ.tasks.addCommentFollowerTask")
#def addCommentFollowerTask(comment, impressionId, impression):
#    try:
#        action = Action.objects.create(fromKey=comment.creator,toKey=comment.target,isAnonymous=comment.isAnonymous,actionKey=impressionId,actionType=ActionType.Comment, content=str(comment.content))
#        action.newsFeed = set.union(set(impression.involvers), [comment.creator.key])
#        action.activityFeed = set([comment.creator.key, comment.target.key])
#        action.save()
#    except Exception as e:
#        traceback.print_exc(file=sys.stdout)
#    return 
#
#@task(name="taskQ.tasks.addFriendProfileTask")
#def addFriendProfileTask(token, fbId):
#    url = "https://graph.facebook.com/" + fbId + "/friends/?fields=first_name,last_name&access_token=" + token
#    try:
#        loop = True
#        keySet = Set([])
#        while loop:
#            response = urllib2.urlopen(url).read()
#            friends = json.loads(response)
#            if 'data' in friends:
#                for friend in friends['data']:
#                    try:
#                        friendKey = getProfileKey(friend['id'])
#                        meKey = getProfileKey(fbId)
#                        keySet.add(friendKey)
#                        try:
#                            profile = Profile.objects.get(key=friendKey)
#                        except Profile.DoesNotExist:
#                            profile = Profile.objects.create(key=friendKey,firstName=friend['first_name'],lastName=friend['last_name'],fbId=friend['id'],followerIndex=FollowerIndex.objects.create(),followingIndex=FollowerIndex.objects.create(),friendList=FriendList.objects.create())
#                            profile.save()
#                            
#                        followerIndex = profile.followerIndex
#                        FollowerIndex.objects.raw_update({"_id": ObjectId(followerIndex.id)}, {"$addToSet": {"keys": meKey}})
#                        
#                        if Account.objects.filter(profile=profile):
#                            # mean account exists, then add the fbId to friend's following list
#                            followingIndex = profile.followingIndex
#                            FollowerIndex.objects.raw_update({"_id": ObjectId(followingIndex.id)}, {"$addToSet": {"keys": meKey}})
#                            addToNewsFeedV2Task.delay(meKey, friendKey)
#                    except Exception as e:
#                        traceback.print_exc(file=sys.stdout)
#
#            loop = False                
#            if 'paging' in friends:
#                if 'next' in friends['paging']:
#                    url = friends['paging']['next']
#                    loop = True
#        
#        profile = Profile.objects.get(key=getProfileKey(fbId))
#        followingIndex = profile.followingIndex
#        followingIndex.addKeys(keySet)
#        followingIndex.save()
#        friendList = profile.friendList
#        friendList.addKeys(keySet)
#        friendList.save()
#    except Exception as e:
#        traceback.print_exc(file=sys.stdout)
#            
#    return
#
## post status message on facebook
#@task(name="taskQ.tasks.postStatus")
#def postStatusToFacebook(token, impression):
#    sourceProfile = impression.creator
#    targetProfile = impression.target
#    url = "https://graph.facebook.com/" + impression.target.fbId + "/feed/?access_token=" + token
#    '''
#                link: "https://itunes.apple.com/us/app/impressions./id516864195?ls=1&mt=8",
#                name: "Impressions App",
#                caption: "The only app that allows you to comment your friend anonymously!",
#                //picture: "http://developer.appcelerator.com/assets/img/DEV_titmobile_image.png",
#                description: "Come and join millions of users that give friends 5 star ratings!",
#
#    '''
#    data = {'link': "https://itunes.apple.com/us/app/impressions./id516864195?ls=1&mt=8",
#            'name': "Impressions App",
#            'caption': "The only app that allows you to comment your friend anonymously!",
#            'description': "Come and join millions of users that give friends 5 star ratings!",
#            }
#    try:
#        data['message'] = ' '.join(["I just created an Impression for", targetProfile.firstName, targetProfile.lastName])
#        data['message'] = data['message'] + '\n' + impression.content
#        urllib2.urlopen(url, urllib.urlencode(data)).read()
#    except Exception:
#        traceback.print_exc(file=sys.stdout)
#    
#    return 
