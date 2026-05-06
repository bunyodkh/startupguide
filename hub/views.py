from django.db.models import Case, When, Value, IntegerField, Subquery, OuterRef, F
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404

from users.models import BuilderProfile
from wiki.models import Resource
from .models import EcosystemEntity, EntityCategory, ProgramCycle


_ACTIVE_STATUSES = [
    ProgramCycle.ProgramStatus.ACCEPTING,
    ProgramCycle.ProgramStatus.UPCOMING,
    ProgramCycle.ProgramStatus.IN_PROGRESS,
]

_CYCLE_STATUS_ORDER = Case(
    When(active_status=ProgramCycle.ProgramStatus.ACCEPTING,   then=Value(0)),
    When(active_status=ProgramCycle.ProgramStatus.UPCOMING,    then=Value(1)),
    When(active_status=ProgramCycle.ProgramStatus.IN_PROGRESS, then=Value(2)),
    default=Value(3),
    output_field=IntegerField(),
)

_active_cycle_qs = ProgramCycle.objects.filter(
    is_active=True,
    status__in=_ACTIVE_STATUSES,
).order_by('-cycle_number')


def index(request):
    categories = EntityCategory.objects.prefetch_related('entities').all()

    people = (
        BuilderProfile.objects
        .filter(is_published=True, show_on_main_page=True)
        .select_related('user')
        .prefetch_related('affiliated_entities')
        .order_by('user__first_name', 'user__last_name')
    )

    places = (
        EcosystemEntity.objects
        .filter(has_physical_space=True, is_active=True)
        .select_related('category', 'parent')
        .order_by('name')
    )

    latest_cycle_status = (
        ProgramCycle.objects
        .filter(program=OuterRef('pk'), is_active=True, status__in=_ACTIVE_STATUSES)
        .order_by('-cycle_number')
        .values('status')[:1]
    )
    latest_cycle_deadline = (
        ProgramCycle.objects
        .filter(program=OuterRef('pk'), is_active=True, status__in=_ACTIVE_STATUSES)
        .order_by('-cycle_number')
        .values('registration_deadline')[:1]
    )

    programs_qs = (
        EcosystemEntity.objects
        .filter(has_physical_space=False, is_active=True)
        .filter(cycles__is_active=True, cycles__status__in=_ACTIVE_STATUSES)
        .distinct()
        .select_related('category', 'parent')
        .prefetch_related(
            Prefetch('cycles', queryset=_active_cycle_qs, to_attr='active_cycles')
        )
        .annotate(
            active_status=Subquery(latest_cycle_status),
            active_deadline=Subquery(latest_cycle_deadline),
            status_order=_CYCLE_STATUS_ORDER,
        )
        .order_by('status_order', F('active_deadline').asc(nulls_last=True))
    )

    programs = [
        (program, program.active_cycles[0] if program.active_cycles else None)
        for program in programs_qs
    ]

    resources = (
        Resource.objects
        .filter(is_published=True)
        .select_related('category', 'author')
        .order_by('category__name', 'title')
    )

    return render(request, 'index.html', {
        'categories': categories,
        'people': people,
        'places': places,
        'programs': programs,
        'resources': resources,
    })


def program_detail(request, pk):
    program = get_object_or_404(
        EcosystemEntity.objects.select_related('category', 'parent'),
        pk=pk,
        has_physical_space=False,
    )
    cycles = (
        program.cycles
        .filter(is_active=True)
        .prefetch_related('coordinators__user', 'organizers', 'regions')
        .order_by('-cycle_number')
    )
    latest_cycle = cycles.first()
    return render(request, 'hub/program_detail.html', {
        'program': program,
        'cycles': cycles,
        'latest_cycle': latest_cycle,
    })
