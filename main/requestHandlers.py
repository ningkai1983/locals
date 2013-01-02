'''
Created on Jul 11, 2012

@author: kaining
'''
from django.views.generic import View
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.db import connections

#from taskQ.tasks import addContentFollowerTask, addFriendProfileTask, addLikeFollowerTask, addCommentFollowerTask, applyCodeTask, postStatusToFacebook

from bson.objectid import ObjectId  

from main.models import *
from main.exceptions import * 
from main.common import *

import urllib2, json, datetime, logging, base64, pymongo, sys, traceback

from boto.s3.connection import S3Connection
conn = S3Connection('AKIAJQD3IYLGJOBU2RJA', '6uYfKcl2w1wuo2wxROL2JnWl5Z/sE3pPPSv75k5V')
from boto.s3.key import Key
bucket = conn.create_bucket('kainingsupermybucket')

logger = logging.getLogger("impression.applog")
conn = connections['default']

RESULT_PER_PAGE = 10

def getValueFromDict(key, dic, default):
    if key in dic:
        return dict['key']
    return default

class ParamWrapper():
    
    def __init__(self):
        self.data = {}
        self.request = {}
        self.response = {}

class BaseView(View):
    '''
    classdocs
    This is the abstract class for all servlets, including parsing request
    '''
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(BaseView, self).dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        return self.process(request, request.GET);
    
    def post(self, request, *args, **kwargs):
        return self.process(request, request.POST);
    
    def requireLogin(self):
        raise NotImplementedError( "Should have implemented this function requireLogin" )

    def processData(self, request):
        raise NotImplementedError( "Should have implemented this function processData" )
    
    def process(self, request, params, *args, **kwargs):
        try:
            logger.info(request)
#            param = ParamWrapper()
#            param.data = json.loads(params['content'])
            if (self.requireLogin()):
                '''
                chekc the status of session if accountKey is set
                '''
                if not hasattr(request, 'user'):
#                if 'user' in request.session:
#                    param.user = request.session['user']
#                    param.user = request.user
#                else:
                    # TODO should differentiate login failure and session expires
                    raise ReLoginException()
            result = self.processData(request)
            if result is not None:
                logger.info(result)
            else:
                result = {}
            return wrapHttpResponse(result)
        except LocalsException as e:
            return wrapExceptionHttpResponse(e)
        except Exception as e:
            logging.exception("Faild to serve request")
            #traceback.print_exc(file=sys.stdout)
            return wrapExceptionHttpResponse(ServerErrorException())

# function to save profile image to s3, return the link for profile image
def handle_profile_image(user, imageFile):
    key = Key(bucket)
    key.key = 'userid_' + user.id  + '_' + str(int(time.time())) + '.png'
    key.set_contents_from_file(imageFile)
    profileImage = ProfileImage.objects.create(user=user, imageURL=key.key)
    profileImage.save()
    return profileImage.imageURL

from django import forms
class RegisterForm(forms.Form):
    image = forms.ImageField()
    firstName = forms.CharField()
    lastName = forms.CharField()
    email = forms.EmailField()
    username = forms.CharField()
    password = forms.CharField()

def username_present(username):
    if User.objects.filter(username=username).count():
        return True
    return False

def email_present(email):
    if User.objects.filter(email=email).count():
        return True
    return False

class Register(BaseView):
    def requireLogin(self):
        return False

    def processData(self, request):
        try:
            if request.method == 'POST':
                form = RegisterForm(request.POST, request.FILES)
                
                if form.is_valid():
                    data = form.cleaned_data
                    # check username/email exists or not, if not then register this user
                    if (username_present(data['username'])):
                        raise UsernameExistsException()
                    if (email_present(data['email'])):
                        raise EmailExistsException()
                    
                    user = User.objects.create_user(data['username'], data['email'], data['password'])
                    user.first_name = data['firstName']
                    user.last_name = data['lastName']
                    user.save()
                    profileImage = handle_profile_image(user, request.FILES['image'])
                    userProfile = UserProfile.objects.create(user=user, profileImage=profileImage, social=Social.objects.create())
                    userProfile.save()
                    
                    request.session['user'] = user
                    return {} 
            else:
                form = RegisterForm()
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            logging.exception("Faild to serve request")
            raise e
        return {}

