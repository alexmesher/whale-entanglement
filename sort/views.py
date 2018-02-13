from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic


import csv
import sys
import string
import math
import time
import socket
import argparse
import flickrapi
from datetime import datetime
import geopandas as gpd
from geopandas.geoseries import *

import sort.methods as Methods
from .forms import Search_form, Target_form, Owners_form
from .models import Photo, Tag, Target, Owner, Term, Photo_sorted, Tag_sorted


def HomeSearch(request):
	if request.method == 'POST':
		if 'search_submit' in request.POST:
			form = Search_form(request.POST)
			if form.is_valid():
				lon1 = form.cleaned_data['lon1']
				lat1 = form.cleaned_data['lat1']
				lon2 = form.cleaned_data['lon2']
				lat2 = form.cleaned_data['lat2']
				bb = str(lon1) + "," + str(lat1) + "," + str(lon2) + "," + str(lat2)
				mintime = datetime.timestamp(form.cleaned_data['mintime'])
				maxtime = datetime.timestamp(form.cleaned_data['maxtime'])
				targ = form.cleaned_data['target']
				terms = form.cleaned_data['terms'].split(", ")
				try:
					terms.remove('')
				except:
					pass
				#tag_lists = [tgs[i:i + 19] for i in range(0, len(tgs), 19)]
				flickrAPIKey = '1692f541ed22f8486eba2bc151a7055a'
				flickrSecret = '05d7fdb95d376d7e'
				#try:
				fapi = flickrapi.FlickrAPI(flickrAPIKey, flickrSecret, format='parsed-json')
				try:
					target = Target.objects.get(text=targ)
				except Target.DoesNotExist:
					target = Target(text=targ)
					target.save()
				total = 0
				new = 0
				for trm in terms:
					try:
						term = Term.objects.get(text=trm)
					except Term.DoesNotExist:
						term = Term(text=trm)
						term.save()
					term.targets.add(target)
					pages_left = 1
					page = 1
					while pages_left + 1 > page:
						#tag_string = ", ".join(tag_list)
						rsp = fapi.photos.search(api_key=flickrAPIKey,
							ispublic="1",
							media="photos",
							per_page="250", 
							page=page,#str(pageNum),
							has_geo = "1", 
							bbox=bb,
							#tags=tag_string,
							extras="tags, original_format, license, geo, date_taken, date_upload, o_dims, views",
							text=term,
							accuracy="1", #6 is region level.  most things seem 10 or better.
							# min_upload_date=str(mintime),
							# max_upload_date=str(maxtime))
							min_taken_date=str(datetime.fromtimestamp(mintime)),
							max_taken_date=str(datetime.fromtimestamp(maxtime))
							)
						pages_left = int(rsp['photos']['pages'])
						usa_shape = gpd.read_file('/code/shapefiles/monterey_and_santa_cruz.shp')
						geom = usa_shape.geometry
						for p in rsp['photos']['photo']:
							coord = Point(float(p['longitude']),float(p['latitude']))
							try:
								photo = Photo.objects.get(photo_id=p['id'])
								try:
									photo_sorted = Photo_sorted.objects.get(photo=photo,target=target)
								except Photo_sorted.DoesNotExist:
									photo_sorted = Photo_sorted(photo=photo,target=target)
								photo_sorted.save()
							except Photo.DoesNotExist:
								if not coord.intersects(geom.ix[0]):
									photo = Photo(photo_id=p['id'],
										image='http://farm3.static.flickr.com/' + p['server'] + '/'+ p['id'] + "_" + p['secret'] + '.jpg',
										date_taken=p['datetaken'],
										lat=p['latitude'],
										lon=p['longitude'],
										accuracy=p['accuracy'],
										secret=p['secret'],
										server=p['server'])
									photo.save()
									photo_sorted = Photo_sorted(photo=photo,target=target)
									photo_sorted.save()
									try:
										owner = Owner.objects.get(owner_id=p['owner'])
									except Owner.DoesNotExist:
										owner = Owner(owner_id=p['owner'])
										owner.save()
									photo.owner = owner
									tags = p['tags'].split()
									for t in tags:
										try:
											tag = Tag.objects.get(text=t)
										except Tag.DoesNotExist:
											tag = Tag(text=t)
											tag.save()
										tag.photos.add(photo)
										tag.save()
							photo.save()
						page += 1
						search_complete = 'search_complete'
			target_form = Target_form()
			search_form = Search_form()
			search_complete = ""
			return render(request, 'sort/home_search.html', 
				{'search_form':search_form, 
				'target_form':target_form,
				'search_complete':search_complete })
		else:
			target_form = Target_form(request.POST)
			search_form = Search_form()
			if target_form.is_valid():
				selection = target_form.cleaned_data['selection']
				target = Target.objects.get(pk=int(selection))
				tags = ""
				for tag_sorted in Tag_sorted.objects.filter(target=target,useful=True, was_sorted=True):
					tags = str(tag_sorted.tag.text) + ", " + tags
				return render(request, 'sort/home_search.html', {'search_form':search_form, 'target_form':target_form, 'tags':tags})		
	else:
		target_form = Target_form()
		search_form = Search_form()
		return render(request, 'sort/home_search.html', {'search_form':search_form, 'target_form':target_form})

