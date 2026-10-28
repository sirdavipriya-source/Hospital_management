from django import forms
from .models import Book, BookCategory, LibraryMember, BookIssue
import datetime

class BookCategoryForm(forms.ModelForm):
    class Meta:
        model = BookCategory
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Clinical Medicine', 'required': True}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MED-TXT'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Category scope...'}),
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'book_id', 'isbn', 'title', 'author', 'category', 'publisher', 'edition',
            'total_copies', 'available_copies', 'shelf_location', 'description', 'cover_image', 'cover_url', 'status'
        ]
        widgets = {
            'book_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. BK-1001 (auto if empty)'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '978-0-12-345678-9'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Book Title', 'required': True}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author(s)', 'required': True}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Elsevier / McGraw-Hill'}),
            'edition': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 21st Edition'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'required': True}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'required': True}),
            'shelf_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Shelf A - Section 3'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Abstract, topics covered...'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class LibraryMemberForm(forms.ModelForm):
    class Meta:
        model = LibraryMember
        fields = [
            'member_id', 'name', 'email', 'phone', 'member_type', 'department',
            'address', 'max_allowed_books', 'status', 'joined_date'
        ]
        widgets = {
            'member_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. STU-001 (auto if blank)'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'student@university.edu'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 12345'}),
            'member_type': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Medical Studies / Cardiology'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Hostel or Residence address'}),
            'max_allowed_books': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'joined_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class BookIssueForm(forms.ModelForm):
    class Meta:
        model = BookIssue
        fields = ['issue_id', 'book', 'member', 'issue_date', 'due_date', 'notes']
        widgets = {
            'issue_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ISS-001 (auto if empty)'}),
            'book': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'member': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Borrow remarks or condition note...'}),
        }
