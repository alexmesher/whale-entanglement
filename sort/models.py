from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

import datetime

class Target(models.Model):
	text = models.CharField(max_length=100,unique=True)
	def __str__(self):
		return self.text

class Owner(models.Model):
	owner_id = models.CharField(max_length=100,primary_key=True)

	def __str__(self):
		return self.owner_id

class Term(models.Model):
	text = models.CharField(max_length=200,unique=True)
	targets = models.ManyToManyField(Target)

	def __str__(self):
		return self.text

	def num_owners(self, targ_pk, mintime, maxtime):
		target = Target.objects.get(pk=targ_pk)
		#owner_set = set()
		count = 0
		for photo in self.photo_set.filter(date_taken__range=(mintime,maxtime)):
			photo_sorted = Photo_sorted.objects.get(photo=photo,target=target)
			if photo_sorted.was_sorted == True and photo_sorted.target_pictured == True:
				#owner_set.add(photo.owner)
				count += 1
		#count = len(owner_set)
		return count


class Photo(models.Model):
	photo_id = models.BigIntegerField(primary_key=True)
	image = models.URLField(max_length=200)
	targets = models.ManyToManyField(Target, through='Photo_sorted',through_fields=('photo','target'))
	term = models.ForeignKey(Term,on_delete=models.PROTECT,null=True)
	owner = models.ForeignKey(Owner,on_delete=models.CASCADE,null=True)
	date_taken = models.DateTimeField(null=True)
	lat = models.FloatField()
	lon = models.FloatField()
	accuracy = models.IntegerField()
	secret = models.CharField(max_length=100,null=True)
	server = models.IntegerField(null=True)

	def __str__(self):
		return str(self.photo_id)

class Photo_sorted(models.Model):
	photo = models.ForeignKey(Photo)
	target = models.ForeignKey(Target)
	was_sorted = models.BooleanField(default=False)
	target_pictured = models.BooleanField(default=False)

	def __str__(self):
		return "Photo: " + str(self.photo.photo_id) + ", target: " + str(self.target.text)

class Tag(models.Model):
	text = models.CharField(max_length=500,unique=True)
	photo_sorted = models.ManyToManyField(Photo_sorted)
	targets = models.ManyToManyField(Target, through='Tag_sorted', through_fields=('tag','target'))

	def __str__(self):
		return self.text

	def get_num_target_photos_in(self):
		count = 0
		for photo in self.photos.all():
			if photo.target_pictured:
				count+=1
		return count

	def get_num_non_target_photos_in(self):
		count = 0
		for photo in self.photos.all():
			if not photo.target_pictured:
				count+=1
		return count

	def get_target_ratio(self):
		num_target_photos_in = self.get_num_target_photos_in()
		num_photos = self.photos.count()
		ratio = num_target_photos_in/num_photos
		return ratio

class Tag_sorted(models.Model):
	tag = models.ForeignKey(Tag)
	target = models.ForeignKey(Target)
	was_sorted = models.BooleanField(default=False)
	useful = models.BooleanField(default=False)

	def __str__(self):
		return "Term: " + str(self.tag.text) + ", target: " + str(self.target.text)













	






