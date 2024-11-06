from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import GroupCreationForm
from .models import Group
from django.contrib.auth.models import User

def home(request):
    return render(request, "chipin/home.html")

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupCreationForm(request.POST, user=request.user)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'Group "{group.name}" created successfully!')
            return redirect('chipin:group_detail', group_id=group.id)
    else:
        form = GroupCreationForm(user=request.user)  # Properly instantiate the form
    return render(request, 'chipin/create_group.html', {'form': form})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    return render(request, 'chipin/group_detail.html', {'group': group})

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user == group.admin:
        group.delete()
        messages.success(request, f'Group "{group.name}" has been deleted.')
    else:
        messages.error(request, "You do not have permission to delete this group.")
    return redirect('chipin:home')

@login_required
def accept_invite(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    user_id = request.GET.get('user_id')
    
    if user_id:
        invited_user = get_object_or_404(User, id=user_id)
        
        if invited_user in group.members.all():
            messages.info(request, f'{invited_user.username} is already a member of the group "{group.name}".')
        elif invited_user in group.invited_users.all():
            group.members.add(invited_user)  # Add the invited user to members
            group.invited_users.remove(invited_user)  # Remove from invited list
            messages.success(request, f'{invited_user.username} has successfully joined the group "{group.name}".')
        else:
            messages.error(request, "You are not invited to join this group.")
    else:
        messages.error(request, "Invalid invitation link.")
    
    return redirect('chipin:group_detail', group_id=group.id)

@login_required
def invite_users(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    users_not_in_group = User.objects.exclude(id__in=group.members.values_list('id', flat=True))
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        invited_user = get_object_or_404(User, id=user_id)

        if invited_user in group.invited_users.all():
            messages.info(request, f'{invited_user.username} has already been invited.')
        else:
            group.invited_users.add(invited_user)
            messages.success(request, f'Invitation sent to {invited_user.username}.')
        
        return redirect('chipin:group_detail', group_id=group.id)
    
    return render(request, 'chipin/invite_users.html', {
        'group': group,
        'users_not_in_group': users_not_in_group
    })
