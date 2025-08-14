from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from rest_framework import status
from .models import File
from django.views.decorators.csrf import csrf_exempt
import json
import os
import uuid
import base64
from io import BytesIO
import requests
import threading
@csrf_exempt
def file_upload_view(request):
    if request.method == 'POST':
        
        try:
            data = json.loads(request.body)
            
            file_data = data.get('file_data') 
            file_url = data.get('url')
            file_name=data.get('file_name','')
            if data.get('media_type')=='image':
                
                extension='.jpg'
            elif data.get('media_type')=='video':
                extension='.mp4'
            file_type=extension
            if not file_data and not file_url:
                return JsonResponse({'error': 'Either file content or URL must be provided'}, 
                                    status=status.HTTP_400_BAD_REQUEST)

            # Define local bucket path
            bucket_name = data.get('bucket_name')
           
            bucket_path = os.path.join('media', bucket_name)
            
            

            # Generate unique filename
            unique_filename = f'{uuid.uuid4()}' 
        
            unique_filename += extension
            filepath=f'{bucket_path}/{unique_filename}' 
            thread=threading.Thread(target=file_creation_thread,args=(file_data,file_url,bucket_path,filepath,file_name,file_type))
            thread.start()
            print(filepath)
            return JsonResponse({'file_path': filepath}, status=status.HTTP_200_OK)


        except (json.JSONDecodeError, ValidationError) as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
# Create your views here.


def file_creation_thread(file_data,file_url,bucket_path,file_path,file_name,file_type):
    import os
    if not os.path.isdir(bucket_path):
        os.makedirs(bucket_path)
    if file_data:
                # Handle file upload from request data (base64 encoded)
       
        with open(file_path, 'wb+') as destination:
            destination.write(base64.b64decode(file_data)) 

    elif file_url:
        # Handle file upload from URL
        try:
            response = requests.get(file_url)
            response.raise_for_status() 
            
            with open(file_path, 'wb+') as f:
                f.write(response.content)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f'Failed to download file from URL: {e}'}, 
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Create File object in database
    file_obj = File.objects.create(
        
        file_path=file_path,
        file_name=file_name,
        file_type=file_type,
        file_size=os.path.getsize(file_path)
        
    )
    file_obj.save()
