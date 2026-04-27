from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import BuilderProfileForm, UserInfoForm
from .models import BuilderProfile


@login_required
def manage_profile(request):
    profile, _ = BuilderProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserInfoForm(request.POST, instance=request.user)
        profile_form = BuilderProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            profile.refresh_from_db()
            ctx = {
                'user_form': UserInfoForm(instance=request.user),
                'form': BuilderProfileForm(instance=profile),
                'profile': profile,
                'success': True,
            }
            if request.headers.get('HX-Request'):
                return render(request, 'users/partials/profile_form.html', ctx)
            return redirect('users:manage_profile')
        if request.headers.get('HX-Request'):
            return render(request, 'users/partials/profile_form.html', {
                'user_form': user_form,
                'form': profile_form,
                'profile': profile,
            })
    else:
        user_form = UserInfoForm(instance=request.user)
        profile_form = BuilderProfileForm(instance=profile)

    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'form': profile_form,
        'profile': profile,
    })
