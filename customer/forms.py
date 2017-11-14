from django import forms
from customer.models import Customer
from common.models import Address, Comment


class CustomerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}
        self.fields['phone'].required = False
        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({
            'placeholder': 'Last Name'})
        #self.fields['account_name'].widget.attrs.update({
        #    'placeholder': 'Account Name'})

    class Meta:
        model = Customer
        fields = (
            'title', 'first_name', 'last_name', 'org', 'phone', 'email', 'activity', 'description'
        )

    def clean_phone(self):
        client_phone = self.cleaned_data.get('phone', None)
        if client_phone:
            try:
                if int(client_phone) and not client_phone.isalpha():
                    ph_length = str(client_phone)
                    if len(ph_length) < 10 or len(ph_length) > 13:
                        raise forms.ValidationError('Phone number must be minimum 10 Digits and maximum 13 Digits')
            except (ValueError):
                raise forms.ValidationError('Phone Number should contain only Numbers')
            return client_phone


class CustomerCommentForm(forms.ModelForm):
    comment = forms.CharField(max_length=64, required=True)

    class Meta:
        model = Comment
        fields = ('comment', 'contact', 'commented_by')