def HomePhotos(request):
	if request.method =='POST':
		target_form = Target_form(request.POST)
		if target_form.is_valid():
			selection = target_form.cleaned_data['selection']
			target = Target.objects.get(pk=int(selection))
			return HttpResponseRedirect(reverse('sort:sort_photos', args=(target.pk,)))
	else:
		target_form = Target_form()
		return render(request, 'sort/home_photos.html', {'target_form':target_form})	

def SortPhotos(request,target_pk):
	target = Target.objects.get(pk=target_pk)
	if request.method == 'POST':
		tag_list = []
		decision_dict = request.POST.dict()
		decision_dict.pop('csrfmiddlewaretoken', None)
		#return render(request, 'sort/sort.html', {'search_pk':search_pk, 'decision_dict':decision_dict})
		for photo_id, decision in decision_dict.items():
			photo = Photo.objects.get(photo_id=photo_id)
			photo_sorted = Photo_sorted.objects.get(photo=photo,target=target)
			if decision == "accept":
				photo_sorted.target_pictured = True
				for tag in photo.tag_set.all():
					try:
						tag_sorted = Tag_sorted.objects.get(tag=tag,target=target)
					except Tag_sorted.DoesNotExist:
						tag_sorted = Tag_sorted(tag=tag,target=target)
						tag_sorted.save()
			else:
				photo_sorted.target_pictured = False
			photo_sorted.was_sorted=True
			photo_sorted.save()
	left = Photo_sorted.objects.filter(was_sorted=False).count()
	if left == 0:
		return HttpResponseRedirect(reverse('sort:home_photos'))
	photo_list = Photo.objects.filter(targets=target, photo_sorted__was_sorted=False)[0:199]
	return render(request, 
		'sort/sort_photos.html', 
		{'photo_list':photo_list, 
		'target':target, 
		'count':left})


def HomeTags(request):
	if request.method =='POST':
		target_form = Target_form(request.POST)
		if target_form.is_valid():
			selection = target_form.cleaned_data['selection']
			target = Target.objects.get(pk=int(selection))
			return HttpResponseRedirect(reverse('sort:sort_tags',args=(target.pk,)))
	else:
		target_form = Target_form()
		return render(request, 'sort/home_tags.html', {'target_form':target_form})	

def SortTags(request,target_pk):
	target = Target.objects.get(pk=target_pk)
	if request.method == 'POST':
		decision_dict = request.POST.dict()
		decision_dict.pop('csrfmiddlewaretoken', None)
		for tag_pk, decision in decision_dict.items():
			tag = Tag.objects.get(pk=tag_pk)
			tag_sorted = Tag_sorted.objects.get(tag=tag, target=target)
			if decision == "useful":
				tag_sorted.useful = True
			tag_sorted.was_sorted = True
			tag_sorted.save()
		return HttpResponseRedirect(reverse('sort:home_tags'))
	else:
		tag_list = Tag.objects.filter(targets=target, tag_sorted__was_sorted=False)
	return render(request, 'sort/sort_tags.html', {'target':target, 'tag_list':tag_list})

def AnalyticsView(request):
	if request.method == 'POST':
		if 'owners_submit' in request.POST:
			target_form = Target_form()
			owners_form = Owners_form(request.POST)
			if owners_form.is_valid():
				targ = owners_form.cleaned_data['target']
				target = Target.objects.get(pk=int(targ))
				mintime = owners_form.cleaned_data['mintime']
				maxtime = owners_form.cleaned_data['maxtime']
				count = Methods.num_owners_of_targeted_photos(target,mintime,maxtime)
				return render(request, 'sort/analytics.html', {'owners_form':owners_form, 'target_form':target_form, 'count':count})
		else:# 'csv_submit' in request.POST:
			owners_form = Owners_form()
			target_form = Target_form(request.POST)
			if target_form.is_valid():
				targ_text = target_form.cleaned_data['selection']
				data = Methods.get_saturation_curve_data(targ_text)
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="testingout.csv"'
				writer = csv.writer(response)
				writer.writerow(["search","terms","photos w/target"])
				for search in data: 
					writer.writerow([search, data[search][0], data[search][1]])
				return response	
	else:
		owners_form = Owners_form()
		target_form = Target_form()
	return render(request, 'sort/analytics.html', {'owners_form':owners_form, 'target_form':target_form})
