from django import forms
from .models import *

class UserForm(forms.ModelForm):
    # password = forms.CharField(widget=forms.PasswordInput)
    # confirmPassword = forms.CharField(widget=forms.PasswordInput),"confirmPassword", "password"
    class Meta:
        model = User
        fields = ("username", "first_name" , "last_name", "email", "is_active")
        
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
        
class StatusForm(forms.ModelForm):
    # backgroundColor = ColorField(widget=ColorWidget(attrs={'palette': COLOR_CHOICES}))
    class Meta:
        model = Status
        fields = ("name", "backgroundColor", "active")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'class':'form-control'}
        self.fields['backgroundColor'].widget.attrs = {'class':'form-control'}
        self.fields['active'].widget.attrs = {'class':'form-check-input'}
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "active")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'class':'form-control'}
        self.fields['active'].widget.attrs = {'class':'form-check-input'}
        
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ("img",
                  "name", 
                  "starting_price", 
                  "min_increase_price", 
                  "max_increase_price", 
                  "condition", 
                  "status", 
                  "category", 
                  "description",
                  "tag",)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'class':'form-control'}
        self.fields['tag'].widget.attrs = {'class':'form-control'}
        self.fields['starting_price'].widget.attrs = {'class':'form-control', 'step': 1}
        self.fields['min_increase_price'].widget.attrs = {'class':'form-control', 'step': 1}
        self.fields['max_increase_price'].widget.attrs = {'class':'form-control', 'step': 1}
        self.fields['condition'].widget.attrs = {'class':'form-control form-select'}   
        self.fields['status'].widget.attrs = {'class':'form-control form-select'}   
        self.fields['category'].widget.attrs = {'class':'form-control form-select'}
        self.fields['description'].widget.attrs={  "placeholder": "Start typing here",
                                            "class": "form-control",
                                            "style": "height:100px; width:100%"} 


class ItemBidForm(forms.ModelForm):
    price_input = forms.DecimalField()
    class Meta:
        model = Item
        fields = ("price_input", )
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price_input'].widget.attrs = {'class':'form-control'}
        
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("text", )
        # exclude = ("user", )
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs={  "placeholder": "Start typing here",
                                            "class": "form-control",
                                            "style": "height:100px; width:100%"}    