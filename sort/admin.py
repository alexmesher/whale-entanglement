from django.contrib import admin

from .models import Photo, Tag, Target, Owner, Photo_sorted, Tag_sorted

admin.site.register(Photo)
admin.site.register(Tag)
admin.site.register(Target)
admin.site.register(Owner)
admin.site.register(Photo_sorted)
admin.site.register(Tag_sorted)
