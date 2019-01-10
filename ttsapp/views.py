from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from ttsapp.models import Uploads, Userkeys
from uuid import uuid4
from ttsapp.tasks import convert_file_to_mp3
from datetime import datetime
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from ttsapp.utils import account_activation_token


class SignupPageView(View):
    """
        endpoint: /signup
        purpose: "handles signup of an user"
    """
    def get(self, request):
        """

        :param request: None
        :return: render signup form with fields email, first_name, last_name, passowrd
        """
        template_name = 'signup.html'
        context = {"signup_page": "active"}
        return render(request, template_name=template_name, context=context)

    def post(self, request):
        """
        :param request: email and password, confirm_password are mandatory to this api
        :return: sends success message if signup success, else display error messages
        """
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        c_password = request.POST.get('password_confirmation')
        if c_password != password:
            context = {"signup_page": "active", "messages": {"level": "danger", "short": "Error!",
                                                             "msg": "Password doesn't match with confirm password"}}
            return render(request, template_name='signup.html', context=context)

        user = User.objects.filter(username=email)

        if user.exists():
            context = {"signup_page": "active", "messages": {"level": "danger", "short": "Error!",
                                                             "msg": "Email address already exists"}}
            return render(request, template_name='signup.html', context=context)
        elif email and password:
            u = User()
            u.username = email
            u.email = email
            u.first_name = first_name
            u.last_name = last_name
            u.set_password(password)
            u.is_active = False
            u.save()

            #email part
            mail_subject = 'Activate your user account.'
            current_site = get_current_site(request)
            message = render_to_string('acc_active_email.html', {
                'user': u,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(u.pk)).decode(),
                'token': account_activation_token.make_token(u),
            })
            to_email = email
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            context = {"signup_page": "active", "messages": {"level": "success", "short": "Success! ",
                                                             "msg": "Please confirm your email address to "
                                                                    "complete the registration"}}
            return render(request, template_name='signup.html', context=context)

        return


class ActivateView(View):
    """
        This is an view for activating email link for view
    """
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            current_site = get_current_site(request)
            url = "http://" + current_site.domain + "/login/"
            msg = 'Thank you for your email confirmation. Now you can login your account <a href=%s >here</a>' % url
            return HttpResponse(msg)
        else:
            return HttpResponse('Activation link is invalid!')


class LoginPageView(View):
    """
        endpoint: /login
        purpose: to authenticate users
    """

    def get(self, request):
        """
        :param request: None
        :return: render login form with username and password fields
        """
        template_name = 'login.html'
        context = {"login_page": "active"}
        return render(request, template_name=template_name, context=context)

    def post(self, request):
        """
        :param request: email, password are needed to authenticate
        :return: if login success redirect to another page else display error message
        """

        template_name = 'login.html'
        context = {"login_page": "active"}
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(username=username).first()
        if user is not None and not user.is_active:
            context["messages"] = {"msg": "Email Verification Pending", "level": "danger", "short": "Error! "}
            return render(request=request, template_name=template_name, context=context)

        if user is not None:
            # A backend authenticated the credentials
            user = authenticate(username=username, password=password)
            if user and user.is_authenticated:
                login(request, user)
                context["messages"] = {"msg": "login successful", "level": "success", "short": "Success! "}
                return redirect(self.request.GET.get('next', '/'))

            else:
                context["messages"] = {"msg": "wrong password", "level": "danger", "short": "Error! "}
                return render(request=request, template_name=template_name, context=context)
        else:
            # No backend authenticated the credentials
            context["messages"] = {"msg": "User not found", "level": "danger", "short": "Error! "}
            return render(request=request, template_name=template_name, context=context)


class LogoutView(View):
    """
        endpoint: /logout
        purpose: Handles logout of an user
    """
    def get(self, request):
        """
        :param request: request headers
        :return: renders login page
        """
        logout(request)
        return redirect('/login')


