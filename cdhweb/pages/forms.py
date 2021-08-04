from django import forms


class SiteSearchForm(forms.Form):
    """Search form for finding pages across the site."""

    FILTER_CHOICES = (
        ("everything", "everything"),
        ("people", "people"),
        ("updates", "updates"),
        ("projects", "projects"),
        ("events", "events"),
    )

    # keyword query
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "type": "search",
                "placeholder": "Search pages, people, projects, updates & events",
            }
        ),
    )

    # filter to different page types
    filter = forms.ChoiceField(choices=FILTER_CHOICES)
