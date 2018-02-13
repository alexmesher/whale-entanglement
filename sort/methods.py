from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

import datetime
from datetime import datetime, timedelta
from .models import Target, Tag, Owner, Photo


def num_owners_of_targeted_photos(target,mintime,maxtime):
	delta = maxtime - mintime
	l = 0
	for i in range(delta.days + 1):
		#l.append(mintime + timedelta(days=i))
		p = Owner.objects.filter(photo__photo_sorted__target=target,
		photo__photo_sorted__was_sorted=True,
		photo__photo_sorted__target_pictured=True,
		photo__date_taken__range=(mintime+ timedelta(days=i),mintime + timedelta(days=(i+1)))).count()
		l += p
	return l

def get_saturation_curve_data(target):
	data = {}
	photo_set = set()
	targ = Target.objects.get(pk=target)
	for flickr_search in Flickr_search.objects.filter(target=targ).order_by('pk'):
		data[flickr_search.pk] = [flickr_search.term_set.count(), 0]
		count = 0
		for photo in flickr_search.photo_set.filter(target_pictured=True):
			if photo.photo_id not in photo_set:
				photo_set.add(photo.photo_id)
				count += 1
		data[flickr_search.pk][1] = count
	return data

		# 	- make a dictionary of searches:(# of terms, # of photos), initializing # of photos to 0
# - for each photo w/target
#     - get earliest flickr_search of the photo
#         - dictionary[earliest flickr_search][1] += 1
# - export dictionary to csv
