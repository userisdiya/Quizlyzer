from django.db import models
from django.contrib.auth.models import User

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topics = models.TextField()
    score = models.FloatField()
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    practice_topics = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz by {self.user.username} on {self.timestamp.strftime('%Y-%m-%d')}"