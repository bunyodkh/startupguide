import random

from django import forms as django_forms
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, IntegerField, Subquery, OuterRef, F, Prefetch
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from users.models import BuilderProfile
from wiki.models import Resource
from .forms import CycleForm, RegistrationSettingsForm
from .models import (
    EcosystemEntity, EntityCategory, ProgramCycle,
    RegistrationForm, CustomField, RegistrationResponse,
)


# ── Constants ──────────────────────────────────────────────────────────────────

_LANGS = [
    ('en', 'Question in English'),
    ('ru', 'Вопрос на русском'),
    ('uz', "O'zbek tilidagi savol"),
]

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


# ── Helpers ────────────────────────────────────────────────────────────────────

def _is_coordinator(user, program):
    return program.coordinators.filter(user=user).exists()


def _get_reg_form(cycle):
    if not cycle:
        return None
    try:
        return cycle.registration_form
    except RegistrationForm.DoesNotExist:
        return None


def _build_apply_form_class(reg_form, custom_fields):
    fields = {
        'full_name': django_forms.CharField(
            max_length=255, label='Full Name',
            widget=django_forms.TextInput(attrs={'class': 'form-input'}),
        ),
        'email': django_forms.EmailField(
            label='Email',
            widget=django_forms.EmailInput(attrs={'class': 'form-input'}),
        ),
    }
    fields['phone'] = django_forms.CharField(
        max_length=50, required=True, label='Phone',
        widget=django_forms.TextInput(attrs={'class': 'form-input'}),
    )
    for cf in custom_fields:
        widget = (
            django_forms.Textarea(attrs={'class': 'form-input', 'rows': 3})
            if cf.field_type == 'textarea'
            else django_forms.TextInput(attrs={'class': 'form-input'})
        )
        fields[f'custom_{cf.pk}'] = django_forms.CharField(
            label=cf.label,
            required=cf.is_required,
            widget=widget,
        )
    return type('ApplyForm', (django_forms.BaseForm,), {'base_fields': fields})


# ── Public views ───────────────────────────────────────────────────────────────

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
        .order_by('?')[:3]
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
        .order_by('?')
    )

    all_pairs = [
        (program, cycle)
        for program in programs_qs
        for cycle in (program.active_cycles if program.active_cycles else [])
    ]
    programs = random.sample(all_pairs, min(3, len(all_pairs)))

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


def program_detail(request, slug):
    program = get_object_or_404(
        EcosystemEntity.objects
        .select_related('category', 'parent')
        .prefetch_related('coordinators__user'),
        slug=slug,
        has_physical_space=False,
    )
    cycles = (
        program.cycles
        .filter(is_active=True)
        .prefetch_related('contributors__user', 'organizers', 'regions')
        .order_by('-cycle_number')
    )
    cycle_slug = request.GET.get('cycle')
    if cycle_slug:
        latest_cycle = cycles.filter(slug=cycle_slug).first() or cycles.first()
    else:
        latest_cycle = cycles.first()

    reg_form = _get_reg_form(latest_cycle)
    custom_fields = list(reg_form.custom_fields.order_by('order')) if reg_form else []

    apply_form = None
    if reg_form and reg_form.is_open and not reg_form.external_url:
        ApplyForm = _build_apply_form_class(reg_form, custom_fields)
        apply_form = ApplyForm()

    user_is_coordinator = (
        request.user.is_authenticated and
        _is_coordinator(request.user, program)
    )

    return render(request, 'hub/program_detail.html', {
        'program': program,
        'cycles': cycles,
        'latest_cycle': latest_cycle,
        'user_is_coordinator': user_is_coordinator,
        'reg_form': reg_form,
        'apply_form': apply_form,
        'custom_fields': custom_fields,
    })


def program_apply(request, slug):
    if request.method != 'POST':
        return redirect('hub:view_program', slug=slug)

    program = get_object_or_404(EcosystemEntity, slug=slug, has_physical_space=False)
    cycle = program.cycles.filter(is_active=True).order_by('-cycle_number').first()
    reg_form = _get_reg_form(cycle)

    if not reg_form or not reg_form.is_open or reg_form.external_url:
        return HttpResponse(status=400)

    custom_fields = list(reg_form.custom_fields.order_by('order'))
    ApplyForm = _build_apply_form_class(reg_form, custom_fields)
    form = ApplyForm(request.POST)

    if form.is_valid():
        email = form.cleaned_data['email']
        if RegistrationResponse.objects.filter(form=reg_form, email=email).exists():
            return render(request, 'hub/partials/_apply_block.html', {
                'program': program,
                'reg_form': reg_form,
                'apply_form': ApplyForm(),
                'custom_fields': custom_fields,
                'already_applied': True,
            })
        custom_answers = {
            cf.label: form.cleaned_data.get(f'custom_{cf.pk}', '')
            for cf in custom_fields
        }
        RegistrationResponse.objects.create(
            form=reg_form,
            full_name=form.cleaned_data['full_name'],
            email=form.cleaned_data['email'],
            phone=form.cleaned_data.get('phone', ''),
            role=form.cleaned_data.get('role', ''),
            custom_answers=custom_answers,
        )
        return render(request, 'hub/partials/_apply_block.html', {
            'program': program,
            'applied': True,
            'apply_form': ApplyForm(),
            'custom_fields': custom_fields,
        })

    return render(request, 'hub/partials/_apply_block.html', {
        'program': program,
        'reg_form': reg_form,
        'apply_form': form,
        'custom_fields': custom_fields,
    })


