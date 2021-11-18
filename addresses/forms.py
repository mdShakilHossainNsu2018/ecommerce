from django import forms

from .models import Address


class AddressForm(forms.ModelForm):
    """
    User-related CRUD form
    """

    nickname = forms.CharField(label='',
                               widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                             "placeholder": "Enter Your nickname."}))

    name = forms.CharField(label='',
                           widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                         "placeholder": "Enter Your Name."}))
    address_line_1 = forms.CharField(label='',
                                     widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                                   "placeholder": "Address line 1"}))

    address_line_2 = forms.CharField(label='',
                                     widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                                   "placeholder": "Address line 2"}))

    city = forms.CharField(label='',
                           widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                         "placeholder": "Your City"}))

    country = forms.CharField(label='',
                              widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                            "placeholder": "Your Country"}))
    state = forms.CharField(label='',
                            widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                          "placeholder": "Your State"}))

    postal_code = forms.CharField(label='',
                                  widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                                "placeholder": "Your Postal Code"}))

    class Meta:
        model = Address
        fields = [
            'nickname',
            'name',
            # 'billing_profile',
            'address_type',
            'address_line_1',
            'address_line_2',
            'city',
            'country',
            'state',
            'postal_code'
        ]


class AddressCheckoutForm(forms.ModelForm):
    """
    User-related checkout address create form
    """
    nickname = forms.CharField(label='',
                               widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                             "placeholder": "Enter Your nickname."}))

    name = forms.CharField(label='',
                           widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                         "placeholder": "Enter Your Name."}))
    address_line_1 = forms.CharField(label='',
                                     widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                                   "placeholder": "Address line 1"}))

    address_line_2 = forms.CharField(label='',
                                     widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                                   "placeholder": "Address line 2"}))

    city = forms.CharField(label='',
                           widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                         "placeholder": "Your City"}))

    country = forms.CharField(label='',
                              widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                            "placeholder": "Your Country"}))
    state = forms.CharField(label='',
                            widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                          "placeholder": "Your State"}))

    postal_code = forms.CharField(label='',
                                  widget=forms.TextInput(attrs={'class': 'fadeIn first login_input',
                                                                "placeholder": "Your Postal Code"}))

    class Meta:
        model = Address
        fields = [
            'nickname',
            'name',
            # 'billing_profile',
            # 'address_type',
            'address_line_1',
            'address_line_2',
            'city',
            'country',
            'state',
            'postal_code'
        ]
