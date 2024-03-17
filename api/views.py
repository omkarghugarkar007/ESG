import json
from uploader.models import Document, Questionaire
from uploader.utils import getAnswer, addNewPdf
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import datetime
import os

# Create your views here.
@csrf_exempt
def uploadFile(request):
    if request.method == 'POST' and request.FILES:
        uploaded_file = request.FILES['document']
        reportYear = request.POST['reportYear']
        # Check if the file extension is allowed
        allowed_extensions = ['pdf', 'doc', 'docx']
        file_extension = uploaded_file.name.split('.')[-1]

        if file_extension not in allowed_extensions:
            return JsonResponse({'error': 'Only .pdf or .doc files are allowed'}, status=400)
        
        # Checking if file exceeds threshold
        max_size = 5 * 1024 * 1024  # 5MB (adjust size as needed)
        if uploaded_file.size > max_size:
            return JsonResponse({'error': 'File size exceeds the limit of 5MB'}, status=400)

        new_file = Document(document=uploaded_file, reportYear=reportYear)
        new_file.save()
        return JsonResponse({
            'status': 'Success',
            'message': 'File uploaded successfully',
            'trackerId': new_file.document.name.split('/')[1]
        }, status=201)
    else:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

def transform_response(response):
    document_references = [citation[1] for citation in response["citations"]]
    transformed_response = {
        "reportYear": response["reportYear"],  # Assuming "2024" is a fixed value for reportYear
        "questionnaireSummary": {
            "response": response["paragraph"],
            "status": "success",
            "citation": response["citations"],
            "documentReference": ", ".join(document_references),
            "accuracy": response["accuracy"],  # Assuming "0.8" is a fixed value for accuracy
            "confidenceScores": response["confidenceScores"]  # Assuming "0.8" is a fixed value for confidenceScores
        }
    }
    return transformed_response

@csrf_exempt
def getSpecificQuestionResponse(request):
    if request.method == 'POST':
        print(request.POST)
        if 'inputQuestion' not in request.POST or request.POST['inputQuestion'] == "":
            return JsonResponse({'error': 'Add a question in request body'}, status=400)
        
        response = getAnswer(request.POST['inputQuestion'], [], request.POST['reportYear'])
        final_response = transform_response(response)
        return JsonResponse(final_response, status=200)
    else:
        return JsonResponse({'error': 'Something went wrong. Please try again.'}, status=400)

@csrf_exempt
def getDocs(request):
    if request.method == 'POST':
        response = []
        reportYear = request.POST['reportYear']
        docs = Document.objects.filter(reportYear=reportYear)
        for doc in docs:
            response.append({
                'documentName': doc.document.name.split('/')[1],
                'metadata': {
                    'documentType': 'PDF',
                    'refernceLink': doc.document.url,
                    'reportYear': reportYear
                }
            })
        return JsonResponse(response, safe=False, status=200)
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({'error': 'Only GET method is allowed.'}, status=405)

@csrf_exempt
def getReportStatus(request, reportYear, taskId):
    if request.method == 'GET':
        docs = Document.objects.filter(reportYear=reportYear)
        isPresent = any(doc.document.name.split('/')[1] == taskId for doc in docs)
        status = 'success' if isPresent else 'fail'
        response = {
            'taskId': taskId,
            'status': status,
            'createAt': datetime.datetime.now()
        }
        return JsonResponse(response, safe=False, status=200)
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({'error': 'Only GET method is allowed.'}, status=405)

@csrf_exempt
def uploadQuestionnaire(request):
    if request.method == 'POST' and request.FILES:
        uploaded_file = request.FILES['SurveyQuestionnaireDocumentName']
        metatdata = json.loads(request.POST['metadata'])
        # Check if the file extension is allowed
        allowed_extensions = ['pdf', 'doc', 'docx']
        file_extension = uploaded_file.name.split('.')[-1]

        if file_extension not in allowed_extensions:
            return JsonResponse({'error': 'Only .pdf or .doc files are allowed'}, status=400)
        
        # Checking if file exceeds threshold
        max_size = 5 * 1024 * 1024  # 5MB (adjust size as needed)
        if uploaded_file.size > max_size:
            return JsonResponse({'error': 'File size exceeds the limit of 5MB'}, status=400)

        new_file = Questionaire(questionaire=uploaded_file, reportYear=metatdata['generateReportforYear'], response='[]')
        new_file.save()
        response_list = addNewPdf(new_file.questionaire.url)
        new_file.response = json.dumps(response_list)
        new_file.save()
        return JsonResponse({
            'taskId': new_file.questionaire.name.split('/')[1],
            'status': 'success',
            'createAt': datetime.datetime.now()
        }, status=200)
    else:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

@csrf_exempt
def getReport(request, reportYear):
    if request.method == 'GET':
        documents = []
        report_dir = os.path.join(os.getcwd(), 'media\\reports')
        reports = [f for f in os.listdir(report_dir)]
        for report in reports:
            if report.startswith(reportYear):
                documents.append({
                    'documentName': report,
                    'metadata': {
                        'documentType': 'PDF',
                        'refernceLink': os.path.join(report_dir, report),
                        'reportYear': reportYear
                    }
                })
        if len(documents):
            response = {"documents": documents, "message": "Reports fetched successfully"}
        else:
            response = {"documents": documents, "message": f"No reports forund for {reportYear}. Save your reports at chatESG."}
        
        return JsonResponse(response, safe=False, status=200)
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({'error': 'Only GET method is allowed.'}, status=405)