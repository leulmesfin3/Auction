from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import *

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm

from django.core.paginator import Paginator


from django.views.decorators.clickjacking import xframe_options_exempt
# Create your views here.


def route(request):
    if request.user.is_authenticated:
        return redirect('/home')
    return redirect('/login')


def mdPage(request):
    return render(request, 'md.html')

def loginPage(request):
    message_danger = None
    username = None
    if request.user.is_authenticated:
        return redirect("route")
    elif request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            return redirect('route')
        else:
            message_danger = "Invalid Username or Password"
    return render(request, 'login.html', {"message_danger":message_danger,
                                          "username":username if username else ""})


def logoutPage(request):
    logout(request)
    return redirect('/login')


@login_required(login_url="/login/")
def homePage(request):
    return render(request, 'home.html')

@login_required(login_url="/login/")
def viewLotPage(request):
    return render(request, 'viewLot.html')
        

def registerPage(request):
    message_danger = None
    if request.user.is_authenticated:
        return redirect("route")
    if request.method == "POST":
        userForm = UserForm(request.POST or None, prefix="userForm")
        userDetailForm = UserDetailForm(request.POST or None, prefix="userDetailForm")
        setPasswordForm = SetPasswordForm(request.user, request.POST, prefix="setPasswordForm")
        if userForm.is_valid() and userDetailForm.is_valid():
            user = userForm.save(commit=False)
            if not setPasswordForm.is_valid():
                for error in setPasswordForm.errors:
                    if not message_danger:
                        message_danger = ""
                    message_danger = message_danger + setPasswordForm.errors[error]
            else:
                setPasswordForm.user = user
                user.save()
                setPasswordForm.save()
                userDetail = userDetailForm.save(commit=False)
                userDetail.user = user
                userDetail.save()
                return redirect('/login')
    userDetailForm = UserDetailForm(prefix="userDetailForm")
    userForm = UserForm(prefix="userForm")
    setPasswordForm = SetPasswordForm(request.POST, prefix="setPasswordForm")
    setPasswordForm.fields['new_password1'].widget.attrs = {
        'class':'form-control'
    }
    setPasswordForm.fields['new_password2'].widget.attrs = {
        'class':'form-control'
    }
    return render(request, 'register.html', {"userForm":userForm, "userDetailForm":userDetailForm ,"setPasswordForm":setPasswordForm, "message_danger":message_danger})


@login_required(login_url="/login/")
def editProfilePage(request):
    message_danger = None
    userObj = get_object_or_404(User, id=request.user.id)
    userDetailObj = get_object_or_404(UserDetail, user=userObj)
    if request.method == "POST":
        userForm = UserForm(request.POST or None, prefix="userForm", instance = userObj)
        userDetailForm = UserDetailForm(request.POST or None, prefix="userDetailForm", instance = userDetailObj)
        if userForm.is_valid():
            user = userForm.save(commit=False)
            user.save()
        if userDetailForm.is_valid():
            userDetail = userDetailForm.save(commit=False)
            userDetail.save()
    userForm = UserForm(prefix="userForm", instance = userObj)
    userDetailForm = UserDetailForm(prefix="userDetailForm", instance = userDetailObj)
    return render(request, 'editProfile.html', {"userForm":userForm, "userDetailForm":userDetailForm, "message_danger":message_danger })


login_required(login_url="/login/")
@xframe_options_exempt
def commentPage(request, module, id):
    commentList = {}
    if module == "condition":
        commentList = Comment.objects.filter(condition = id).order_by("-createdOn")
    elif module == "category":
        commentList = Comment.objects.filter(category = id).order_by("-createdOn")
    elif module == "status":
        commentList = Comment.objects.filter(status = id).order_by("-createdOn")
    return render(request, 'comment.html', {"commentList": commentList})



@login_required(login_url="/login/")
def changePasswordPage(request):
    message_danger = None
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('route')
        else:
            print('Please correct the error below.')
            for error in form.errors:
                if not message_danger:
                    message_danger = ""
                message_danger = message_danger + form.errors[error]
    else:
        form = PasswordChangeForm(request.user)
    form.fields['old_password'].widget.attrs = {
        'class':'form-control'
    }
    form.fields['new_password1'].widget.attrs = {
        'class':'form-control'
    }
    form.fields['new_password2'].widget.attrs = {
        'class':'form-control'
    }
    return render(request, 'changePassword.html', {'form': form, "message_danger":message_danger})


@login_required(login_url="/login/")
def conditionPage(request):
    conditionList = Condition.objects.filter().order_by("createdOn")
    paginator = Paginator(conditionList, 10)  # Show 25 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'condition.html', { "page_obj":page_obj, "total_page":range(1,paginator.num_pages+1)})


@login_required(login_url="/login/")
def conditionAddPage(request):
    if request.method == "POST":
        commentForm = CommentForm(request.POST or None, prefix="commentForm")
        conditionForm = ConditionForm(request.POST or None, prefix="conditionForm")
        if conditionForm.is_valid():
            condition = conditionForm.save(commit=False)
            condition.save()
            if commentForm.is_valid():
                comment = commentForm.save(commit=False)
                comment.user = request.user
                comment.text = "Add:_" + comment.text
                comment.save()
                condition.comment.add(comment)
            return redirect("conditionPage")
    commentForm = CommentForm(prefix="commentForm")
    conditionForm = ConditionForm(prefix="conditionForm")
    return render(request, 'conditionForm.html', {"commentForm":commentForm, "conditionForm":conditionForm})

