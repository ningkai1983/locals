"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
import json
from django.core.serializers.json import DjangoJSONEncoder
from taskQ import tasks
import time

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class ProfileTestCase(TestCase):
    def setUp(self):
        pass
        #self.lion = Profile.objects.create(name="lion", sound="roar")
        #self.cat = Profile.objects.create(name="cat", sound="meow")

    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        #self.assertEqual(self.lion.speak(), 'The lion says "roar"')
        #self.assertEqual(self.cat.speak(), 'The cat says "meow"')
        self.assertEqual(1, 1)

fp = open('main/test.jpg', 'rb')

testAccount1 = {'username': 'ningkai', 'password': 'pass', 'email':'a@a.net', 'image': fp, 'firstName': 'a', 'lastName': 'bbb'}
testAccount2 = {'username': 'superb', 'password': 'pass', 'email':'b@abc.net', 'image': fp}

def buildImageParam(image):
    return {'image': open(image, 'rb')
            }

#def login(client, testAccount=testAccount1):
#    fbId = testAccount['fbId']
#    token = testAccount['token']
#    response = client.post('/peek/', {'content': json.dumps({'fbId': fbId}, cls=DjangoJSONEncoder)})
#    # {"salt":secureCode, "type":peekType}
#    content = json.loads(response.content)
#    content = content['content']
#    salt = content['salt']
#    peekType = content['type']
#    if (peekType == 1):
#        response = client.post('/login/', wrapRequest({'fbId': fbId, 'salted': Util.generateHash(fbId, salt)}, cls=DjangoJSONEncoder))
#    elif (peekType == 0):
#        response = client.post('/register/', wrapRequest({'fbId': fbId, 'salted': Util.generateHash(fbId, salt), 'facebookToken': token}))
#        # client.get('/signupFriends/?facebookToken=' + token + '&fbId=' + fbId)
#
#    return response, client

def wrapRequest(data):
    return {'content': json.dumps(data, cls=DjangoJSONEncoder)}

class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
#    def test_Register(self):
#        with open('main/test.jpg', 'rb') as fp:
#            self.client.post('/register/', {'name': 'fred', 'attachment': fp})
    
    def test_Login(self):
        response = self.client.post('/register/', testAccount1)
        response = self.client.post('/login/', {'username': testAccount1['username'], 'password': testAccount1['password']})
        uploadPackage = {'tags': ['room', 'global'], 'lat': 1.0, 'lon':4.0, 'image': open('main/test.jpg', 'rb'), 'title': 'hahatitle' }
        self.client.post('/upload/', uploadPackage)
        response = self.client.post('/getAround/', {'lat': 1.0, 'lon': 4.0, 'category':'', 'page': 0})
        print response
#        content = json.loads(response.content)

        self.assertEqual(200, response.status_code)

#class PostImageTestCase(TestCase):
#    def setUp(self):
#        self.client = Client()
#    
#    def test_Post(self):
#        response = self.client.post('/register/', {'content': json.dumps(testAccount1, cls=DjangoJSONEncoder)})
        

