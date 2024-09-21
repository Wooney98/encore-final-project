from django.shortcuts import render,redirect
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from .forms import CreateUserForm
from django.contrib.auth import login, authenticate, logout
from Account.forms import UserForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages, auth
from django.contrib.auth.hashers import check_password
# def test(reauests):
#     return render(reauests,'test.html')

#이렇게 redirect를 사용하면 해당 페이지로 바로 이동 가능.
#메인 페이지로 접속하지만 바로 register페이지로 넘어가는 것을 볼 수 있음.
def test(requests):
    # template_name = 'test.html'
    return redirect("login")

class Cal_t(TemplateView):
    template_name = 'index1.html'

class Index2(TemplateView):
    template_name = 'index2.html' 

class Index(TemplateView):
    template_name = 'index.html' 

class RegisterPage(TemplateView):
    template_name = 'register.html'

class BoardPage(TemplateView):
    template_name = 'board.html'
    
#계정 생성 처리 부분
class UserCreateView(CreateView):
    form_class = CreateUserForm #forms.py에 정의 되어 있는 form 클래스
    template_name = 'register.html' #보여질 template(html파일)파일 이름.
    #form에 입력 된 내용에 에러가 없고, 테이블 레코드 생성이 완료된 후 이동할 url 지정
    #success_url 역시 CreateView 상속 안에 있는 내용으로 만약 계정 생성이 성공할 경우 어느 페이지로 넘길건지에 대한 정보를 담음
    success_url = reverse_lazy('register_done') #url패턴 전달 인자, urls.py 모듈이 메모리 로딩 된 후에 실행
    
#계정 생성 완료됐다는 페이지 이동
class UserCreateDoneTV(TemplateView):
    #템플릿만 넘기면 됨. 데이터를 입력하거나 가져올 필요가 없음.
    template_name = 'register_done.html' #보여질 템플릿 파일 이름.

def login_view(request, *args, **kwargs):
    context = {}

    user = request.user
    if user.is_authenticated:
        return redirect("/board/")
    
    if request.POST:
        email = request.POST.get('username')
        password = request.POST.get('password')
        print(email)
        print(password)
        user = authenticate(email=email, password=password)
        print(user)
        if user:
            login(request, user)
            return redirect("/board/")
        else:
            context = {"fail":"입력하신 정보가 잘못되었습니다."}
            # return redirect("login")
 
    return render(request, "registration/login.html", context)

def get_redirect_if_exists(request):
    redirect = None
    if request.GET:
        if request.GET.get("next"):
            redirect = str(request.GET.get("next"))
    return redirect

def change_password(request):
    context= {}
    if request.method == "POST":
        print("ok")
        user = request.user
        origin_password = request.POST["origin_password"]
        if check_password(origin_password, user.password):
            print("ok1")
            new_password = request.POST["new_password"]
            print(len(new_password))
            confirm_password = request.POST["confirm_password"]
            if len(new_password) < 8:
                print(len(new_password))
                context.update({'error':"8자 이상으로 입력해주세요"})  
                return render(request, 'registration/password_change.html',context = context)
            else:
                if new_password == confirm_password:
                    print("ok2")
                    user.set_password(new_password)
                    user.save()
                    return redirect('/accounts/logout')
                else:
                    print("ok3")
                    messages.error(request, 'Password not same')
                    context.update({'error':"새로운 비밀번호를 다시 확인해주세요."})
                    return render(request, 'registration/password_change.html',context = context)
        else:
            context.update({'error':"현재 비밀번호가 일치하지 않습니다."})
            messages.error(request, 'Password not correct')
        return render(request, 'registration/password_change.html', context = context)
    else:
        return render(request, 'registration/password_change.html')