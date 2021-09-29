from django.db import models
from django.db.models.fields import CharField

# Create your models here.
class Image(models.Model):
    title = models.CharField(max_length = 800, unique = True)
    categorie = models.CharField(default="demo_image", max_length=200, unique = False)
    created_at = models.DateTimeField(auto_now_add = True)
    src = models.TextField()
    url = models.URLField(default = "", max_length=200)
    description = models.TextField(default = "")
    def __str__(self):
        return "_".join([self.title, self.src])
   