#class CreateImpressionTestCase(TestCase):
#    def setUp(self):
#        self.client = Client()
#
#    def test_CreateAndRemoveOnSelf(self):
#        response, self.client = login(self.client)
#        self.assertEqual(200, response.status_code)
#
#        # test normal creation
#        self.client.post('/addImpression/', wrapRequest({'targetFbIdString':'3436158', 'isAnonymous': False, 'words':'it\'s a content', 'rating':3, 'tag':['job']}))
#        self.client.post('/addImpression/', wrapRequest({'targetFbIdString':'3436158', 'isAnonymous': False, 'words':'it\'s two content', 'rating':5, 'tag':['job']}))
#        
#        profile = Profile.findOne({'_id': "FB_3436158"})
#        self.assertEqual(4, profile['average'])
#
#        self.client.post('/getProfile/', wrapRequest({'targetId':'FB_3436158', 'page': 0, 'order': 0}))
#        self.client.post('/getProfile/', wrapRequest({'targetId':'FB_3436158', 'page': 0, 'order': 2}))
#        
#        for impression in Impression.find({}):
##            print impression
#            key = impression['_id']
##            print key
#        self.client.post('/remove/', wrapRequest({'key':str(key)}))     
#        
#        # test anonymously creation with credits deduction
#        account = Account.objects.get(fbId='3436158')
#        self.assertEqual(35, account.credits)
#
#        self.client.post('/addImpression/', wrapRequest({'targetFbIdString':'3436158', 'isAnonymous': True, 'words':'it\'s anonymous content', 'rating':5, 'tag':['job']}))
#        self.client.post('/addImpression/', wrapRequest({'targetFbIdString':'3436158', 'isAnonymous': True, 'words':'it\'s two anonymous content', 'rating':1, 'tag':['job']}))
#
#        response = self.client.post('/getProfile/', wrapRequest({'targetId':'FB_3436158', 'page': 0, 'order': 0}))
#        result = json.loads(response.content)
#        self.assertEqual(3.0, result['content']['profile']['average'])
#        self.assertEqual(3, len(result['content']['impressions']['result']))
#        
#        account = Account.objects.get(fbId='3436158')
#        self.assertEqual(25, account.credits)
#        
#        # like an impression        
#        impressionId = result['content']['impressions'][0]['key']
#        response = self.client.post('/like/', wrapRequest({'iId':impressionId}))
#        response = self.client.post('/getProfile/', wrapRequest({'targetId':'FB_3436158', 'page': 0, 'order': 0}))
#        result = json.loads(response.content)
#        self.assertEqual(1, result['content']['impressions'][0]['likeCount'])
#
#        # unlike the impression
#        response = self.client.post('/unlike/', wrapRequest({'iId':impressionId}))
#        response = self.client.post('/getProfile/', wrapRequest({'targetId':'FB_3436158', 'page': 0, 'order': 0}))
#        result = json.loads(response.content)
#        self.assertEqual(0, result['content']['impressions'][0]['likeCount'])
#
#    '''
#    register 2 accounts, update one and get the newsfeed for the other one
#    '''
#    def test_NewsFeed(self):
#        
#        # signup with account2
#        aClient = Client()
#        r, aClient = login(aClient, testAccount2)
#        
#        # clear the account and signup with account1
#        response, self.client = login(self.client)
#        self.assertEqual(200, response.status_code)
#        
#        response = self.client.post('/getProfile/', wrapRequest({'targetId':'FB_3436158', 'page': 0, 'order': 0}))
#        #print response
#        self.client.post('/addImpression/', wrapRequest({'targetFbIdString':'216743', 'isAnonymous': False, 'words':'it\'s a content', 'rating':3, 'tag':['job']}))
#        self.client.post('/addImpression/', wrapRequest({'targetFbIdString':'216743', 'isAnonymous': True, 'words':'it\'s anonymous content', 'rating':5, 'tag':['job']}))
#        
#        impressions = Impression.objects.all()
#        for impression in impressions:
#            #self.client.get('/addToFollower/?impressionId=' + impression.id)
#            self.client.post('/addComment/', wrapRequest({'impressionId': impression.id, 'isAnonymous':False, 'content':'wahahahahaah'}))
#            self.client.post('/addComment/', wrapRequest({'impressionId': impression.id, 'isAnonymous':True, 'content':'wahahahahaah'}))
#        
#        #for action in Action.objects.all():
#            #print action.actionKey + action.fromKey + action.toKey + action.actionName
#            #print action.newsFeed
#        # login(aClient, testAccount2)
#        response = aClient.post('/getNewsFeed/', wrapRequest({'page': 0}))
#        obj = json.loads(response.content)
#        self.assertEqual(1, len(obj['content']['feeds']))
#        
#        # get activities for a friend
#        response = self.client.get('/getActivities/', wrapRequest({'page': 0, 'fbId': '216743'}))
#        obj = json.loads(response.content)
#        self.assertEqual(6, len(obj['content']['activity']))
#
#        # get activities for oneself
#        response = self.client.get('/getActivities/', wrapRequest({'page': 0, 'fbId': '3436158'}))
#        obj = json.loads(response.content)
#        self.assertEqual(6, len(obj['content']['activity']))
#
#        # get activities for someone not related
#        response = aClient.get('/getActivities/', wrapRequest({'page': 0, 'fbId': '216743'}))
#        obj = json.loads(response.content)
#        self.assertEqual(6, len(obj['content']['activity']))
#        self.assertEqual(0, obj['content']['page'])
#        
#        # get activities for someone not related
#        response = aClient.get('/getActivities/', wrapRequest({'page': 0, 'fbId': '3436158'}))
#        obj = json.loads(response.content)
#        self.assertEqual(3, len(obj['content']['activity']))
#        self.assertEqual(0, obj['content']['page'])
#        
#        # remove a comment
#        response = self.client.post('/getImpression/', wrapRequest({'impressionId': obj['content']['activity'][0]['actionKey'], 'page': 0}))
#        obj = json.loads(response.content)
#        commentId = obj['content']['comments'][0]['key']
#        response = self.client.post('/removeComment/', wrapRequest({'commentId': commentId}))
#        response = self.client.post('/getProfile/', wrapRequest({'targetId':'FB_3436158', 'page': 0, 'order': 0}))
#        response = self.client.post('/getProfile/', wrapRequest({'targetId':'FB_216743', 'page': 0, 'order': 0}))
#        print response
#
#        # get activities for oneself
#        response = self.client.get('/getActivities/', wrapRequest({'page': 0, 'fbId': '3436158'}))
#        obj = json.loads(response.content)
#        self.assertEqual(6, len(obj['content']['activity']))
#
#class AsyncTaskTestCase(TestCase):
#    def setUp(self):
#        self.client = Client()
#
#    def test_addFriendsTest(self):
#        response, self.client = login(self.client)
#        
#        profile = Profile.objects.get(key='FB_3436158')
#        followingIndex = profile.followingIndex
#        self.assertGreater(len(followingIndex.keys), 200)
#    
#    def test_addImpressionTest(self):
#        pass
#
#class BaseModelTestCase(TestCase):
#    def test_simpleTest(self):
#        profile = Profile.objects.create(key="FB_123",firstName='firstName',lastName='lastName',fbId='123',followerIndex=FollowerIndex.objects.create(),followingIndex=FollowerIndex.objects.create(),friendList=FriendList.objects.create())
#        profile.save()
#        queryResult= Profile.findOne({'_id': "FB_123"})
#        self.assertEqual('firstName', queryResult['firstName'])
#        
#        queryResult = Profile.findOne({'_id': "FB_123"}, {'lastName': True})
#        self.assertEqual('lastName', 'lastName')
#        self.assertNotIn('firstName', queryResult)
        

        
        