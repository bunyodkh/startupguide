from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render, redirect

from hub.models import EcosystemEntity, ProgramCycle
from .forms import BuilderProfileForm
from .models import BuilderProfile


def people_list(request):
    people = (
        BuilderProfile.objects
        .filter(is_published=True)
        .select_related('user')
        .prefetch_related('affiliated_entities__category')
        .order_by('user__first_name', 'user__last_name')
    )

    grouped = {}
    ungrouped = []
    for person in people:
        entity = person.affiliated_entities.first()
        if entity and entity.category:
            key = entity.category.name
            grouped.setdefault(key, []).append(person)
        else:
            ungrouped.append(person)

    groups = [(label, members) for label, members in sorted(grouped.items())]
    if ungrouped:
        groups.append((None, ungrouped))

    return render(request, 'users/people_list.html', {'groups': groups})


@login_required
def manage_profile(request):
    profile, _ = BuilderProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile_form = BuilderProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            profile.refresh_from_db()
            ctx = {
                'form': BuilderProfileForm(instance=profile),
                'profile': profile,
                'success': True,
            }
            if request.headers.get('HX-Request'):
                return render(request, 'users/partials/profile_form.html', ctx)
            return redirect('users:manage_profile')
        if request.headers.get('HX-Request'):
            return render(request, 'users/partials/profile_form.html', {
                'form': profile_form,
                'profile': profile,
            })
    else:
        profile_form = BuilderProfileForm(instance=profile)

    return render(request, 'users/manage_profile.html', {
        'form': profile_form,
        'profile': profile,
    })


def view_profile(request, slug):
    cycles_qs = ProgramCycle.objects.select_related('program').only(
        'id', 'title', 'cycle_number',
        'program__id', 'program__name', 'program__short_name',
    ).order_by('program__name', '-cycle_number')

    programs_qs = EcosystemEntity.objects.only('id', 'name', 'short_name').order_by('name')

    profile = (
        BuilderProfile.objects
        .select_related('user')
        .prefetch_related(
            'affiliated_entities',
            Prefetch('coordinated_programs', queryset=programs_qs),
            Prefetch('contributed_cycles', queryset=cycles_qs),
        )
        .filter(slug=slug)
        .first()
    )
    if not profile:
        return render(request, 'users/profile_not_found.html', status=404)

    return render(request, 'users/view_profile.html', {
        'profile': profile,
    })