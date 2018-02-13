from django import forms
import time

from .models import Target

class Search_form(forms.Form):
	target = forms.CharField(label='Search target',max_length=200,initial="humpback")
	lon1 = forms.FloatField(label='Longitude of southwest coordinate',initial=-123.005582)#monterey county: -123.005582; west coast: -126.254883
	lat1 = forms.FloatField(label='Latitude of southwest coordinate',initial=35.794951)#monterey county: 35.794951; west coast: 33.369531
	lon2 = forms.FloatField(label='Longitude of northeast coordinate',initial=-121.353405)#monterey county: -121.353405; west coast: -117.465820
	lat2 = forms.FloatField(label='Latitude of northeast coordinate',initial=36.855475)#monterey county: 36.855475; west coast: 49.334072
	terms = forms.CharField(label='Search terms',max_length=5000,required=False,initial="humpback")
	mintime = forms.DateTimeField(initial="1/1/15 0:00")
	maxtime = forms.DateTimeField(initial="6/1/15 0:00")

class Target_form(forms.Form):
	targets = []

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






		
