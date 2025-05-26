from django.shortcuts import render

def home(request):
    return render(request, 'quiz_app/home.html')

from django.shortcuts import redirect
from .forms import UserRegistrationForm, UserLoginForm
from .models import User

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'quiz_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(username=username, password=password)
                # Store user info in session
                request.session['user_id'] = user.id
                request.session['role'] = user.role
                return redirect('dashboard')
            except User.DoesNotExist:
                form.add_error(None, "Invalid credentials")
    else:
        form = UserLoginForm()
    return render(request, 'quiz_app/login.html', {'form': form})

def logout_view(request):
    request.session.flush()  # Clears all session data
    return redirect('login')  # Redirect to login page


from django.shortcuts import render, redirect
from .models import User, Quiz
quizzes = Quiz.objects.all()

def dashboard(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    if not user_id:
        return redirect('login')

    if user.role == 'admin':
        quizzes = Quiz.objects.filter(created_by=user)
        return render(request, 'quiz_app/admin_dashboard.html', {
            'user': user,
            'quizzes': quizzes
            })
    else:
        return render(request, 'quiz_app/student_dashboard.html', {
            'user': user
            })

from .forms import QuizForm
from .models import Quiz

def create_quiz(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    if user.role != 'admin':
        return redirect('dashboard')

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = user
            quiz.save()
            return redirect('dashboard')
    else:
        form = QuizForm()

    return render(request, 'quiz_app/create_quiz.html', {'form': form, 'user': user})

from django.shortcuts import render, redirect
from .forms import QuestionForm

def add_question(request, quiz_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    if user.role != 'admin':
        return redirect('dashboard')

    quiz = Quiz.objects.get(id=quiz_id)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            return redirect('add_question', quiz_id=quiz.id)
    else:
        form = QuestionForm()

    all_questions = quiz.questions.all()

    return render(request, 'quiz_app/add_question.html', {
        'form': form,
        'quiz': quiz,
        'questions': all_questions,
        'user': user,
    })

def student_quiz_list(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    if user.role != 'student':
        return redirect('dashboard')

    quizzes = Quiz.objects.filter(is_active=True)

    return render(request, 'quiz_app/student_quiz_list.html', {
        'quizzes': quizzes,
        'user': user,
    })

from .models import StudentResult

def attempt_quiz(request, quiz_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    if user.role != 'student':
        return redirect('dashboard')

    quiz = Quiz.objects.get(id=quiz_id)
    questions = quiz.questions.all()

    if request.method == 'POST':
        score = 0
        total = questions.count()
        results = []

        for q in questions:
            selected = request.POST.get(str(q.id))
            is_correct = selected == q.correct_answer
            if is_correct:
                score += 1
            results.append({
                'question': q.text,
                'selected': selected,
                'correct': q.correct_answer,
                'is_correct': is_correct
            })

        StudentResult.objects.create(
            student=user,
            quiz=quiz,
            score=score,
            total=total
        )
        if StudentResult.objects.filter(student=user, quiz=quiz).exists():
            return render(request, 'quiz_app/already_attempted.html', {'quiz': quiz})

        return render(request, 'quiz_app/quiz_result.html', {
            'quiz': quiz,
            'score': score,
            'total': total,
            'results': results
        })

    return render(request, 'quiz_app/attempt_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })

def student_results(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    if user.role != 'student':
        return redirect('dashboard')

    results = StudentResult.objects.filter(student=user)

    return render(request, 'quiz_app/student_results.html', {
        'results': results
    })

from .models import StudentResult, Quiz

def view_all_results(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    if user.role != 'admin':
        return redirect('dashboard')

    quizzes = Quiz.objects.filter(created_by=user)
    selected_quiz_id = request.GET.get('quiz')
    selected_quiz = None
    results = []

    if selected_quiz_id:
        selected_quiz = Quiz.objects.get(id=selected_quiz_id)
        results = StudentResult.objects.filter(quiz=selected_quiz)

    return render(request, 'quiz_app/view_all_results.html', {
        'quizzes': quizzes,
        'results': results,
        'selected_quiz': selected_quiz,
    })

from django.db.models import F

def leaderboard(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)

    top_scores = StudentResult.objects.filter(quiz=quiz).order_by('-score', 'submitted_at')[:5]

    return render(request, 'quiz_app/leaderboard.html', {
        'quiz': quiz,
        'top_scores': top_scores
    })

from django.db.models import Avg, Count, Max, Min

def analytics_dashboard(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    if user.role != 'admin':
        return redirect('dashboard')

    # Basic metrics
    total_quizzes = Quiz.objects.filter(created_by=user).count()
    total_students = User.objects.filter(role='student').count()
    total_attempts = StudentResult.objects.filter(quiz__created_by=user).count()

    average_score = StudentResult.objects.filter(quiz__created_by=user).aggregate(avg_score=Avg('score'))['avg_score']
    top_score = StudentResult.objects.filter(quiz__created_by=user).aggregate(top=Max('score'))['top']
    low_score = StudentResult.objects.filter(quiz__created_by=user).aggregate(low=Min('score'))['low']

    most_attempted_quiz = (
        StudentResult.objects.filter(quiz__created_by=user)
        .values('quiz__title')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )

    return render(request, 'quiz_app/analytics_dashboard.html', {
        'total_quizzes': total_quizzes,
        'total_students': total_students,
        'total_attempts': total_attempts,
        'average_score': average_score,
        'top_score': top_score,
        'low_score': low_score,
        'most_attempted_quiz': most_attempted_quiz,
    })

def view_questions(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    questions = quiz.questions.all()

    return render(request, 'quiz_app/view_questions.html', {
        'quiz': quiz,
        'questions': questions
    })

def delete_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    quiz.delete()
    return redirect('dashboard')

