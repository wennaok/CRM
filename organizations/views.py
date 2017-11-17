from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from organizations.models import Organization
from common.models import User, Address, Comment
from common.utils import LEAD_STATUS, LEAD_SOURCE
from oppurtunity.models import Opportunity, STAGES, SOURCES
from contacts.models import Contact
from organizations.forms import OrganizationForm#OrganizationCommentForm
from common.forms import BillingAddressForm

# Create your views here.


@login_required
def organizations_list(request):
    org_obj = Organization.objects.all()
    page = request.POST.get('per_page')
    name = request.POST.get('name')
    city = request.POST.get('city')
    email = request.POST.get('email')

    if name:
        org_obj = Organization.objects.filter(name__icontains=name)
    if city:
        org_obj = Organization.objects.filter(address=Address.objects.filter
                                       (city__icontains=city))
    if email:
        org_obj = Organization.objects.filter(email__icontains=email)

    return render(request, 'organizations/organizations.html', {
        'org_obj': org_obj, 'per_page': page
    })


@login_required
def add_org(request):
    users = User.objects.filter(is_active=True).order_by('email')
    organization_form = OrganizationForm(assigned_to=users)
    address_form = BillingAddressForm()
    assignedto_list = request.POST.getlist('assigned_to')
    if request.method == 'POST':
        organization_form = OrganizationForm(request.POST, assigned_to=users)
        address_form = BillingAddressForm(request.POST)
        if address_form.is_valid():
            org_obj = organization_form.save(commit=False)
            address_object = address_form.save()
            org_obj.address = address_object
            org_obj.created_by = request.user
            org_obj.save()
            org_obj.assigned_to.add(*assignedto_list)
            if request.POST.get("savenewform"):
                return HttpResponseRedirect(reverse("organizations:new_organization"))
            else:
                return HttpResponseRedirect(reverse('organizations:list'))
        else:
            return render(request, 'organizations/create_org.html', {
                          'org_form': organization_form, 'address_form': address_form,
                          'users': users,
                          'status': LEAD_STATUS, 'source': LEAD_SOURCE,
                          'assignedto_list': assignedto_list})
    else:
        return render(request, 'organizations/create_org.html', {
                      'org_form': organization_form, 'address_form': address_form,
                      'users': users, 'status': LEAD_STATUS, 'source': LEAD_SOURCE})


@login_required
def view_organization(request, pk):
    organization_record = get_object_or_404(Organization, id=pk)
    comments = organization_record.organization_comments.all()
    return render(request, 'organizations/view_organization.html', {
        'organization_record': organization_record,
        'comments': comments
    })


@login_required
def edit_organization(request, pk):
    organization_obj = get_object_or_404(Organization, id=pk)
    users = User.objects.filter(is_active=True).order_by('email')
    form = OrganizationForm(
        instance=organization_obj, assigned_to=users)
    assignedto_list = request.POST.getlist("assigned_to")
    if request.method == 'POST':
        form = OrganizationForm(
            request.POST, instance=organization_obj, assigned_to=users)
        if form.is_valid():
            organization_obj = form.save(commit=False)
            organization_obj.created_by = request.user
            if request.POST.get('stage') in ['CLOSED WON', 'CLOSED LOST']:
                organization_obj.closed_by = request.user
            organization_obj.save()
            organization_obj.assigned_to.clear()
            organization_obj.assigned_to.add(*assignedto_list)
            if request.is_ajax():
                return JsonResponse({'error': False})
            return HttpResponseRedirect(reverse('organizations:list'))
        else:
            if request.is_ajax():
                return JsonResponse({'error': True, 'organization_errors': form.errors})
            return render(request, 'organizations/create_org.html', {
                'organization_form': form,
                'organization_obj': organization_obj,
                'users': users,
                'assignedto_list': assignedto_list,

            })
    else:
        return render(request, 'organizations/create_org.html', {
            'organization_form': form,
            'organization_obj': organization_obj,
            'users': users,
            'assignedto_list': assignedto_list,
        })


@login_required
def remove_organization(request, pk):
    organization_record = get_object_or_404(Organization, id=pk)
    organization_record.delete()
    if request.is_ajax():
        return JsonResponse({'error': False})
    return HttpResponseRedirect(reverse('organization:list'))

# CRUD Operations Ends
# Comments Section Starts


#@login_required
#def add_comment(request):
    #if request.method == 'POST':
        #organization = get_object_or_404(Organization, id=request.POST.get('organizationid'))
        #if request.user in organization.assigned_to.all() or request.user == organization.created_by:
            #form = OrganizationCommentForm(request.POST)
            #if form.is_valid():
                #organization_comment = form.save(commit=False)
                #organization_comment.comment = request.POST.get('comment')
                #organization_comment.commented_by = request.user
                #organization_comment.organization = organization
                #organization_comment.save()
                #data = {"comment_id": organization_comment.id,
                        #"comment": organization_comment.comment,
                        #"commented_on": organization_comment.commented_on,
                        #"commented_by": organization_comment.commented_by.email}
                #return JsonResponse(data)
            #else:
                #return JsonResponse({"error": form['comment'].errors})
        #else:
            #data = {'error': "You Dont Have permissions to Comment"}
            #return JsonResponse(data)


#@login_required
#def edit_comment(request):
    #if request.method == "POST":
        #comment = request.POST.get('comment')
        #comment_id = request.POST.get("commentid")
        #com = get_object_or_404(Comment, id=comment_id)
        #form = OrganizationCommentForm(request.POST)
        #if request.user == com.commented_by:
            #if form.is_valid():
                #com.comment = comment
                #com.save()
                #data = {"comment": com.comment, "commentid": comment_id}
                #return JsonResponse(data)
            #else:
                #return JsonResponse({"error": form['comment'].errors})
        #else:
            #return JsonResponse({"error": "You dont have authentication to edit"})
    #else:
        #return render(request, "404.html")


#@login_required
#def remove_comment(request):
    #if request.method == 'POST':
        #comment_id = request.POST.get('comment_id')
        #comment = get_object_or_404(Comment, id=comment_id)
        #if request.user == comment.commented_by:
            #comment.delete()
            #data = {"cid": comment_id}
            #return JsonResponse(data)
        #else:
            #return JsonResponse({"error": "You Dont have permisions to delete"})
    #else:
        #return HttpResponse("Something Went Wrong")

# Other Views


@login_required
def get_organization(request):
    if request.method == 'GET':
        organizations = Organization.objects.all()
        return render(request, 'organizations/organizations_list.html', {'organization': organizations})
    else:
        return HttpResponse('Invalid Method or Not Authanticated in load_calls')
