from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import *

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm

from django.core.paginator import Paginator


from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models import Q
from django.db.models import Subquery
# Create your views here.


def route(request):
    # return redirect('/home')
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
    itemList = Item.objects.filter()
    statusRequestList = request.GET.getlist('status')
    conditionRequestList = request.GET.getlist('condition')
    categoryRequestList = request.GET.getlist('category')
    search = request.GET.get('search')
    if statusRequestList:
        itemList = itemList.filter(status__id__in=statusRequestList)
    if conditionRequestList:
        itemList = itemList.filter(condition__id__in=conditionRequestList)
    if categoryRequestList:
        itemList = itemList.filter(category__id__in=categoryRequestList)
    if search:
        itemList = itemList.filter(name__icontains = search)
    else:
        search = "";
    itemList = itemList.order_by("-createdOn")
    paginator = Paginator(itemList, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    categoryList = Category.objects.filter(active=True).order_by("name")
    conditionList = Condition.objects.filter(active=True).order_by("name")
    statusList = Status.objects.filter(active=True).order_by("name")
    return render(request, 'item.html', { "page_obj":page_obj,
                                         "total_page":range(1,paginator.num_pages+1),
                                         "showFilter":True,"categoryList":categoryList,
                                         "conditionList":conditionList,
                                         "statusList":statusList,
                                         "statusRequestList":[int(x) for x in statusRequestList],
                                         "conditionRequestList":[int(x) for x in conditionRequestList],
                                         "categoryRequestList":[int(x) for x in categoryRequestList],
                                         "search":search
                                         })

@login_required(login_url="/login/")
def viewLotPage(request, id):
    itemObj = get_object_or_404(Item, id=id)
    if request.method == "POST":
        itemBidForm = ItemBidForm(request.POST or None, prefix="itemBidForm", instance=itemObj)
        if itemBidForm.is_valid():
            if not itemObj.user == request.user:
                itemPriceHistory = ItemPriceHistory()
                itemPriceHistory.user = request.user
                itemPriceHistory.item = itemObj
                itemPriceHistory.price = itemBidForm['price_input'].value()
                itemPriceHistory.save()
    itemBidForm = ItemBidForm(prefix="itemBidForm")
    itemBidForm.fields['price_input'].widget.attrs = {
        **itemBidForm.fields['price_input'].widget.attrs,
        **{"min":itemObj.current_price() + itemObj.min_increase_price,
           "max":itemObj.current_price() + itemObj.max_increase_price,}
        }
    bidPriceList = {}
    if itemObj.user == request.user:
        priceList = ItemPriceHistory.objects.filter(item = itemObj).order_by("-createdOn")
        paginator = Paginator(priceList, 10)  # Show 10 contacts per page.
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        bidPriceList = {"page_obj":page_obj, "total_page":range(1,paginator.num_pages+1)}
    return render(request, 'viewLot.html', { **{"item":itemObj, "itemBidForm":itemBidForm}, **bidPriceList })    

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
                user.is_active=True
                user.save()
                setPasswordForm.save()
                userDetail = userDetailForm.save(commit=False)
                userDetail.user = user
                userDetail.save()
                return redirect('/login')
        else:
            try:
                if User.objects.filter(username=userForm['username'].value()):
                    message_danger = "Username already taken!"
                else:
                    for error in userForm.errors:
                            if not message_danger:
                                message_danger = ""
                            message_danger = message_danger + setPasswordForm.errors[error]
                    for error in userDetailForm.errors:
                            if not message_danger:
                                message_danger = ""
                            message_danger = message_danger + setPasswordForm.errors[error]
            except:...
       
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
    elif module == "item":
        commentList = Comment.objects.filter(item = id).order_by("-createdOn")
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
            # print('Please correct the error below.')
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
    if not request.user.is_superuser: 
        raise Http404
    conditionList = Condition.objects.filter().order_by("-createdOn")
    paginator = Paginator(conditionList, 10)  # Show 10 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'condition.html', { "page_obj":page_obj, "total_page":range(1,paginator.num_pages+1)})

@login_required(login_url="/login/")
def conditionAddPage(request):
    if not request.user.is_superuser: 
        raise Http404
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
    if not request.user.is_superuser: 
        raise Http404
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
    if not request.user.is_superuser: 
        raise Http404
    statusList = Status.objects.filter().order_by("-createdOn")
    paginator = Paginator(statusList, 10)  # Show 10 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'status.html', { "page_obj":page_obj, "total_page":range(1,paginator.num_pages+1)})

@login_required(login_url="/login/")
def statusAddPage(request):
    if not request.user.is_superuser: 
        raise Http404
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
    if not request.user.is_superuser: 
        raise Http404
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
    if not request.user.is_superuser: 
        raise Http404
    categoryList = Category.objects.filter().order_by("-createdOn")
    paginator = Paginator(categoryList, 10)  # Show 10 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'category.html', { "page_obj":page_obj, "total_page":range(1,paginator.num_pages+1)})

@login_required(login_url="/login/")
def categoryAddPage(request):
    if not request.user.is_superuser: 
        raise Http404
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
    if not request.user.is_superuser: 
        raise Http404
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

@login_required(login_url="/login/")
def itemPage(request):
    itemList = Item.objects.filter(user = request.user)
    statusRequestList = request.GET.getlist('status')
    conditionRequestList = request.GET.getlist('condition')
    categoryRequestList = request.GET.getlist('category')
    search = request.GET.get('search')
    if statusRequestList:
        itemList = itemList.filter(status__id__in=statusRequestList)
    if conditionRequestList:
        itemList = itemList.filter(condition__id__in=conditionRequestList)
    if categoryRequestList:
        itemList = itemList.filter(category__id__in=categoryRequestList)
    if search:
        itemList = itemList.filter(name__icontains = search)
    else:
        search = "";
    itemList = itemList.order_by("-createdOn")
    paginator = Paginator(itemList, 10)  # Show 10 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    categoryList = Category.objects.filter(active=True).order_by("name")
    conditionList = Condition.objects.filter(active=True).order_by("name")
    statusList = Status.objects.filter(active=True).order_by("name")
    return render(request, 'item.html', { "page_obj":page_obj,
                                         "total_page":range(1,paginator.num_pages+1),
                                         "showAdd":True,
                                         "showFilter":True,"categoryList":categoryList,
                                         "conditionList":conditionList,
                                         "statusList":statusList,
                                         "statusRequestList":[int(x) for x in statusRequestList],
                                         "conditionRequestList":[int(x) for x in conditionRequestList],
                                         "categoryRequestList":[int(x) for x in categoryRequestList],
                                         "search":search})

@login_required(login_url="/login/")
def itemAddPage(request):
    if request.method == "POST":
        itemForm = ItemForm(request.POST or None, request.FILES, prefix="itemForm")
        if itemForm.is_valid():
            item = itemForm.save(commit=False)
            item.user = request.user
            item.save()
            # if commentForm.is_valid():
            #     comment = commentForm.save(commit=False)
            #     comment.user = request.user
            #     comment.text = "Add:_" + comment.text
            #     comment.save()
            #     item.comment.add(comment)
            return redirect("itemPage")
    itemForm = ItemForm(prefix="itemForm")
    return render(request, 'itemForm.html', { "itemForm":itemForm})

@login_required(login_url="/login/")
def itemEditPage(request, id):
    itemObj = get_object_or_404(Item, id=id)
    old_status = itemObj.status.id
    if request.method == "POST":
        commentForm = CommentForm(request.POST or None, prefix="commentForm")
        itemForm = ItemForm(request.POST or None, request.FILES, prefix="itemForm", instance=itemObj)
        if itemForm.is_valid():
            item = itemForm.save(commit=False)
            item.save()
            itemForm.save_m2m()
            if old_status != itemForm['status'].value():
                itemStatusHistory = ItemStatusHistory()
                itemStatusHistory.user = request.user
                itemStatusHistory.status = item.status
                itemStatusHistory.item = item
                itemStatusHistory.save()
            if commentForm.is_valid():
                comment = commentForm.save(commit=False)
                comment.user = request.user
                comment.text = "Edit:_" + comment.text
                comment.save()
                item.comment.add(comment)
            return redirect("itemPage")
    commentForm = CommentForm(prefix="commentForm")
    itemForm = ItemForm(prefix="itemForm", instance=itemObj, initial = {"category":Category.objects.filter(item__id=id).values_list("id", flat=True)})
    return render(request, 'itemForm.html', {"commentForm":commentForm, "itemForm":itemForm, "id":id})

@login_required(login_url="/login/")
def itemMyBidPage(request):
    itemList = Item.objects.filter(itempricehistory__user = request.user).order_by("-createdOn")
    statusRequestList = request.GET.getlist('status')
    conditionRequestList = request.GET.getlist('condition')
    categoryRequestList = request.GET.getlist('category')
    search = request.GET.get('search')
    if statusRequestList:
        itemList = itemList.filter(status__id__in=statusRequestList)
    if conditionRequestList:
        itemList = itemList.filter(condition__id__in=conditionRequestList)
    if categoryRequestList:
        itemList = itemList.filter(category__id__in=categoryRequestList)
    if search:
        itemList = itemList.filter(name__icontains = search)
    else:
        search = "";
    itemList = itemList.distinct().order_by("-createdOn")
    paginator = Paginator(itemList, 10)  # Show 10 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    categoryList = Category.objects.filter(active=True).order_by("name")
    conditionList = Condition.objects.filter(active=True).order_by("name")
    statusList = Status.objects.filter(active=True).order_by("name")
    return render(request, 'item.html', { "page_obj":page_obj,
                                         "total_page":range(1,paginator.num_pages+1),
                                         "showAdd":False,
                                         "showFilter":True,"categoryList":categoryList,
                                         "conditionList":conditionList,
                                         "statusList":statusList,
                                         "statusRequestList":[int(x) for x in statusRequestList],
                                         "conditionRequestList":[int(x) for x in conditionRequestList],
                                         "categoryRequestList":[int(x) for x in categoryRequestList],
                                         "search":search})


@login_required(login_url="/login/")
def usersPage(request):
    if not request.user.is_superuser: 
        raise Http404
    userDetailList = UserDetail.objects.filter().order_by("user__pk")
    paginator = Paginator(userDetailList, 10)  # Show 10 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'users.html', { "page_obj":page_obj, "total_page":range(1,paginator.num_pages+1)})

@login_required(login_url="/login/")
def usersEditPage(request, id):
    if not request.user.is_superuser: 
        raise Http404
    message_danger = None
    userObj = get_object_or_404(User, id=id)
    userDetailObj = get_object_or_404(UserDetail, user=userObj)
    if request.method == "POST":
        userForm = UserForm(request.POST or None, prefix="userForm", instance = userObj)
        userDetailForm = UserDetailForm(request.POST or None, prefix="userDetailForm", instance = userDetailObj)
        commentForm = CommentForm(request.POST or None, prefix="commentForm")
        if userForm.is_valid():
            user = userForm.save(commit=False)
            user.save()
        if userDetailForm.is_valid():
            userDetail = userDetailForm.save(commit=False)
            userDetail.save()
        if commentForm.is_valid():
            comment = commentForm.save(commit=False)
            comment.user = request.user
            comment.text = "Edit:_" + comment.text
            comment.save()
            userDetail.comment.add(comment)
    userForm = UserForm(prefix="userForm", instance = userObj)
    userDetailForm = UserDetailForm(prefix="userDetailForm", instance = userDetailObj)
    commentForm = CommentForm(prefix="commentForm")
    return render(request, 'editProfile.html', {"userForm":userForm, "userDetailForm":userDetailForm, "message_danger":message_danger, "commentForm":commentForm })

@login_required(login_url="/login/")
def usersPasswordPage(request, id):
    if not request.user.is_superuser: 
        raise Http404
    message_danger = None
    message = None
    userObj = get_object_or_404(User, id=id)
    if request.method == "POST":
        setPasswordForm = SetPasswordForm(userObj, request.POST, prefix="setPasswordForm")
        if not setPasswordForm.is_valid():
            print(1)
            for error in setPasswordForm.errors:
                if not message_danger:
                    message_danger = ""
                message_danger = message_danger + setPasswordForm.errors[error]
        else:
            print(2)
            setPasswordForm.user = userObj
            setPasswordForm.save()
            message = "Password Updated"
    setPasswordForm = SetPasswordForm(userObj, prefix="setPasswordForm")
    setPasswordForm.fields['new_password1'].widget.attrs = {
        'class':'form-control'
    }
    setPasswordForm.fields['new_password2'].widget.attrs = {
        'class':'form-control'
    }
    return render(request, 'password.html', {"setPasswordForm":setPasswordForm, "message_danger":message_danger, "message":message})

@login_required(login_url="/login/")
def messageChatPage(request, id):
    itemObj = get_object_or_404(Item, id=id)
    if itemObj.user == request.user:
        raise Http404
    messageForm = MessageForm(request.POST or None, prefix="messageForm")
    if request.method == "POST":
        if messageForm.is_valid():
            message = messageForm.save(commit=False)
            message.message_from = request.user
            message.message_to = itemObj.user
            message.item = itemObj
            message.save()
    messageForm = MessageForm(prefix="messageForm")
    messageList = Message.objects.filter(item = itemObj).filter(Q(message_from = request.user) | Q(message_to = request.user)).order_by("createdOn")
    return render(request, 'message.html', { "messageForm":messageForm , "messageList":messageList} )

@login_required(login_url="/login/")
def messageChatAdminPage(request, id, user):
    itemObj = get_object_or_404(Item, id=id)
    userObj = get_object_or_404(User, id=user)
    if user == request.user or itemObj.user != request.user:
        raise Http404
    messageForm = MessageForm(request.POST or None, prefix="messageForm")
    if request.method == "POST":
        if messageForm.is_valid():
            message = messageForm.save(commit=False)
            message.message_from = request.user
            message.message_to = userObj
            message.item = itemObj
            message.save()
    messageForm = MessageForm(prefix="messageForm")
    messageList = Message.objects.filter(item = itemObj).filter(Q(message_from = userObj) | Q(message_to = userObj)).order_by("createdOn")
    return render(request, 'message.html', { "messageForm":messageForm , "messageList":messageList} )

@login_required(login_url="/login/")
def messageListPage(request):
    messageList = Message.objects.filter(
        pk__in= Subquery(Message.objects.filter(Q(message_from = request.user) | Q(message_to = request.user)).distinct("item").values('pk'))
    ).order_by("-createdOn")
    paginator = Paginator(messageList, 10)  # Show 10 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'messageList.html', { "page_obj":page_obj, "total_page":range(1,paginator.num_pages+1)})