# ── Coordinator views ──────────────────────────────────────────────────────────

@login_required
def program_manage(request, pk):
    program = get_object_or_404(
        EcosystemEntity.objects.prefetch_related('coordinators__user'),
        pk=pk,
        has_physical_space=False,
    )
    if not _is_coordinator(request.user, program):
        return render(request, 'hub/403.html', status=403)

    all_cycles = list(program.cycles.order_by('-cycle_number'))

    cycle_pk = request.GET.get('cycle')
    latest_cycle = next((c for c in all_cycles if str(c.pk) == cycle_pk), None) if cycle_pk else None

    reg_form = None
    if latest_cycle:
        reg_form, _ = RegistrationForm.objects.get_or_create(cycle=latest_cycle)

    custom_fields = list(reg_form.custom_fields.order_by('order')) if reg_form else []
    settings_form = RegistrationSettingsForm(instance=reg_form) if reg_form else None
    cycle_create_form = CycleForm()

    recent_responses = list(reg_form.responses.order_by('-submitted_at')[:10]) if reg_form else []
    cycle_form = CycleForm(instance=latest_cycle) if latest_cycle else None
    form_mode = _get_form_mode(reg_form, custom_fields) if reg_form else 'choice'

    return render(request, 'hub/program_manage.html', {
        'program': program,
        'all_cycles': all_cycles,
        'latest_cycle': latest_cycle,
        'reg_form': reg_form,
        'custom_fields': custom_fields,
        'settings_form': settings_form,
        'cycle_create_form': cycle_create_form,
        'recent_responses': recent_responses,
        'cycle': latest_cycle,
        'form': cycle_form,
        'langs': _LANGS,
        'form_mode': form_mode,
    })


@login_required
def form_responses(request, pk):
    program = get_object_or_404(EcosystemEntity, pk=pk, has_physical_space=False)
    if not _is_coordinator(request.user, program):
        return render(request, 'hub/403.html', status=403)

    cycle = program.cycles.filter(is_active=True).order_by('-cycle_number').first()
    reg_form = _get_reg_form(cycle)
    custom_fields = []
    responses = []

    if reg_form:
        custom_fields = list(reg_form.custom_fields.order_by('order'))
        responses = reg_form.responses.order_by('-submitted_at')

    return render(request, 'hub/form_responses.html', {
        'program': program,
        'cycle': cycle,
        'reg_form': reg_form,
        'custom_fields': custom_fields,
        'responses': responses,
    })


# ── Full-page cycle views ──────────────────────────────────────────────────────

@login_required
def cycle_list_page(request, pk):
    return redirect('hub:program_manage', pk=pk)


@login_required
def cycle_archive_view(request, pk, cycle_pk):
    program = get_object_or_404(EcosystemEntity, pk=pk, has_physical_space=False)
    if not _is_coordinator(request.user, program):
        return render(request, 'hub/403.html', status=403)
    if request.method == 'POST':
        cycle = get_object_or_404(ProgramCycle, pk=cycle_pk, program=program)
        cycle.is_active = not cycle.is_active
        cycle.save(update_fields=['is_active'])
    return redirect('hub:cycle_list', pk=program.pk)




@login_required
def cycle_create_page(request, pk):
    program = get_object_or_404(EcosystemEntity, pk=pk, has_physical_space=False)
    if not _is_coordinator(request.user, program):
        return render(request, 'hub/403.html', status=403)
    if request.method == 'POST':
        form = CycleForm(request.POST, request.FILES)
        if form.is_valid():
            cycle = form.save(commit=False)
            cycle.program = program
            cycle.save()
            return redirect('hub:program_manage', pk=program.pk)
    else:
        form = CycleForm()
    return render(request, 'hub/cycle_form.html', {
        'program': program,
        'form': form,
        'editing': False,
    })


