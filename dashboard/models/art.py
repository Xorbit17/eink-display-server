from django.db import models

class ContentType(models.Model):
    name = models.CharField(max_length=255)
    classifier_prompt = models.TextField()
    generator_prompt = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Artstyle(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    pipeline_definition = models.JSONField(default=dict)
    generator_prompt = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    
    
class ArtstyleContentType(models.Model):
    artstyle=models.ForeignKey(Artstyle, on_delete=models.CASCADE)
    content_type=models.ForeignKey(ContentType, on_delete=models.CASCADE)

