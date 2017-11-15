from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import modelformset_factory
from activity.models import Activity
from activity.forms import ActivityForm


# Create your views here.
@login_required
def activity_list(request):

    status = ['in process','converted','recycled','assigned','dead' ]
    activity_obj = sorted(Activity.objects.all().order_by('enddate','startdate'), key = lambda p:status.index(p.status))


    page = request.POST.get('per_page')

    #email = request.POST.get('email')
    #if email:
        #activity_obj = Activity.objects.filter(email__icontains=email)

    return render(request, 'activity/activity.html', {
        'activity_obj': activity_obj, 'per_page': page})


@login_required
def add_activity(request):

    activity_form = ActivityForm()

    if request.method == 'POST':
        activity_form = ActivityForm(request.POST)

        if activity_form.is_valid():
            activity_obj = activity_form.save(commit=False)
            activity_obj.save()

            if request.POST.get("savenewform"):
                return HttpResponseRedirect(reverse("activity:add_activity"))
            else:
                return HttpResponseRedirect(reverse('activity:list'))
        else:
            return render(request, 'activity/create_activity.html', {
                          'activity_form': activity_form})
    else:
        return render(request, 'activity/create_activity.html', {
                      'activity_form': activity_form})