@login_required
def cycle_edit_page(request, pk, cycle_pk):
    program = get_object_or_404(EcosystemEntity, pk=pk, has_physical_space=False)
    if not _is_coordinator(request.user, program):
        return render(request, 'hub/403.html', status=403)
    cycle = get_object_or_404(ProgramCycle, pk=cycle_pk, program=program)
    if request.method == 'POST':
        form = CycleForm(request.POST, request.FILES, instance=cycle)
        if form.is_valid():
            form.save()
            return redirect('hub:program_manage', pk=program.pk)
    else:
        form = CycleForm(instance=cycle)
    return render(request, 'hub/cycle_form.html', {
        'program': program,
        'cycle': cycle,
        'form': form,
        'editing': True,
    })


# ── HTMX: cycle endpoints ──────────────────────────────────────────────────────

def _cycles_ctx(program):
    return {
        'program': program,
        'cycles': list(program.cycles.order_by('-cycle_number')),
        'cycle_create_form': CycleForm(),
    }


@login_required
def cycle_htmx_item(request, pk, cycle_pk):
    program = get_object_or_404(EcosystemEntity, pk=pk, has_physical_space=False)
    if not _is_coordinator(request.user, program):
        return HttpResponse(status=403)
    cycle = get_object_or_404(ProgramCycle, pk=cycle_pk, program=program)
    return render(request, 'hub/partials/_cycle_item.html', {
        'program': program, 'cycle': cycle,
    })


@login_required
def cycle_htmx_edit(request, pk, cycle_pk):
    program = get_object_or_404(EcosystemEntity, pk=pk, has_physical_space=False)
    if not _is_coordinator(request.user, program):
        return HttpResponse(status=403)
    cycle = get_object_or_404(ProgramCycle, pk=cycle_pk, program=program)

    if request.method == 'POST':
        form = CycleForm(request.POST, request.FILES, instance=cycle)
        if form.is_valid():
            form.save()
            return render(request, 'hub/partials/_cycle_item.html', {
                'program': program, 'cycle': cycle,
            })
        return render(request, 'hub/partials/_cycle_item_edit.html', {
            'program': program, 'cycle': cycle, 'form': form,
        })

    form = CycleForm(instance=cycle)
    return render(request, 'hub/partials/_cycle_item_edit.html', {
        'program': program, 'cycle': cycle, 'form': form,
    })


@login_required
def cycle_htmx_create(request, pk):
    program = get_object_or_404(EcosystemEntity, pk=pk, has_physical_space=False)
    if not _is_coordinator(request.user, program):
        return HttpResponse(status=403)

    if request.method == 'POST':
        form = CycleForm(request.POST, request.FILES)
        if form.is_valid():
            cycle = form.save(commit=False)
            cycle.program = program
            cycle.save()
            ctx = _cycles_ctx(program)
            return render(request, 'hub/partials/_cycles_section.html', ctx)
        ctx = _cycles_ctx(program)
        ctx['cycle_create_form'] = form
        return render(request, 'hub/partials/_cycles_section.html', ctx)

    return HttpResponse(status=405)


# ── HTMX: active cycle inline edit ────────────────────────────────────────────

def _active_cycle_ctx(program, cycle, form=None):
    if form is None:
        form = CycleForm(instance=cycle) if cycle else CycleForm()
    return {'program': program, 'cycle': cycle, 'form': form}


@login_required
def cycle_manage_htmx(request, pk):
    program = get_object_or_404(EcosystemEntity, pk=pk, has_physical_space=False)
    if not _is_coordinator(request.user, program):
        return HttpResponse(status=403)
    cycle = program.cycles.order_by('-cycle_number').first()
    if not cycle:
        return HttpResponse(status=404)
    if request.method == 'POST':
        form = CycleForm(request.POST, request.FILES, instance=cycle)
        if form.is_valid():
            form.save()
            cycle.refresh_from_db()
            form = CycleForm(instance=cycle)
        return render(request, 'hub/partials/_active_cycle_form.html',
                      _active_cycle_ctx(program, cycle, form))
    return HttpResponse(status=405)


# ── HTMX: form settings endpoints ─────────────────────────────────────────────

def _get_form_mode(reg_form, custom_fields):
    if reg_form.external_url:
        return 'link'
    if reg_form.is_open or custom_fields:
        return 'form'
    return 'choice'


def _form_section_ctx(program, reg_form):
    custom_fields = list(reg_form.custom_fields.order_by('order'))
    return {
        'program': program,
        'cycle': reg_form.cycle,
        'reg_form': reg_form,
        'settings_form': RegistrationSettingsForm(instance=reg_form),
        'custom_fields': custom_fields,
        'form_mode': _get_form_mode(reg_form, custom_fields),
        'langs': _LANGS,
    }


