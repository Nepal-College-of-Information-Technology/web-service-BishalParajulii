from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Message


def chatPage(request, *args, **kwargs):
    return render(request, "app/chatPage.htm")


from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render , get_object_or_404
import base64
from django.core.files.base import ContentFile

User = get_user_model()

@login_required
def users_list(request):
    users = User.objects.exclude(username=request.user.username)
    return render(request, 'app/index.htm', {'users': users})





@login_required
def private_chat_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    return render(request, 'app/private_chat.htm', {
        'other_user': other_user,       # ✅ Pass other_user to template
        'sender_id': request.user.id,   # ✅ Pass sender_id to template
        'sender': request.user.username, # ✅ Pass sender username
        'receiver': other_user,         # ✅ Pass receiver user for easy access in JS
        'request': request,             # ✅ Optional: if you're using {{ request.user.username }} in JS
    })
   


def user_list(request):
    current_user = request.user
    users = User.objects.exclude(id=current_user.id)
    user_data = [{"username": user.username, "id": user.id} for user in users]
    
    return JsonResponse(user_data, safe=False)



# @login_required
# # @csrf_exempt
# def upload_chat_file(request, user_id):
#     if request.method == 'POST':
#         receiver = get_object_or_404(User, id=user_id)
#         message_text = request.POST.get('message', '')
#         uploaded_file = request.FILES.get('file', None)

#         Message.objects.create(
#             sender=request.user,
#             receiver=receiver,
#             message=message_text,
#             file=uploaded_file
#         )
#         return JsonResponse({'status': 'success'})

#     return JsonResponse({'error': 'Invalid request'}, status=400)