class AboutPageView(View):
    """
        endpoint: /about
        purpose: this handles about page views
    """

    def get(self, request):
        """
        :param request: None
        :return: render about page
        """
        template_name = 'about.html'
        context = {"about_page": "active"}
        return render(request=request, template_name=template_name, context=context)


class HomePageView(View):
    """
        endpoint: /
        purpose: this handles Home page views
    """
    def get(self, request):
        """
        :param request: None
        :return: render home page
        """
        template_name = 'home.html'
        context = {"home_page": "active"}
        if request.user and request.user.is_authenticated:
            upobjs = Uploads.objects.filter(user=request.user, is_active=True).order_by('-created_on')
        else:
            upobjs = []
        master_list = []
        for i in upobjs:
            status = "Under Process" if not i.is_processed else "Processed"
            d_link = None if not i.output_file else settings.SERVER_URL + i.output_file
            master_list.append({"file_name": i.file_name, "created_on": i.created_on.strftime("%d-%m-%Y"),
                                "status": status, "output_file": d_link, "is_processed": i.is_processed})
        context["files"] = master_list
        return render(request=request, template_name=template_name, context=context)


class Fileupload(View):
    """
            endpoint: /upload
            purpose: this handles file uploads views
        """

    def get(self, request):
        """
        :param request: None
        :return: render upload page
        """
        template_name = 'upload.html'
        context = {"upload_page": "active"}
        return render(request=request, template_name=template_name, context=context)

    def post(self, request):
        """
        :param request: files and return link
        :return: render file  page
        """
        template_name = 'upload.html'

        context = {}
        print(request.FILES)
        if request.FILES['myfile']:
            try:
                myfile = request.FILES['myfile']
                file_path = 'uploads/' + '%s/%s' % (datetime.today().strftime("%Y/%m/%d"), str(request.user.id)
)
                fs = FileSystemStorage(location=file_path)
                filename = fs.save(myfile.name, myfile)
                uploaded_file_url = fs.url(filename)
                # save file paths in uploads table
                fname = uploaded_file_url.split('media')[-1]
                upobj = Uploads()
                upobj.user = request.user
                upobj.file_name = myfile.name
                upobj.file_path = file_path + fname
                upobj.save()

                # call celery task here
                convert_file_to_mp3.delay(int(upobj.id))
                return redirect('/')
                # context = {"upload_page": "active", "messages": {"level": "success", "msg": "File Uploaded "
                #                                                                             "Successfully",
                #                                                                             "short": "Success! "}}
            except Exception as e:
                context = {"upload_page": "active", "messages": {"level": "danger", "msg": str(e),
                                                                 "short": "Error! "}}
        else:
            context = {"upload_page": "active", "messages": {"level": "danger", "msg": "No files found",
                                                            "short": "Error! "}}
        return render(request=request, template_name=template_name, context=context)


class PreferenceView(View):
    """
        endpoint: /user/preferences/
        purpose: handles user api keys generation and deactivation
    """
    def get(self, request):
        template_name = 'preferences.html'
        context = {"api_key": ""}
        if request.user:
            keyobj = Userkeys.objects.filter(user=request.user).first()
            api_key = keyobj.api_key if keyobj else ""
            context["api_key"] = api_key
        return render(request=request, template_name=template_name, context=context)

    def post(self, request):
        template_name = 'preferences.html'
        context = {}
        if request.user:
            keyobj = Userkeys.objects.create(user=request.user, api_key=str(uuid4()))
            keyobj.save()
            api_key = keyobj.api_key
            context["api_key"] = api_key
        return render(request=request, template_name=template_name, context=context)

    def put(self, request):
        template_name = 'preferences.html'
        context = {}
        if request.user:
            keyobj = Userkeys.objects.filter(user=request.user).first()
            keyobj.api_key = ""
            keyobj.save()
            api_key = ""
            context["api_key"] = api_key
        return render(request=request, template_name=template_name, context=context)