#class registerWithFacebook(BaseView):
#    def requireLogin(self):
#        return False
#    
#    def processData(self, request, param):
#        data = param.data
#    
#        fbId = data['fbId']
#        salted = data['salted']
#        secureCode = cache.get("loginAttemp" + fbId)
#        if secureCode == None:
#            return wrapHttpResponse({})
#    
#        if not Util.validateClienetSalt(fbId, salted, secureCode):
#            return wrapHttpResponse({})
#    
#        token = data['facebookToken']
#        response = urllib2.urlopen("https://graph.facebook.com/me?fields=id,email,first_name,last_name&access_token=" + token).read()
#        simpleProfile = json.loads(response)
#
#        # check profile exists or not and save it
#        if (Account.objects.filter(email=simpleProfile['email']) or Account.objects.filter(fbId=simpleProfile['id'])):
#            # accont existis
#            raise AccountExistsException()
#        
#        try:
#            if not Profile.objects.filter(fbId = fbId):
#                profile = Profile.objects.create(key=getProfileKey(fbId),firstName=simpleProfile['first_name'],lastName=simpleProfile['last_name'],fbId=fbId,followerIndex=FollowerIndex.objects.create(),followingIndex=FollowerIndex.objects.create(),friendList=FriendList.objects.create())
#                profile.save()
#            else:
#                Profile.objects.raw_update({"fbId": fbId}, {'firstName': simpleProfile['first_name'], 'lastName': simpleProfile['last_name'], 'fbId':fbId})
#                profile = Profile.objects.get(fbId = fbId)
#
#            # create the account
#            account = Account.objects.create(fbId = fbId, credits = Impression_app_setting.DEFAULT_INITIAL_CREDITS, facebookToken = token, profile = profile, isActive = True, email=simpleProfile['email'], code=Util.generatePromoCode())
#            account.save()
#            
#            request.session[ACCOUNTID] = account.id
#            addFriendProfileTask.delay(token, fbId)
#        except Exception:
#            logger.error("registration failed")
#            #traceback.print_exc(file=sys.stdout)
#            raise ImpressionException("Failed during account registration")
#    
#        return {}

