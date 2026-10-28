from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
import datetime

from .models import Book, BookCategory, LibraryMember, BookIssue
from .forms import BookForm, BookCategoryForm, LibraryMemberForm, BookIssueForm

# ==========================================
# BOOKS CRUD & INVENTORY
# ==========================================

@login_required
def book_list_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user) or (hasattr(request.user, 'profile') and request.user.profile.is_doctor)):
        messages.error(request, "Access restricted to authorized members.")
        return redirect('home')

    search_query = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')

    books = Book.objects.select_related('category').all()

    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query) |
            Q(book_id__icontains=search_query) |
            Q(publisher__icontains=search_query)
        )

    if category_id:
        books = books.filter(category_id=category_id)

    if status_filter:
        books = books.filter(status=status_filter)

    categories = BookCategory.objects.all()
    form = BookForm()
    category_form = BookCategoryForm()

    # Quick metrics
    total_books = sum(b.total_copies for b in books) if not search_query and not category_id else Book.objects.count()
    total_titles = Book.objects.count()
    available_copies = sum(b.available_copies for b in Book.objects.all())
    borrowed_copies = BookIssue.objects.filter(status__in=['Issued', 'Overdue']).count()
    total_members = LibraryMember.objects.count()

    return render(request, 'library/book_list.html', {
        'books': books,
        'categories': categories,
        'form': form,
        'category_form': category_form,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_status': status_filter,
        'total_titles': total_titles,
        'total_books': total_books,
        'available_copies': available_copies,
        'borrowed_copies': borrowed_copies,
        'total_members': total_members,
    })


@login_required
def book_create_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied. Admin access required.")
        return redirect('book_list')

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f"Book '{book.title}' ({book.book_id}) registered successfully!")
            return redirect('book_list')
        else:
            messages.error(request, "Error adding book. Please check required fields.")
    else:
        form = BookForm()

    return render(request, 'library/book_form.html', {'form': form, 'title': 'Add New Book to Smart Library'})


@login_required
def book_update_view(request, pk):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied.")
        return redirect('book_list')

    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f"Book '{book.title}' updated successfully!")
            return redirect('book_list')
        else:
            messages.error(request, "Error updating book details.")
    else:
        form = BookForm(instance=book)

    return render(request, 'library/book_form.html', {'form': form, 'book': book, 'title': f'Edit Book: {book.title}'})


@login_required
def book_delete_view(request, pk):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied.")
        return redirect('book_list')

    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f"Book '{title}' removed from library catalog.")
        return redirect('book_list')

    return render(request, 'library/book_confirm_delete.html', {'book': book})


@login_required
def book_category_create_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied.")
        return redirect('book_list')

    if request.method == 'POST':
        form = BookCategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Book category '{cat.name}' created.")
        else:
            messages.error(request, "Error creating category.")
    return redirect('book_list')


# ==========================================
# MEMBERS / STUDENTS CRUD
# ==========================================

@login_required
def member_list_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Access restricted to administrators.")
        return redirect('home')

    search_query = request.GET.get('search', '').strip()
    member_type = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')

    members = LibraryMember.objects.prefetch_related('borrow_records').all()

    if search_query:
        members = members.filter(
            Q(name__icontains=search_query) |
            Q(member_id__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(department__icontains=search_query)
        )

    if member_type:
        members = members.filter(member_type=member_type)

    if status_filter:
        members = members.filter(status=status_filter)

    form = LibraryMemberForm()

    total_students = LibraryMember.objects.filter(member_type='Student').count()
    total_staff = LibraryMember.objects.exclude(member_type='Student').count()

    return render(request, 'library/member_list.html', {
        'members': members,
        'form': form,
        'search_query': search_query,
        'selected_type': member_type,
        'status_filter': status_filter,
        'total_members': members.count(),
        'total_students': total_students,
        'total_staff': total_staff,
    })


@login_required
def member_create_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied.")
        return redirect('member_list')

    if request.method == 'POST':
        form = LibraryMemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f"Member '{member.name}' ({member.member_id}) enrolled successfully!")
            return redirect('member_list')
        else:
            messages.error(request, "Error adding member. Please check fields.")
    else:
        form = LibraryMemberForm(initial={'joined_date': datetime.date.today()})

    return render(request, 'library/member_form.html', {'form': form, 'title': 'Register New Library Member / Student'})


