from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import BuilderProfileForm
from .models import BuilderProfile


@login_required
def create_profile(request):
    profile, _ = BuilderProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = BuilderProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                return render(request, 'partials/profile_success.html')
            return redirect('hub:index')
        if request.headers.get('HX-Request'):
            return render(request, 'partials/profile_form.html', {'form': form})
    else:
        form = BuilderProfileForm(instance=profile)

    return render(request, 'create_profile.html', {'form': form})
