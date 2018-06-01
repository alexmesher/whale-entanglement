from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

import geopandas as gpd
import pandas as pd

import flickrapi

import datetime
from datetime import datetime, timedelta
from .models import Target, Tag, Owner, Photo, Photo_sorted, Term


def get_puds(target,mintime,maxtime):
	# table = {}
	# for year in range(mintime.year, maxtime.year + 1):
	# 	table[year] = {}
	# 	if year == maxtime.year:
	# 		for month in range(1,maxtime.month + 1):
	# 			for day in month:
	# 				table[year][month][day] = [0,0]
	# 	elif year == maxtime.year + 1:
	# 		pass
	# 	else:
	# 		for month in range(1, 13):
	# 			for day in month:
	# 				table[year][month][day] = [0,0]
	delta = maxtime - mintime
	table = []
	flickrAPIKey = '1692f541ed22f8486eba2bc151a7055a'
	flickrSecret = '05d7fdb95d376d7e'
	bb = "-123.0000,36.5631,-121.7864,37.0000"
	fapi = flickrapi.FlickrAPI(flickrAPIKey, flickrSecret, format='parsed-json')
	for i in range(delta.days +1):
		today = mintime + timedelta(days=i)
		tomorrow = mintime + timedelta(days=i+1)
		total_owners = set()
		target_owners = set()
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
				min_taken_date=str(datetime.fromtimestamp(datetime.timestamp(today))),
				max_taken_date=str(datetime.fromtimestamp(datetime.timestamp(tomorrow)))
				)
			for photo in rsp['photos']['photo']:
				total_owners.add(photo['owner'])
				#print("owner added: " + str(photo['owner']))
			if page_on == 1:
				total_pages = int(rsp['photos']['pages'])
			page_on += 1
		for photo_sorted in Photo_sorted.objects.filter(was_sorted=True, 
			target_pictured=True, 
			photo__date_taken__range=(today,tomorrow),
			target=target):
			owner = photo_sorted.photo.owner
			#print("date: " + str(photo_sorted.photo.date_taken) + ", owner: " + str(owner))
			target_owners.add(owner)
		try:
			ratio = len(target_owners)/len(total_owners)
		except ZeroDivisionError:
			ratio = "NA"
		table.append([today.year,today.month,today.day,
			len(total_owners),
			len(target_owners),
			ratio])
	return table

def get_saturation_curve_data(targ_pk,mintime,maxtime):
	data = {}
	#photo_set = set()
	target = Target.objects.get(pk=targ_pk)
	for photo in Photo.objects.filter(photo_sorted__target=target,
		photo_sorted__was_sorted=True,
		photo_sorted__target_pictured=True,
		date_taken__range=(mintime,maxtime)):
		term = photo.term.text
		if term in data:
			data[term] += 1
		else:
			data[term] = 1
	return data

		# 	- make a dictionary of searches:(# of terms, # of photos), initializing # of photos to 0
# - for each photo w/target
#     - get earliest flickr_search of the photo
#         - dictionary[earliest flickr_search][1] += 1
# - export dictionary to csv

def get_centroids(target,mintime,maxtime):
	delta = maxtime - mintime
	table = []
	for i in range(delta.days +1):
		today = mintime + timedelta(days=i)
		tomorrow = mintime + timedelta(days=i+1)
		for owner in Owner.objects.filter(photo__photo_sorted__target=target, photo__photo_sorted__target_pictured=True, photo__date_taken__range=(today,tomorrow)).distinct():
			lat_list = []
			lon_list = []
			for photo in Photo.objects.filter(owner=owner,photo_sorted__target=target,date_taken__range=(today,tomorrow)):
				lat_list.append(photo.lat)
				lon_list.append(photo.lon)
			mean_lat = sum(lat_list)/len(lat_list)
			mean_lon = sum(lon_list)/len(lon_list)
			table.append([owner, today.date(), mean_lat, mean_lon])
	return table


def get_top_tags(target, num_tags,mintime,maxtime):
	tag_dict = {}
	total_owners = Photo.objects.filter(
		photo_sorted__target=target,
		photo_sorted__target_pictured=True,
		photo_sorted__was_sorted=True,
		date_taken__range=(mintime,maxtime)).distinct('owner').count()
	initial_terms = ['whale', 'mammal', 'humpback whale', 'humpback', 'grey whale', 'blue whale', 'killer whale', 'orca', 'fin whale', 'cetacean']
	for tag in Tag.objects.filter(targets=target):
		if tag.text not in initial_terms:
			owner_count = Photo.objects.filter(
			photo_sorted__target=target,
			photo_sorted__target_pictured=True,
			photo_sorted__was_sorted=True,
			photo_sorted__tag=tag,
			date_taken__range=(mintime,maxtime)).distinct('owner').count()
			tag_dict[tag.text] = owner_count
	sort_array = sorted(tag_dict, key=tag_dict.get, reverse=True)[:20]
	# sort_tuples = [(("total",total_owners))]
	# for tag in sort_array:
	# 	sort_tuples.append((tag, tag_dict[tag]))
	tag_string = ""
	for tag in sort_array:
		tag_string += tag + ", "
	return tag_string #sort_tuples #tag_string

def delete_unsorted(target,mintime,maxtime):
	for photo in Photo.objects.filter(date_taken__range=(mintime,maxtime),photo_sorted__target=target,photo_sorted__was_sorted=False):
		photo.delete()

def get_distances(filepath):
	us = gpd.read_file(filepath)
	us = us.to_crs(epsg=32610)
	usgeom = us.geometry
	centroids = gpd.read_file('/code/shapefiles/whale_watching_09-18_centroids.shp')
	centroids = centroids.to_crs(epsg=32610)
	distances = centroids.distance(usgeom.ix[0])
	ddf = pd.DataFrame(distances,columns=["distance_to_land"])
	merged = centroids.merge(ddf, left_index=True,right_index=True)
	return merged








