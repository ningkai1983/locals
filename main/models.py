'''
Created on Dec 24, 2012

@author: kaining
'''
from django.db import models, connections
import time, datetime

from boto.s3.connection import S3Connection
conn = S3Connection('AKIAJQD3IYLGJOBU2RJA', '6uYfKcl2w1wuo2wxROL2JnWl5Z/sE3pPPSv75k5V')
from boto.s3.key import Key
bucket = conn.create_bucket('kainingsupermybucket')

conn = connections['default']

class ActionType:
    CreateImpression = 0
    Like = 1
    Comment = 2
    RemoveImpression = 3
    RemoveComment = 4
    UnLike = 5

class BaseModel(models.Model):
    isActive = models.BooleanField(default=True)
    creationDate = models.DateTimeField('date created')
    creationTime = models.FloatField(default=0.0)

    class Meta:
        abstract = True
        
    def save(self, **kwargs):
        if not self.creationTime:
            self.creationTime = time.time()
            self.creationDate = datetime.datetime.utcnow()
        super(BaseModel,self).save()

    @staticmethod
    def getCollection(name):
        # this is the naming convension under a certain package
        return conn.get_collection("main_" + name.lower())
    
    @classmethod
    def findOne(cls, query, filter=None):
        collection = BaseModel.getCollection(cls.__name__)
        if 'isActive' not in query:
            query['isActive'] = True
        return collection.find_one(query, filter)
    
    @classmethod
    def find(cls, query, filter=None):
        collection = BaseModel.getCollection(cls.__name__)
        if 'isActive' not in query:
            query['isActive'] = True
        return collection.find(query, filter)

    @classmethod
    def remove(cls, obj):
        obj.isActive = False
        obj.save()
#        collection = BaseModel.getCollection(cls.__name__)
#        collection.update(query, {"$set": {"isActive": False}})
        return 

    @classmethod
    def update(cls, query, update):
        collection = BaseModel.getCollection(cls.__name__)
        collection.update(query, update)
        return 

#def handle_uploaded(imageFile, imageType='n'):
#    key = Key(bucket)
#    key.key = "testid" + '_' + str(int(time.time())) + imageType + '.png'
#    key.set_contents_from_file(imageFile)
#    photo = Photo.objects.create(u=key.key,t=imageType)
#    photo.save()
#    operatePhoto.delay(photo.id)
##    https://s3.amazonaws.com/kainingsupermybucket/testid_1352140815n.png
#
#from django import forms
#class UploadFileForm(forms.Form):
##    title = forms.CharField(max_length=50)
##    file  = forms.FileField()
#    image = forms.ImageField()
#
#@csrf_exempt
#def upload_file(request):
#    try:
#        if request.method == 'POST':
#            form = UploadFileForm(request.POST, request.FILES)
#            if form.is_valid():
#    #            userAuth = UserSocialAuth.objects.get(user=request.user.id)
#                handle_uploaded(request.FILES['image'])
#                return HttpResponseRedirect('/success/url/')
#        else:
#            form = UploadFileForm()
#    except:
#        traceback.print_exc(file=sys.stdout)
#        logging.exception("Faild to serve request")
#    return render_to_response('upload.html', {'form': form})

from django.contrib.auth.models import User

class ProfileImage(BaseModel):
    imageURL = models.URLField()
    user = models.ForeignKey(User, unique=True)

class Social(models.Model):
    fbId = models.CharField(max_length = 30)
    fbToken = models.CharField(max_length = 255)
    twitterId = models.CharField(max_length = 30)
    twitterToken = models.CharField(max_length = 255)

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    profileImage = models.URLField()

    social = models.ForeignKey(Social)
    
    level = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    joinDate = models.DateTimeField('date joined', auto_now_add = True)

class Point(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()

#Place.objects.filter(geom__distance_lte=(point, 
#D(mi=20))).distance(point).order_by('distance')
from django_mongodb_engine.contrib import MongoDBManager
from djangotoolbox.fields import EmbeddedModelField
from djangotoolbox.fields import ListField, SetField

class LikePool(BaseModel):
    likes = SetField(models.ForeignKey(UserProfile, related_name='+'))

class Resource(BaseModel):
    tags = ListField()
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    type = models.IntegerField(default = 0) # 0 means image
    loc = EmbeddedModelField(Point)
    imageURL = models.CharField(max_length = 255) # stores the link to image
    likes = models.ForeignKey(LikePool, related_name='+')
    likeCount = models.IntegerField(default = 0) 
    commentCount = models.IntegerField(default = 0)
    creator = models.ForeignKey(UserProfile, related_name='+')

    objects = MongoDBManager() 
    class MongoMeta:
        indexes = [
            [('loc', '2d')]
        ]    

    @staticmethod
    def getContent(content):
        return {'title': content.title, 'category': content.category, 'lon':content.loc.lon, 'lat':content.loc.lat, 'imageURL':content.imageURL, 'likeCount': content.likeCount}
    
class Comment(BaseModel):
    creator = models.ForeignKey(UserProfile, related_name='+')
    target = models.ForeignKey(UserProfile, related_name='+')

    resource = models.ForeignKey(Resource, related_name='+')
    content = models.TextField()

    @staticmethod
    def getContent(content):
        return {"creator": UserProfile.getDummyProfile() if content.isAnonymous else UserProfile.getSimpleProfile(content.creator), "content": content.content, 'isAnonymous': content.isAnonymous, "creationTime": content.creationTime, "key": content.id}

class FlagContent(BaseModel):
    creator = models.ForeignKey(UserProfile, related_name='+')
    objectId = models.CharField(max_length = 30)
    objectType = models.IntegerField(default = 0)
    cleard = models.BooleanField(default=False)

class VisitHistory(BaseModel):
    fromAccount = models.ForeignKey(UserProfile, related_name='+')
    toAccount = models.ForeignKey(UserProfile, related_name='+')
    timestamp = models.DateTimeField('date visited', auto_now_add = True)
    
class Rate(models.Model):
    creator = models.ForeignKey(UserProfile, related_name='+')
    target = models.ForeignKey(UserProfile, related_name='+')
    resource = models.ForeignKey(Resource, related_name='+')
    rating = models.IntegerField()
    creationTime = models.DateTimeField()
    
    @staticmethod
    def getRate(rate, hide):
        obj = {'creator': UserProfile.getDummyProfile(), 'target': rate.target, 'term': rate.term, 'content': rate.content, 'rating': rate.rating, 'isAnonymous':rate.isAnonymous, 'creationTime': rate.creationTime}
        if not hide:
            obj['creator'] = rate.creator
        return obj

