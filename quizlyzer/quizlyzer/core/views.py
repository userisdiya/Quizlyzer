# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm # Removed UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .services import generate_mcqs_from_topics
from .models import QuizAttempt
from .forms import SimpleRegistrationForm # Import our new form
import random

def register_view(request):
    if request.method == 'POST':
        form = SimpleRegistrationForm(request.POST) # Use our custom form
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SimpleRegistrationForm() # Use our custom form
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    if request.method == 'POST':
        topics = request.POST.getlist('topics')
        topics = [topic for topic in topics if topic.strip()]

        if not topics:
            messages.error(request, "Please enter at least one topic.")
            return redirect('dashboard')

        mcqs = generate_mcqs_from_topics(topics)

        if not mcqs:
            messages.error(request, "Sorry, we couldn't generate a quiz. The AI may be busy or the topics were too abstract. Please try again.")
            return redirect('dashboard')
        
        for mcq in mcqs:
            random.shuffle(mcq['options'])
        
        request.session['quiz_mcqs'] = mcqs
        request.session['quiz_topics'] = topics
        return redirect('take_quiz')

    return render(request, 'core/dashboard.html')

@login_required
def take_quiz_view(request):
    mcqs = request.session.get('quiz_mcqs')
    if not mcqs:
        messages.info(request, "Start a new quiz by entering some topics!")
        return redirect('dashboard')
    
    indexed_mcqs = list(enumerate(mcqs))
    return render(request, 'core/take_quiz.html', {'indexed_mcqs': indexed_mcqs})

@login_required
def submit_quiz_view(request):
    if request.method == 'POST':
        mcqs = request.session.get('quiz_mcqs', [])
        topics = request.session.get('quiz_topics', [])
        
        user_answers = {}
        correct_answers_count = 0
        incorrect_topics = set()

        for i, mcq in enumerate(mcqs):
            user_answer = request.POST.get(f'question_{i}')
            user_answers[i] = user_answer
            if user_answer and user_answer == mcq['correct_answer']:
                correct_answers_count += 1
            else:
                incorrect_topics.add(mcq.get('topic', 'Unknown Topic'))
        
        score = (correct_answers_count / len(mcqs)) * 100 if mcqs else 0
        
        QuizAttempt.objects.create(
            user=request.user,
            topics=", ".join(topics),
            score=score,
            total_questions=len(mcqs),
            correct_answers=correct_answers_count,
            practice_topics=", ".join(list(incorrect_topics))
        )
        
        request.session['quiz_results'] = {
            'score': round(score, 2),
            'mcqs': mcqs,
            'user_answers': user_answers,
            'practice_topics': list(incorrect_topics)
        }
        
        del request.session['quiz_mcqs']
        del request.session['quiz_topics']
        
        return redirect('quiz_results')
    return redirect('dashboard')

@login_required
def quiz_results_view(request):
    results = request.session.get('quiz_results')
    if not results:
        return redirect('dashboard')
    
    return render(request, 'core/results.html', {'results': results})

@login_required
def past_history_view(request):
    attempts = QuizAttempt.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'core/past_history.html', {'attempts': attempts})
