from django import forms
from academics.models import Subject
from .models import ChatMessage


class ChatSubjectSelectForm(forms.Form):

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.filter(is_active=True),
        empty_label="Select Subject",
        widget=forms.Select(attrs={"class": "form-control"})
    )


class ChatMessageForm(forms.ModelForm):

    content = forms.CharField(
        max_length=1000,
        min_length=2,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ask your question...",
                "autocomplete": "off",
                "class": "form-control",
            }
        )
    )

    class Meta:
        model = ChatMessage
        fields = ["content"]

    def clean_content(self):
        message = self.cleaned_data.get("content", "").strip()

        if not message:
            raise forms.ValidationError("Message cannot be empty.")

        forbidden_keywords = ["http://", "https://", "<script", "</script>"]
        for keyword in forbidden_keywords:
            if keyword in message.lower():
                raise forms.ValidationError("Invalid content detected.")

        return message