@login_required
def form_settings_htmx(request, pk, cycle_pk):
    program = get_object_or_404(EcosystemEntity, pk=pk, has_physical_space=False)
    if not _is_coordinator(request.user, program):
        return HttpResponse(status=403)

    cycle = get_object_or_404(ProgramCycle, pk=cycle_pk, program=program)
    reg_form = _get_reg_form(cycle)
    if not reg_form:
        return HttpResponse(status=404)

    if request.method == 'POST':
        form = RegistrationSettingsForm(request.POST, instance=reg_form)
        if form.is_valid():
            form.save()
            reg_form.refresh_from_db()

    return render(request, 'hub/partials/_form_section.html',
                  _form_section_ctx(program, reg_form))


@login_required
def field_add_htmx(request, pk, cycle_pk):
    program = get_object_or_404(EcosystemEntity, pk=pk, has_physical_space=False)
    if not _is_coordinator(request.user, program):
        return HttpResponse(status=403)

    cycle = get_object_or_404(ProgramCycle, pk=cycle_pk, program=program)
    reg_form = _get_reg_form(cycle)
    if not reg_form:
        return HttpResponse(status=404)

    if request.method == 'POST':
        label_en = request.POST.get('label_en', '').strip()
        label_ru = request.POST.get('label_ru', '').strip()
        label_uz = request.POST.get('label_uz', '').strip()
        base_label = label_en or label_ru or label_uz
        if base_label:
            order = reg_form.custom_fields.count()
            CustomField.objects.create(
                form=reg_form,
                label=base_label,
                label_en=label_en or None,
                label_ru=label_ru or None,
                label_uz=label_uz or None,
                field_type=request.POST.get('field_type', 'text'),
                is_required='is_required' in request.POST,
                order=order,
            )

    return render(request, 'hub/partials/_form_section.html',
                  _form_section_ctx(program, reg_form))


@login_required
def field_delete_htmx(request, pk, cycle_pk, field_pk):
    program = get_object_or_404(EcosystemEntity, pk=pk, has_physical_space=False)
    if not _is_coordinator(request.user, program):
        return HttpResponse(status=403)

    cycle = get_object_or_404(ProgramCycle, pk=cycle_pk, program=program)
    reg_form = _get_reg_form(cycle)
    if not reg_form:
        return HttpResponse(status=404)

    reg_form.custom_fields.filter(pk=field_pk).delete()
    return render(request, 'hub/partials/_form_section.html',
                  _form_section_ctx(program, reg_form))


@login_required
def cycle_toggle_htmx(request, pk, cycle_pk):
    program = get_object_or_404(EcosystemEntity, pk=pk, has_physical_space=False)
    if not _is_coordinator(request.user, program):
        return HttpResponse(status=403)
    cycle = get_object_or_404(ProgramCycle, pk=cycle_pk, program=program)
    cycle.is_active = not cycle.is_active
    cycle.save(update_fields=['is_active'])
    return render(request, 'hub/partials/_cycle_table_row.html', {
        'cycle': cycle,
        'program': program,
    })


def cycle_register_page(request, slug):
    cycle = get_object_or_404(
        ProgramCycle.objects.select_related('program').prefetch_related('organizers', 'regions'),
        slug=slug,
        is_active=True,
    )
    program = cycle.program
    reg_form = _get_reg_form(cycle)

    if reg_form and reg_form.external_url:
        return redirect(reg_form.external_url)

    if not reg_form or not reg_form.is_open:
        return render(request, 'hub/cycle_register.html', {
            'cycle': cycle, 'program': program, 'closed': True,
        })

    custom_fields = list(reg_form.custom_fields.order_by('order'))
    ApplyForm = _build_apply_form_class(reg_form, custom_fields)
    applied = False
    already_applied = False
    form = ApplyForm()

    if request.method == 'POST':
        form = ApplyForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if RegistrationResponse.objects.filter(form=reg_form, email=email).exists():
                already_applied = True
            else:
                custom_answers = {
                    cf.label: form.cleaned_data.get(f'custom_{cf.pk}', '')
                    for cf in custom_fields
                }
                RegistrationResponse.objects.create(
                    form=reg_form,
                    full_name=form.cleaned_data['full_name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data.get('phone', ''),
                    role=form.cleaned_data.get('role', ''),
                    custom_answers=custom_answers,
                )
                applied = True
                form = ApplyForm()

    return render(request, 'hub/cycle_register.html', {
        'cycle': cycle,
        'program': program,
        'apply_form': form,
        'custom_fields': custom_fields,
        'applied': applied,
        'already_applied': already_applied,
    })