@login_required(login_url="/login/")
def conditionEditPage(request, id):
    conditionObj = get_object_or_404(Condition, id=id)
    if request.method == "POST":
        commentForm = CommentForm(request.POST or None, prefix="commentForm")
        conditionForm = ConditionForm(request.POST or None, prefix="conditionForm", instance=conditionObj)
        if conditionForm.is_valid():
            condition = conditionForm.save(commit=False)
            condition.save()
            if commentForm.is_valid():
                comment = commentForm.save(commit=False)
                comment.user = request.user
                comment.text = "Edit:_" + comment.text
                comment.save()
                condition.comment.add(comment)
            return redirect("conditionPage")
    commentForm = CommentForm(prefix="commentForm")
    conditionForm = ConditionForm(prefix="conditionForm", instance=conditionObj)
    return render(request, 'conditionForm.html', {"commentForm":commentForm, "conditionForm":conditionForm, "id":id})



@login_required(login_url="/login/")
def statusPage(request):
    statusList = Status.objects.filter().order_by("createdOn")
    paginator = Paginator(statusList, 10)  # Show 25 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'status.html', { "page_obj":page_obj, "total_page":range(1,paginator.num_pages+1)})


@login_required(login_url="/login/")
def statusAddPage(request):
    if request.method == "POST":
        commentForm = CommentForm(request.POST or None, prefix="commentForm")
        statusForm = StatusForm(request.POST or None, prefix="statusForm")
        if statusForm.is_valid():
            status = statusForm.save(commit=False)
            status.save()
            if commentForm.is_valid():
                comment = commentForm.save(commit=False)
                comment.user = request.user
                comment.text = "Add:_" + comment.text
                comment.save()
                status.comment.add(comment)
            return redirect("statusPage")
    commentForm = CommentForm(prefix="commentForm")
    statusForm = StatusForm(prefix="statusForm")
    return render(request, 'statusForm.html', {"commentForm":commentForm, "statusForm":statusForm})

@login_required(login_url="/login/")
def statusEditPage(request, id):
    statusObj = get_object_or_404(Status, id=id)
    if request.method == "POST":
        commentForm = CommentForm(request.POST or None, prefix="commentForm")
        statusForm = StatusForm(request.POST or None, prefix="statusForm", instance=statusObj)
        if statusForm.is_valid():
            status = statusForm.save(commit=False)
            status.save()
            if commentForm.is_valid():
                comment = commentForm.save(commit=False)
                comment.user = request.user
                comment.text = "Edit:_" + comment.text
                comment.save()
                status.comment.add(comment)
            return redirect("statusPage")
    commentForm = CommentForm(prefix="commentForm")
    statusForm = StatusForm(prefix="statusForm", instance=statusObj)
    return render(request, 'statusForm.html', {"commentForm":commentForm, "statusForm":statusForm, "id":id})

@login_required(login_url="/login/")
def categoryPage(request):
    categoryList = Category.objects.filter().order_by("createdOn")
    paginator = Paginator(categoryList, 10)  # Show 25 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'category.html', { "page_obj":page_obj, "total_page":range(1,paginator.num_pages+1)})

@login_required(login_url="/login/")
def categoryAddPage(request):
    if request.method == "POST":
        commentForm = CommentForm(request.POST or None, prefix="commentForm")
        categoryForm = CategoryForm(request.POST or None, prefix="categoryForm")
        if categoryForm.is_valid():
            category = categoryForm.save(commit=False)
            category.save()
            if commentForm.is_valid():
                comment = commentForm.save(commit=False)
                comment.user = request.user
                comment.text = "Add:_" + comment.text
                comment.save()
                category.comment.add(comment)
            return redirect("categoryPage")
    commentForm = CommentForm(prefix="commentForm")
    categoryForm = CategoryForm(prefix="categoryForm")
    return render(request, 'categoryForm.html', {"commentForm":commentForm, "categoryForm":categoryForm})

@login_required(login_url="/login/")
def categoryEditPage(request, id):
    categoryObj = get_object_or_404(Category, id=id)
    if request.method == "POST":
        commentForm = CommentForm(request.POST or None, prefix="commentForm")
        categoryForm = CategoryForm(request.POST or None, prefix="categoryForm", instance=categoryObj)
        if categoryForm.is_valid():
            category = categoryForm.save(commit=False)
            category.save()
            if commentForm.is_valid():
                comment = commentForm.save(commit=False)
                comment.user = request.user
                comment.text = "Edit:_" + comment.text
                comment.save()
                category.comment.add(comment)
            return redirect("categoryPage")
    commentForm = CommentForm(prefix="commentForm")
    categoryForm = CategoryForm(prefix="categoryForm", instance=categoryObj)
    return render(request, 'categoryForm.html', {"commentForm":commentForm, "categoryForm":categoryForm, "id":id})
