from django.forms import ModelForm
from auctions.models import Listing

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class ListingForm(ModelForm):
	class Meta:
		model = Listing
		exclude = ["isActive", "seller"]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.layout = Layout(
			Row(
				Column("title", css_class="form-group col-md-8 mb-0"),
				Column("initialPrice", css_class="form-group col-md-4 mb-0"),
				css_class="form-row"
			),
			"description",
			Row(
				Column("imageUrl", css_class="form-group col-md-9 mb-0"),
				Column("category", css_class="form-group col-md-3 mb-0"),
				css_class="form-row"
			),
			Submit("submit", "Save and Exit")
		)