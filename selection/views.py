from django.shortcuts import render, redirect
from .forms import UserForm, RegistrationForm, LoginForm, SelectionForm, DuesForm, NoDuesForm, StudentDetailsForm
from django.http import HttpResponse, Http404
from selection.models import Student, Room, Hostel
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.save()
            Student.objects.create(user=new_user)
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password1'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('login/edit/')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid Login')
    else:
        form = UserForm()
        args = {'form': form}
        return render(request, 'reg_form.html', args)


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password'])
            if user is not None:
                if user.is_warden:
                    return HttpResponse('Invalid Login')
                if user.is_active:
                    login(request, user)
                    student = request.user.student
                    return render(request, 'profile.html', {'student': student})
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid Login')
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})


def warden_login(request):
    user = request.user
    if user is not None:
        try:
            if user.is_warden and user.is_active:
                login(request, user)
                room_list = request.user.warden.hostel.room_set.all()
                context = {'rooms': room_list}
                return render(request, 'warden.html', context)
        except BaseException:
            pass
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password'])
            if user is not None:
                if not user.is_warden:
                    return HttpResponse('Invalid Login')
                elif user.is_active:
                    login(request, user)
                    room_list = request.user.warden.hostel.room_set.all()
                    context = {'rooms': room_list}
                    return render(request, 'warden.html', context)
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid Login')
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})


@login_required
def edit(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, instance=request.user.student)
        if form.is_valid():
            form.save()
            student = request.user.student
            return render(request, 'profile.html', {'student': student})
    else:
        form = RegistrationForm(instance=request.user.student)
        return render(request, 'edit.html', {'form': form})


@login_required
def select(request):
    if request.user.student.room:
        return HttpResponse('You have already selected room - ' + str(request.user.student.room) + '. Please contact your Hostel Caretaker or Warden')

    if request.method == 'POST':
        if not request.user.student.no_dues:
            return HttpResponse('You have dues. Please contact your Hostel Caretaker or Warden')
        form = SelectionForm(request.POST, instance=request.user.student)
        if form.is_valid():
            if request.user.student.room_id:
                request.user.student.room_allotted = True
                room_id = request.user.student.room_id
                room = Room.objects.get(id=room_id)
                room.vacant = False
                room.save()
            form.save()
            student = request.user.student
            return render(request, 'profile.html', {'student': student})
    else:
        if not request.user.student.no_dues:
            return HttpResponse('You have dues. Please contact your Hostel Caretaker or Warden')
        form = SelectionForm(instance=request.user.student)
        student_gender = request.user.student.gender
        student_course = request.user.student.course
        student_room_type = request.user.student.course.room_type
        hostel = Hostel.objects.filter(
            gender=student_gender, course=student_course)
        filtered_rooms = Room.objects.none()
        if student_room_type == 'B':
            for i in range(len(hostel)):
                h_id = hostel[i].id
                filtered_room = Room.objects.filter(
                    hostel_id=h_id, room_type=['S', 'D'], vacant=True)
                filtered_rooms = filtered_rooms | filtered_room
        else :
            for i in range(len(hostel)):
                h_id = hostel[i].id
                filtered_room = Room.objects.filter(
                    hostel_id=h_id, room_type=student_room_type, vacant=True)
                filtered_rooms = filtered_rooms | filtered_room
        form.fields["room"].queryset = filtered_rooms
        return render(request, 'select_room.html', {'form': form})


@login_required
def warden_dues(request):
    user = request.user
    if user is not None:
        if not user.is_warden:
            return HttpResponse('Invalid Login')
        else:
            students = Student.objects.all()
            return render(request, 'dues.html', {'students': students})
    else:
        return HttpResponse('Invalid Login')


@login_required
def warden_add_due(request):
    user = request.user
    if user is not None:
        if not user.is_warden:
            return HttpResponse('Invalid Login')
        else:
            if request.method == "POST":
                form = DuesForm(request.POST)
                if form.is_valid():
                    student = form.cleaned_data.get('choice')
                    student.no_dues = False
                    student.save()
                    return HttpResponse('Done')
            else:
                form = DuesForm()
                return render(request, 'add_due.html', {'form': form})
    else:
        return HttpResponse('Invalid Login')


@login_required
def warden_remove_due(request):
    user = request.user
    if user is not None:
        if not user.is_warden:
            return HttpResponse('Invalid Login')
        else:
            if request.method == "POST":
                form = NoDuesForm(request.POST)
                if form.is_valid():
                    student = form.cleaned_data.get('choice')
                    student.no_dues = True
                    student.save()
                    return HttpResponse('Done')
            else:
                form = NoDuesForm()
                return render(request, 'remove_due.html', {'form': form})
    else:
        return HttpResponse('Invalid Login')


def logout_view(request):
    logout(request)
    return redirect('/')


def hostel_detail_view(request, hostel_name):
    try:
        this_hostel = Hostel.objects.get(name=hostel_name)
    except Hostel.DoesNotExist:
        raise Http404("Invalid Hostel Name")
    context = {
        'hostel': this_hostel,
        'rooms': Room.objects.filter(
            hostel=this_hostel)}
    return render(request, 'hostels.html', context)


@login_required
def warden_student_list(request):
    user = request.user
    if user is not None:
        if not user.is_warden:
            return HttpResponse('Invalid Login')
        else:
            students = []
            for course in user.warden.hostel.course.all():
                students = students + list(Student.objects.all().filter(course=course))
            return render(request, 'warden_student_list.html', {'students': students})
    else:
        return HttpResponse('Invalid Login')


@login_required
def change_student_details(request, enrollment_no):
    user = request.user
    if user is not None:
        if not user.is_warden:
            return HttpResponse('Invalid Login')
        else:
            try:
                this_student = Student.objects.get(enrollment_no=enrollment_no)
                old_room_id = this_student.room_id
            except BaseException:
                raise Http404("Invalid Student or Room")
            if request.method == 'POST':
                form = StudentDetailsForm(request.POST, instance=this_student)
                if form.is_valid():


                    form.save()
                    print(str(old_room_id) + " " + str(this_student.room_id))
                    if not this_student.room_id:
                        # Clear room selection of this student
                        print("clear")
                        old_room = Room.objects.get(id=old_room_id)
                        old_room.vacant = True
                        old_room.save()
                        this_student.room_allotted = False
                        this_student.save()
                    elif old_room_id != this_student.room_id:
                        # Free the old room
                        print("switch")
                        old_room = Room.objects.get(id=old_room_id)
                        old_room.vacant = True
                        old_room.save()
                        # Allot new room
                        new_room = Room.objects.get(id=this_student.room_id)
                        new_room.vacant = False
                        new_room.save()
                    form = StudentDetailsForm(instance=this_student)
                    form.fields["room"].queryset = Room.objects.filter(vacant=True) | Room.objects.filter(id=this_student.room_id)
                    return render(request, 'change_student_details.html', {'form': form})
            else:
                form = StudentDetailsForm(instance=this_student)
                form.fields["room"].queryset = Room.objects.filter(vacant=True) | Room.objects.filter(
                    id=this_student.room_id)
                return render(request, 'change_student_details.html', {'form': form})
    else:
        return HttpResponse('Invalid Login')