@login_required
def member_update_view(request, pk):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied.")
        return redirect('member_list')

    member = get_object_or_404(LibraryMember, pk=pk)
    if request.method == 'POST':
        form = LibraryMemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f"Member '{member.name}' updated successfully!")
            return redirect('member_list')
        else:
            messages.error(request, "Error updating member.")
    else:
        form = LibraryMemberForm(instance=member)

    return render(request, 'library/member_form.html', {'form': form, 'member': member, 'title': f'Edit Member: {member.name}'})


@login_required
def member_delete_view(request, pk):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied.")
        return redirect('member_list')

    member = get_object_or_404(LibraryMember, pk=pk)
    if request.method == 'POST':
        name = member.name
        member.delete()
        messages.success(request, f"Member '{name}' deleted.")
        return redirect('member_list')

    return render(request, 'library/member_confirm_delete.html', {'member': member})


# ==========================================
# BOOK ISSUE & RETURN CIRCULATION
# ==========================================

@login_required
def issue_list_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Access restricted to administrators.")
        return redirect('home')

    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')

    issues = BookIssue.objects.select_related('book', 'member').all()

    if search_query:
        issues = issues.filter(
            Q(issue_id__icontains=search_query) |
            Q(book__title__icontains=search_query) |
            Q(member__name__icontains=search_query) |
            Q(member__member_id__icontains=search_query)
        )

    if status_filter:
        issues = issues.filter(status=status_filter)

    books_available = Book.objects.filter(available_copies__gt=0)
    members_active = LibraryMember.objects.filter(status='Active')
    
    form = BookIssueForm(initial={
        'issue_date': datetime.date.today(),
        'due_date': datetime.date.today() + datetime.timedelta(days=14)
    })

    issued_count = BookIssue.objects.filter(status='Issued').count()
    overdue_count = BookIssue.objects.filter(status='Overdue').count()
    returned_count = BookIssue.objects.filter(status='Returned').count()

    return render(request, 'library/issue_list.html', {
        'issues': issues,
        'books_available': books_available,
        'members_active': members_active,
        'form': form,
        'search_query': search_query,
        'status_filter': status_filter,
        'issued_count': issued_count,
        'overdue_count': overdue_count,
        'returned_count': returned_count,
        'today': datetime.date.today(),
    })


@login_required
def issue_create_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied.")
        return redirect('issue_list')

    if request.method == 'POST':
        form = BookIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            book = issue.book
            if book.available_copies <= 0:
                messages.error(request, f"Sorry, all copies of '{book.title}' are currently borrowed out!")
                return redirect('issue_list')

            # Decrement available copies
            book.available_copies -= 1
            book.save()

            issue.save()
            messages.success(request, f"Book '{book.title}' issued successfully to {issue.member.name} (Due: {issue.due_date})!")
            return redirect('issue_list')
        else:
            messages.error(request, "Error issuing book. Please check details.")
    return redirect('issue_list')


@login_required
def return_book_view(request, pk):
    """Marks an issued book as Returned, calculates fine if overdue, and increases available copies."""
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied.")
        return redirect('issue_list')

    issue = get_object_or_404(BookIssue, pk=pk)
    if issue.status != 'Returned':
        today = datetime.date.today()
        issue.return_date = today
        issue.status = 'Returned'
        
        # Calculate fine if returned past due date
        if today > issue.due_date:
            days_late = (today - issue.due_date).days
            issue.fine_amount = days_late * 5.0  # 5 per day

        issue.save()

        # Restock book available copies
        book = issue.book
        book.available_copies += 1
        book.save()

        messages.success(request, f"Book '{book.title}' successfully returned by {issue.member.name}. Fine applied: ${issue.fine_amount:.2f}")
    else:
        messages.info(request, "This book has already been marked as returned.")

    return redirect('issue_list')