from django.contrib.auth import authenticate, login
class LoginView(BaseView):
    def requireLogin(self):
        return False
    
    def processData(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
            else:
                raise LoginFailedException()
        else:
            raise LoginFailedException()

from django.contrib.auth import logout
class logout(BaseView):
    def requireLogin(self):
        return False
    
    def processData(self, request):
        try:
            logout(request)
        except KeyError:
            pass

class UploadPhotoForm(forms.Form):
    title = forms.CharField(max_length=50)
    lat = forms.FloatField()
    lon = forms.FloatField()
    image = forms.ImageField()

# function to save photo image to s3, also kick off a task to resize it
def handle_image(user, imageFile):
    key = Key(bucket)
    key.key = 'uploadedphoto_userid_' + user.id  + '_' + str(int(time.time())) + '.png'
    key.set_contents_from_file(imageFile)
    return key.key

@csrf_exempt
def upload_file(request):
    try:
        if request.method == 'POST':
            form = UploadPhotoForm(request.POST, request.FILES)
            if form.is_valid():
                handle_image(request.FILES['image'])
        else:
            form = UploadPhotoForm()
    except:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Faild to serve request")
    return 
    
# upload an image to database
class postImage(BaseView):
    def requireLogin(self):
        return True
    
    def processData(self, request):
        try:
            if request.method == 'POST':
                form = UploadPhotoForm(request.POST, request.FILES)
                print request.user
                if form.is_valid():
                    url = handle_image(request.user, request.FILES['image'])
                    data = form.cleaned_data
                    photo = Resource.objects.create(title=data['title'], loc=Point(lat=data['lat'], lon=data['lon']), creator=request.user.get_profile(), imageURL=url, likes=LikePool.objects.create())
                    photo.save()
                    return 
            else:
                form = RegisterForm()
        except:
            traceback.print_exc(file=sys.stdout)
            logging.exception("Faild to serve request")
        return

# remove an image from s3
def remove_image(url):
    key = Key(bucket)
    key.key = url
    bucket.delete_key(key)
    
# remove an image from database
class removeImage(BaseView):
    def requireLogin(self):
        return True
    
    def processData(self, request, param):
        data = param.data
        photo = Resource.objects.get(id=ObjectId(data['id']))
        if photo.creator == request.user:
            Resource.objects.filter(id=ObjectId(data['id'])).delete()
            remove_image(data['imageURL'])
        else:
            raise NoPrivilegeException()

# like an image to database
class addLike(BaseView):
    def requireLogin(self):
        return True
    
    def processData(self, request, param):
        data = param.data
        resource = Resource.objects.get(id=data['id'])
        
        likePool = resource.likes
        likeKey = likePool.id
        if not request.user in likePool.likes:
            LikePool.objects.raw_update({"_id": ObjectId(likeKey)}, {"$addToSet": {"likes": request.user.id}})
            Resource.objects.raw_update({"_id": ObjectId(data['id'])}, {"$inc": {"likeCount":1}})
            # save it to source profile list
            # async call to add to all followers's queue
#            addLikeFollowerTask.delay(data['iId'], sourceProfile.key)

# unlike an image to database
class removeLike(BaseView):
    def requireLogin(self):
        return True
    
    def processData(self, request, param):
        data = param.data


class addComment(BaseView):
    def requireLogin(self):
        return True
    
    def processData(self, request, param):
        data = param.data
    
class removeComment(BaseView):
    def requireLogin(self):
        return True
    
    def processData(self, request, param):
        data = param.data


# http://stackoverflow.com/questions/12064909/using-mongodb-runcommand-with-django-mongodb-engine
class getAround(BaseView):
    def requireLogin(self):
        return False
    
    def processData(self, request):
        data = request.POST
        print data
        results = []
#        , 'category': data['category']
        for result in Resource.objects.order_by('distance').filter(loc={'$near': {data['lon'], data['lat']}})[RESULT_PER_PAGE * data['page']:RESULT_PER_PAGE]:
            print result
            results.append(Resource.getContent(result))
        print results
        return results
            
#class getImpression(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        data = param.data
#        account = param.account
#
#        sourceProfile = Profile.objects.get(fbId=getattr(account, 'fbId'))#.objects.get(fbId=getattr(account, 'fbId'))
#
#        impressionId = data['impressionId']
#        page = data['page']
#        result = []
#
#        try:
#            impression = Impression.objects.get(id=ObjectId(impressionId))
#            if impression.commentCount > 0:
#                for comment in Comment.objects.order_by("-creationTime").filter(impression=impression)[COMMENT_PER_PAGE * page:COMMENT_PER_PAGE]:
#                    result.append(Comment.getContent(comment))
#            
#            impressionContent = Impression.getContent(impression)
#            impressionContent['liked'] = sourceProfile.key in impression.likes.likes
#        except ObjectDoesNotExist as e:
#            logger.error("requested content does not exist")
#            raise ContentNotExistsException()
#
#        return {'impression': impressionContent, 'comments': result, 'page': page}
#    
#class addLike(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        data = param.data
#        account = param.account
#    
#        sourceProfile = Profile.objects.get(fbId=getattr(account, 'fbId'))
#        likePool = Impression.objects.get(id=ObjectId(data['iId'])).likes
#        likeKey = likePool.id
#        if not sourceProfile.key in likePool.likes:
#            LikePool.objects.raw_update({"_id": ObjectId(likeKey)}, {"$addToSet": {"likes": sourceProfile.key}})
#            Impression.objects.raw_update({"_id": ObjectId(data['iId'])}, {"$inc": {"likeCount":1}})
#            # save it to source profile list
#            # async call to add to all followers's queue
#            addLikeFollowerTask.delay(data['iId'], sourceProfile.key)
#        
#        return {}
#
#class unLike(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        data = param.data
#        account = param.account
#    
#        sourceProfile = Profile.objects.get(fbId=getattr(account, 'fbId'))
#        
#        likePool = Impression.objects.get(id=ObjectId(data['iId'])).likes
#        likeKey = likePool.id
#        
#        if sourceProfile.key in likePool.likes:
#            LikePool.objects.raw_update({"_id": ObjectId(likeKey)}, {"$pull": {"likes": sourceProfile.key}})
#            Impression.objects.raw_update({"_id": ObjectId(data['iId'])}, {"$inc": {"likeCount":-1}})
#            Action.objects.filter(fromKey=sourceProfile,actionKey=data['iId'],actionType=ActionType.Like).delete()
#
#        return {}
#
#class removeImpression(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        data = param.data
#        account = param.account
#    
#        sourceProfile = Profile.objects.get(fbId=getattr(account, 'fbId'))
#        impression = Impression.objects.get(id=ObjectId(data['key']))
#        if impression.isActive == False:
#            return {}
#        # first check if it's target/creator
#        if not (impression.creator == sourceProfile or impression.target == sourceProfile):
#            raise NoPrivilegeException()
#        
##        if impression.isAnonymous:
#        if account.credits >= Impression_app_setting.REMOVE_IMPRESSION_CREDIT:
#            account.credits = account.credits - Impression_app_setting.REMOVE_IMPRESSION_CREDIT
#            account.save()
#        else:
#            raise NotEnoughBalanceException()
#        
#        removeId = impression.id
#        
#        if removeId:
#            targetProfile = impression.target
#            if targetProfile.impressionCount == 1:
#                average = 0.0
#            else:
#                average = ( targetProfile.starCount - impression.rating + 0.0 ) / ( targetProfile.impressionCount - 1.0)
#
#            Impression.objects.filter(id=ObjectId(data['key'])).delete()
#
#            # take away the credits from profile and update ranking stuff
#            Profile.update({"_id": targetProfile.key}, {"$inc": {"impressionCount":-1, "starCount": -impression.rating}, "$set": {"average": average}})
#            
#            if impression.isAnonymous:
#                Profile.update({"_id": targetProfile.key}, {"$inc": {"anoCount":-1}})
#        return {'count': targetProfile.impressionCount - 1.0, 'average': "{0:.1f}".format(average)}
#        
#
#class getProfile(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        data = param.data
#        account = param.account
#        
#        result = []
#        
#        # TODO make it done in one query instead of two
#        try:
#            targetProfile = Profile.objects.get(key=data['targetId'])
#            sourceProfile = Profile.objects.get(fbId=getattr(account, 'fbId'))#.objects.get(fbId=getattr(account, 'fbId'))
#            
#            order = '-creationTime'
#            if data['order'] == 0:
#                order = '-creationTime'
#            elif data['order'] == 1:
#                order = '-rating'
#            elif data['order'] == 2:
#                order = 'rating'
#            
#            if data['targetId'] == getattr(sourceProfile, 'key'):#['_id']:#['_id']:
#                # retun full profile
#                # regarding profile image, it will display facebook image for now
#                for impression in Impression.objects.order_by(order).filter(target=targetProfile, isActive=True)[TERM_PER_PAGE * data['page']:TERM_PER_PAGE * ( data['page'] + 1 )]:#.skip(TERM_PER_PAGE * data['page']).limit(TERM_PER_PAGE):
#                    impressionContent = Impression.getContent(impression)
#                    impressionContent['liked'] = sourceProfile.key in impression.likes.likes
#                    result.append(impressionContent)
#            else:
#                for impression in Impression.objects.order_by(order).filter(target=targetProfile, isActive=True)[TERM_PER_PAGE * data['page']:TERM_PER_PAGE * ( data['page'] + 1 )]:#.skip(TERM_PER_PAGE * data['page']).limit(TERM_PER_PAGE):
#                    impressionContent = Impression.getContent(impression)
#                    impressionContent['liked'] = sourceProfile.key in impression.likes.likes
#                    result.append(impressionContent)
#
#        except ObjectDoesNotExist:
#            if 'name' in data:
#                names = data['name'].split(' ', 1 )
#                if len(names) == 2:
#                    targetProfile = Profile.objects.create(key=data['targetId'],firstName=names[0],lastName=names[1],fbId=data['fbId'],followerIndex=FollowerIndex.objects.create(),followingIndex=FollowerIndex.objects.create(),friendList=FriendList.objects.create())
#                else:
#                    targetProfile = Profile.objects.create(key=data['targetId'],firstName=names[0],lastName="",fbId=data['fbId'],followerIndex=FollowerIndex.objects.create(),followingIndex=FollowerIndex.objects.create(),friendList=FriendList.objects.create())
#            else:
#                targetProfile = Profile.objects.create(key=data['targetId'],firstName=data['firstName'],lastName=data['lastName'],fbId=data['fbId'],followerIndex=FollowerIndex.objects.create(),followingIndex=FollowerIndex.objects.create(),friendList=FriendList.objects.create())
#            targetProfile.save()
#        
#        return {"profile": Profile.getProfile(targetProfile), "impressions": {"result": result, "page": data['page'], "sortBy": data['order'], "count": len(result), "start": TERM_PER_PAGE * data['page']}}
#
#class getNewsFeed(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        data = param.data
#        account = param.account
#        
#        sourceProfile = Profile.objects.get(fbId=getattr(account, 'fbId'))
#        actions = Action.objects.order_by('-creationTime').filter(newsFeed=sourceProfile)[FEED_PER_PAGE * data['page']:FEED_PER_PAGE * (data['page'] + 1)]
#        results = []
#        for action in actions:
#            results.append(getAction(action, True))
##            if action.actionType == 0:
##                content = Impression.objects.get(id=ObjectId(action.actionKey))
##                # content = Impression.findOne({"_id": ObjectId(action.actionKey)})
##                results.append({"impression": Impression.getBrief(content), "actionType":0})
##            elif action.actionType == 1:
##                content = Impression.objects.get(id=ObjectId(action.actionKey))
##                # content = Impression.findOne({"_id": ObjectId(action.actionKey)})
##                results.append({"impression": Impression.getBrief(content), "actionType":1})
#        
#        return {"feeds": results, "page": data['page']}
#    
#class getGlobalNewsFeed(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        data = param.data
#        
#        actions = Action.objects.order_by('-creationTime')[FEED_PER_PAGE * data['page']:FEED_PER_PAGE * (data['page'] + 1)]
#        results = []
#        for action in actions:
#            results.append(getAction(action, True))
#
#        return {"feeds": results, "page": data['page']}
#
#def getAction(action, honorAnonymous):
#    if honorAnonymous:
#        return action.getAnonymous()
#    else:
#        return action.getNormal()
#
#class getActivities(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        data = param.data
#        account = param.account
#        
#        targetId = data['fbId']
#        sourceProfile = Profile.objects.get(fbId=getattr(account, 'fbId'))
#        targetProfile = Profile.objects.get(fbId=targetId)
#        results = []
#        
#        actions = Action.objects.defer("activityFeed", "newsFeed").order_by('-creationTime').filter(activityFeed=targetProfile)[FEED_PER_PAGE * data['page']:FEED_PER_PAGE * (data['page'] + 1)]
#        if targetId == getattr(account, 'fbId'):
#            # looking at himself, so showing all activities profile created and other people created on him
#            for action in actions:
#                if action.isAnonymous and action.fromKey != sourceProfile:
#                    # set creator to anonymous
#                    results.append(getAction(action, True))
#                else:
#                    # put whatever it is 
#                    results.append(getAction(action, False))
#        else:
#            for action in actions:
#                if action.fromKey == sourceProfile:
#                    results.append(getAction(action, False))
#                elif action.toKey == targetProfile:
#                    results.append(getAction(action, True))
#                elif action.isAnonymous:
#                    continue
#                else:
#                    results.append(getAction(action, True))
#
#        return {"profile": Profile.getProfile(targetProfile), "activity": results, "page": data['page']}
#
#class verifyReceipt(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        data = param.data
#        account = param.account
#        
#        url = Impression_app_setting.VERIFY_RECEIPT_URL
#        
#        logger.info(data['receipt'])
#        response = urllib2.urlopen(url, json.dumps({'receipt-data': base64.b64encode(data['receipt'])})).read()
#        logger.info(response)
#        receipt = json.loads(response)
#        
#        if receipt['status'] != 0:
#            raise Exception
#        
#        try:
#            plan = Plan.objects.get(app_item_id=receipt['receipt']['product_id'])
#            '''
#            {"original_purchase_date_pst":"2012-09-09 09:26:55 America/Los_Angeles", "unique_identifier":"f499131c4852c46f12206e7127c9a88b4dba6361", "original_transaction_id":"1000000055660636", "bvrs":"1.0", "transaction_id":"1000000055660636", "quantity":"1", "product_id":"com.ningkai.impressions.credits.50", "item_id":"558644366", "purchase_date_ms":"1347208015884", "purchase_date":"2012-09-09 16:26:55 Etc/GMT", "original_purchase_date":"2012-09-09 16:26:55 Etc/GMT", "purchase_date_pst":"2012-09-09 09:26:55 America/Los_Angeles", "bid":"com.ningkai.impressions", "original_purchase_date_ms":"1347208015884"}
#            '''
#            appleReceipt = AppleReceipt.objects.create(receipt=receipt['receipt'])
#            appleReceipt.save()
#            purchase = Purchase.objects.create(purchasor=account, planKey=plan, receipt=appleReceipt)
#            purchase.save()
#            Account.objects.raw_update({'_id': ObjectId(account.id)}, {"$inc":{"credits": plan.credits}})
##            Account.objects.raw_update({'_id': ObjectId(account.id)}, {"$push": {"purchases": purchase}})
#        except Exception:
#            exc_type, exc_value, exc_traceback = sys.exc_info()
#            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
#            logger.exception( ''.join( line for line in lines))  # Log it or whatever here
#            logger.exception("Failed to process purchase")
#            raise FailToProcessPurchaseException() 
#        
#        return {}
#    
#class addComment(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        data = param.data
#        account = param.account
#
#        impressionId = data['impressionId']
#        sourceProfile = Profile.objects.get(fbId=getattr(account, 'fbId'))
#        impression = Impression.objects.get(id=ObjectId(impressionId))
#        targetProfile = impression.target
#
#        if (data['isAnonymous']):
#            # check the creidt and minus value
#            if account.credits >= Impression_app_setting.CREATE_COMMENT_ANONYMOUS_CREDIT:
#                account.credits = account.credits - Impression_app_setting.CREATE_COMMENT_ANONYMOUS_CREDIT
#                account.save()
#            else:
#                raise NotEnoughBalanceException()
#
#        # create a new comment first
#        comment = Comment.objects.create(creator=sourceProfile, target=targetProfile, impression=impression, content=data['content'], isAnonymous=data['isAnonymous'])
#        comment.save()
#        
#        Impression.update({"_id": ObjectId(impression.id)}, {"$inc": {"commentCount": 1}, "$addToSet": {'involvers': sourceProfile.key}})
#        
#        addCommentFollowerTask.delay(comment, impressionId, impression)
#        return {}
#
#class removeComment(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        data = param.data
#        account = param.account
#
#        commentId = data['commentId']
#        comment = Comment.objects.get(id=ObjectId(commentId))
#
#        sourceProfile = Profile.objects.get(fbId=getattr(account, 'fbId'))
#        # first check if it's target/creator
#        if not (comment.creator == sourceProfile or comment.target == sourceProfile):
#            raise NoPrivilegeException()
#        
##        if (comment.isAnonymous):
#        # check the creidt and minus value
#        if account.credits >= Impression_app_setting.REMOVE_COMMENT_CREDIT:
#            account.credits = account.credits - Impression_app_setting.REMOVE_COMMENT_CREDIT
#            account.save()
#        else:
#            raise NotEnoughBalanceException()
#
#        impression = comment.impression
#        
#        Comment.objects.filter(id=ObjectId(commentId)).delete()
#        Impression.objects.raw_update({"_id": ObjectId(impression.id)}, {"$inc": {"commentCount": -1}})
#        
#        return {}
#
#class getFriends(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        data = param.data
#        account = param.account
#        sourceProfile = Profile.objects.get(fbId=getattr(account, 'fbId'))
#        friendList = sourceProfile.friendList;
#         
#        return {'friendList': friendList.friends}    
#    
#class flagContent(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        data = param.data
#        account = param.account
#        sourceProfile = Profile.objects.get(fbId=getattr(account, 'fbId'))
#        objectId = data['objectId']
#        objectType = data['objectType']
#        
#        FlagContent.objects.create(creator=sourceProfile, objectId=objectId, objectType=objectType).save()
#        
#        return {}
#    
## a generic function to add an object to database
#class getTermForProfile(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        data = param.data
#        profile = Profile.objects.get(fbId=data['targetKey'])
#        if profile is None:
#            quickCreateFBAccount(data['targetKey'])
#        termCollection = conn.get_collection('Term')
#        terms = termCollection.find({"target": profile['_id']}).sort(data['sortBy'], pymongo.DESCENDING).skip(TERM_PER_PAGE * data['page']).limit(TERM_PER_PAGE)
#        result = []
#        for term in terms:
#            if term['isAnonymous'] and term['creator'] != profile['_id']:
#                # have to hide the creator information
#                tempProfile = Profile.getDummyProfile()
#                tempTerm = term.getTerm(True)
#            else:
#                tempProfile = Profile.objects.get(_id=term['creator'])
#                tempTerm = term.getTerm(False)
#
#            tempTerm['creator'] = tempProfile
#            result.append(tempTerm)
#        return {'term': result, 'page': data['page']}
#                
#
#def quickCreateFBAccount(fbId):
#    response = urllib2.urlopen("https://graph.facebook.com/" + fbId).read()
#    p = json.loads(response)
#    profile = Profile.objects.create(_id=p['id'],firstName=p['firstName'],lastName=p['lastName'])
#    profile.save()
#
#
#class getAccount(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, data):
#        return 0
#
#class getCredit(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        account = param.account
#        return {"balance": account.credits}
#
#class getReferCode(BaseView):
#    def requireLogin(self):
#        return True
#    
#    def processData(self, request, param):
#        account = param.account
#        return {"code": account.code}    
#
#class peek(BaseView):
#    def requireLogin(self):
#        return False
#    
#    def processData(self, request, data):
#        data = json.loads(request.POST['content'])
#        if Account.objects.filter(fbId=data['fbId']):
#            peekType = 1
#        else:
#            peekType = 0
#        
#        secureCode = Util.generateLoginCode(10)
#        cache.set("loginAttemp" + data['fbId'], secureCode, 3600)
#        return {"salt":secureCode, "type":peekType}

