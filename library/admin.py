from django.contrib import admin
from .models import Book, BookCategory, LibraryMember, BookIssue

@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'title', 'author', 'category', 'total_copies', 'available_copies', 'shelf_location', 'status')
    list_filter = ('status', 'category')
    search_fields = ('book_id', 'title', 'author', 'isbn', 'publisher')

@admin.register(LibraryMember)
class LibraryMemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'name', 'email', 'phone', 'member_type', 'department', 'status', 'joined_date')
    list_filter = ('member_type', 'status', 'department')
    search_fields = ('member_id', 'name', 'email', 'phone')

@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ('issue_id', 'book', 'member', 'issue_date', 'due_date', 'return_date', 'status', 'fine_amount')
    list_filter = ('status', 'issue_date', 'due_date')
    search_fields = ('issue_id', 'book__title', 'member__name', 'member__member_id')
