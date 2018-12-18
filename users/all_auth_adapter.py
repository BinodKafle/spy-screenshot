from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter


# Overwrites email confirmation url so that the correct url is sent in the email.
# to change the actual address, see core.urls name: 'account_confirm_email'
class MyAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        url = "/account_confirm_email/{}/".format(emailconfirmation.key)
        return settings.FRONTEND_HOST + url

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """

        from allauth.account.utils import user_username, user_email, user_field

        data = form.cleaned_data
        # first_name = data.get('first_name')
        # last_name = data.get('last_name')
        print(data)
        name = data.get('name')
        user_type = data.get('user_type')
        email = data.get('email')
        username = data.get('username')
        user_email(user, email)


        # user_username(user, username)
        # if first_name:
        #     user_field(user, 'first_name', first_name)
        # if last_name:
        #     user_field(user, 'last_name', last_name)
        if name:
            user_field(user, 'name', name)
        if user_type:
            user_field(user, 'user_type', user_type)
        if zip:
            user_field(user, 'zip', zip)
        if 'password1' in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        self.populate_username(request, user)
        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            user.save()
        return user
