from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

import flickrapi

import datetime
from datetime import datetime, timedelta
from .models import Target, Tag, Owner, Photo, Photo_sorted, Term


def num_owners_of_targeted_photos(target,mintime,maxtime):
	table = {}
	for year in range(mintime.year, maxtime.year + 1):
		table[year] = {}
		if year == maxtime.year:
			for month in range(1,maxtime.month + 1):
				table[year][month] = [0,0]
		elif year == maxtime.year + 1:
			pass
		else:
			for month in range(1, 13):
				table[year][month] = [0,0]
	delta = maxtime - mintime
	flickrAPIKey = '1692f541ed22f8486eba2bc151a7055a'
	flickrSecret = '05d7fdb95d376d7e'
	bb = "-123.0000,36.5631,-121.7864,37.0000"
	fapi = flickrapi.FlickrAPI(flickrAPIKey, flickrSecret, format='parsed-json')
	for i in range(delta.days +1):
		today = mintime + timedelta(days=i)
		tomorrow = mintime + timedelta(days=i+1)
		#print("today: " + str(today))
		record = []
		owners = set()
		total_pages = 1
		page_on = 1
		while total_pages >= page_on:
			rsp = fapi.photos.search(api_key=flickrAPIKey,
				ispublic="1",
				media="photos",
				per_page="250", 
				page=page_on,#str(pageNum),
				has_geo = "1", 
				bbox=bb,
				#tags=tag_string,
				extras="tags, original_format, license, geo, date_taken, date_upload, o_dims, views",
				text="",
				accuracy="1", #6 is region level.  most things seem 10 or better.
				# min_upload_date=str(mintime),
				# max_upload_date=str(maxtime))
				min_taken_date=str(today),
				max_taken_date=str(tomorrow)
				)
			for photo in rsp['photos']['photo']:
				owners.add(photo['owner'])
				#print("owner added: " + str(photo['owner']))
			if page_on == 1:
				total_pages = int(rsp['photos']['pages'])
			page_on += 1
		table[today.year][today.month][0] += len(owners)	
	for i in range(delta.days + 1):
		today = mintime + timedelta(days=i)
		tomorrow = mintime + timedelta(days=i+1)
		record = []
		owners = set()
		for photo_sorted in Photo_sorted.objects.filter(was_sorted=True, 
			target_pictured=True, 
			photo__date_taken__range=(mintime+ timedelta(days=i),mintime + timedelta(days=(i+1))),
			target=target):
			owner = photo_sorted.photo.owner
			#print("date: " + str(photo_sorted.photo.date_taken) + ", owner: " + str(owner))
			owners.add(owner)
		table[today.year][today.month][1] += len(owners)
	return table




# def main():
# 	mintime = datetime.datetime(2009,1,1,0,0)
# 	maxtime = datetime.datetime(2009,5,1,0,0)
# 	table = num_owners_of_targeted_photos(mintime,maxtime)
# 	print(table)

# main()
