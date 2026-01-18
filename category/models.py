from django.db import models
from django.utils.text import slugify
# Create your models here.
class Category(models.Model):
     name = models.CharField(max_length=100)
     slug = models.CharField(unique=True)
     description = models.TextField(max_length=255, blank=True)
     cat_image = models.ImageField(upload_to='photos/categories', blank=True)

     class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        
        
     def __str__(self):
        return self.name
     
     def save(self, *args, **kwargs):
         if not self.slug:
           self.slug = slugify(self.name)
           super().save(*args, **kwargs)  