from django import forms
from .models import *

class UserForm(forms.ModelForm):
    # password = forms.CharField(widget=forms.PasswordInput)
    # confirmPassword = forms.CharField(widget=forms.PasswordInput),"confirmPassword", "password"
    class Meta:
        model = User
        fields = ("username", "first_name" , "last_name", "email")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs = {'class':'form-control'}
        self.fields['first_name'].widget.attrs = {'class':'form-control'}
        self.fields['last_name'].widget.attrs = {'class':'form-control'}
        self.fields['email'].widget.attrs = {'class':'form-control'}
        # self.fields['password'].widget.attrs = {'class':'form-control'}
        # self.fields['confirmPassword'].widget.attrs = {'class':'form-control'}

class UserDetailForm(forms.ModelForm):
    class Meta:
        model = UserDetail
        fields = ("phone",)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs = {'class':'form-control'}
 
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("user", "text",)
        # exclude = ("user", )
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].widget.attrs = {'class':'form-control'}
        self.fields['text'].widget.attrs={  "placeholder": "Start typing here",
                                            "class": "form-control",
                                            "style": "height:100px; width:100%"}       

class ConditionForm(forms.ModelForm):
    class Meta:
        model = Condition
        fields = ("name", "active")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'class':'form-control'}
        self.fields['active'].widget.attrs = {'class':'form-check-input'}
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "active")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'class':'form-control'}
        self.fields['active'].widget.attrs = {'class':'form-check-input'}