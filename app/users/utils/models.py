from django.db.models import ImageField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _


class SizeRestrictedImageField(ImageField):
    """
    Same as ImageField, but you can specify:
          max_upload_size - a number indicating the maximum file size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB - 104857600
            250MB - 214958080
            500MB - 429916160
    """

    def __init__(self, *args, **kwargs):
        self.max_upload_size = kwargs.pop("max_upload_size", 0)

        super(SizeRestrictedImageField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(SizeRestrictedImageField, self).clean(*args, **kwargs)

        image = data.file
        if image.size > self.max_upload_size:
            raise forms.ValidationError(
                _("Please keep filesize under %s. Current filesize %s")
                % (filesizeformat(self.max_upload_size), filesizeformat(image.size))
            )

        return data


def group_moderator_create(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="moderator")
