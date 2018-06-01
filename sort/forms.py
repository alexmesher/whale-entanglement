from django import forms
import time

from .models import Target

class Search_form(forms.Form):
	target = forms.CharField(label='Search target',max_length=200,initial="whale watching")
	lon1 = forms.FloatField(label='Longitude of southwest coordinate',initial=-123.0000)#monterey county: -123.005582; santa cruz county:-122.32033; monterey bay: -123.0000 west coast: -126.254883
	lat1 = forms.FloatField(label='Latitude of southwest coordinate',initial=36.5631)#monterey county: 35.799640; west coast: 33.369531; mbay: 36.5631
	lon2 = forms.FloatField(label='Longitude of northeast coordinate',initial= -121.7864)#monterey county: -121.353405; west coast: -117.465820; mbay: -121.7864
	lat2 = forms.FloatField(label='Latitude of northeast coordinate',initial=37.0000)#monterey county: 36.855475; west coast: 49.334072; mbay: 37.0000
	terms = forms.CharField(label='Search terms',max_length=5000,required=False,initial="whale, mammal, humpback whale, humpback, grey whale, blue whale, killer whale, orca, fin whale, cetacean")
	mintime = forms.DateTimeField()
	maxtime = forms.DateTimeField()

class Target_date_form(forms.Form):
	targets = []
	mintime = forms.DateTimeField()
	maxtime = forms.DateTimeField()

	def __init__(self, *args, **kwargs):
		self.targets = []
		for target in Target.objects.all():
			self.targets.append((target.pk, target.text))
		super(Target_date_form, self).__init__(*args, **kwargs)
		self.fields['selection'] = forms.ChoiceField(label='Choose a target',choices=self.targets)

class Target_form(forms.Form):
	targets = []
	mintime = forms.DateTimeField()
	maxtime = forms.DateTimeField()
	num_tags = forms.IntegerField(label='Number of tags to be retrieved')

	def __init__(self, *args, **kwargs):
		self.targets = []
		for target in Target.objects.all():
			self.targets.append((target.pk, target.text))
		super(Target_form, self).__init__(*args, **kwargs)
		self.fields['selection'] = forms.ChoiceField(label='Choose a target',choices=self.targets)


	# def __init__(self, *args, **kwargs):
	# 	self.report_names = []
	# 	for report in Report.objects.all():
	# 		self.report_names.append((report.pk, "Report " + str(report.pk)))
	# 	super(Select_report, self).__init__(*args, **kwargs)
	# 	self.fields['selection'] = forms.ChoiceField(label='View a report',choices=self.report_names)

class Owners_form(forms.Form):
	mintime = forms.DateTimeField(label='minimum date')
	maxtime = forms.DateTimeField(label='maximum date')
	targets = []

	def __init__(self, *args, **kwargs):
		self.targets = []
		for target in Target.objects.all():
			self.targets.append((target.pk, target.text))
		super(Owners_form, self).__init__(*args, **kwargs)
		self.fields['target'] = forms.ChoiceField(label='Choose a target',choices=self.targets)






		
