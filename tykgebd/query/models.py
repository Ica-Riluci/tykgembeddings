from django.db import models

class QueryLog(models.Model):
    q_type = models.IntegerField()
    q_datetime = models.DateTimeField(auto_now_add=True)
    q_result = models.TextField()

class SimpleQuery(QueryLog):
    QTYPE = 0
    type = models.IntegerField()
    target = models.CharField(max_length=200)

class SpecQuery1(QueryLog):
    QTYPE = 1
    proto = models.CharField(max_length=20)
    customer_id = models.CharField(max_length=20)

class SpecQuery2(QueryLog):
    QTYPE = 2
    proto = models.CharField(max_length=20)
    e_app = models.TextField()

class SpecQuery3(QueryLog):
    QTYPE = 3
    proto = models.CharField(max_length=20)
    e_app = models.TextField()
