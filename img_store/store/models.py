from django.db import models

# Create your models here.
class Image(models.Model):
    title = models.CharField(max_length=200, unique = True)
    created_at = models.DateTimeField(auto_now_add=True)
    src = models.URLField(max_length=600, unique = True)
    url = models.URLField(default = "", max_length=600)
    description = models.CharField(default = "", max_length=1000)
    def __str__(self):
        return self.title
   