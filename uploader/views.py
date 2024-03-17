from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.template.loader import render_to_string, get_template
from .models import Document, ChatHistory, Questionaire
from .utils import *
import json, time
from xhtml2pdf import pisa
from io import BytesIO
import asyncio
import os

# Create your views here.
def homeView(request):
    allChatHistories = ChatHistory.objects.all()
    context = {
        'success': True,
        'error': '',
        'error_message': '',
        'allChatHistories': allChatHistories
    }
    if request.method == 'POST':
        if 'question' not in request.POST or request.POST['question'] == "":
            context['success'] = False
            context['error'] = 'Invalid question'
            context['error_message'] = 'Invalid queston. Please refresh and try again.'
            return render(request, "index.html", context)
        else:
            # Saving new chat to history
            question = request.POST['question']
            inputData = {}
            inputData["current_question"] = question
            inputData["history"] = []
            response = getAnswer(inputData)
            response = [response]
            response = json.dumps(response)
            history = ChatHistory(
                response=response, 
                name='Chat ' + str(len(allChatHistories) + 1)
            )
            history.save()
            #time.sleep(4)
            return redirect('chatView', pk=history.pk)

    return render(request, "index.html", context)

def deleteView(request):
    print('In delete view')
    allChatHistories = ChatHistory.objects.all()
    if request.method == 'POST':
        allChatHistories.delete()
    context = {
        'success': True,
        'error': '',
        'error_message': '',
        'allChatHistories': allChatHistories
    }
    return render(request, "index.html", context)

def uploadView(request):
    allChatHistories = ChatHistory.objects.all()
    context = {
        'success': True,
        'error': '',
        'error_message': '',
        'allChatHistories': allChatHistories
    }
    if request.method == "POST":
        doc = Document(document=request.FILES.get('file'),reportYear = request.POST.get('reportYear'))
        doc.save()
        path = os.path.join("media/docs", str(request.FILES['file']))
        print(path)
        isAdded = addNewPdf(path)
        context = {'isAdded': isAdded}
    return render(request, "upload.html", context)

new_pk = ''
def uploadQuestionaireView(request):
    allChatHistories = ChatHistory.objects.all()
    context = {
        'success': True,
        'error': '',
        'error_message': '',
        'allChatHistories': allChatHistories
    }
    if request.method == "POST":
        questionaire = request.FILES.get('file')
        reportYear = request.POST.get('reportYear')
        path = os.path.join("media/questionaires/", str(request.FILES['file']))
        print(path)
        new_file = Questionaire(questionaire=questionaire, response='[]', reportYear = reportYear)
        new_file.save()
        response_list = addQuestionPDF(path)
        new_file.response = json.dumps(response_list)
        new_file.save()
        context['response'] = response_list
        global new_pk
        new_pk = new_file.pk

    if new_pk:
        return redirect('reportView', pk=new_pk)
    else:
        return render(request, "upload-questionaire.html", context)

def reportView(request, pk):
    allChatHistories = ChatHistory.objects.all()
    print(pk)
    questionaire = Questionaire.objects.get(pk=pk)
    response = json.loads(questionaire.response)
    print(response)
    context = {
        'success': True,
        'error': '',
        'error_message': '',
        'allChatHistories': allChatHistories,
        'response': response
    }

    # report_html = render_to_string("report.html", context)
    template = get_template("report.html")
    report_html = template.render(context)
    output_path = str(settings.BASE_DIR) + f"/media/reports/output.pdf"
    pdf_response = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(report_html.encode('UTF-8')), pdf_response)

    try:
        with open(output_path, 'wb+') as output:
            pdf = pisa.pisaDocument(BytesIO(report_html.encode('UTF-8')), output)
    except Exception as e:
        print(e)

    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'filename="products_report.pdf"'

    # # create a pdf
    # pisa_status = pisa.CreatePDF(report_html, dest=response)
    # # if error then show some funy view
    # if pisa_status.err:
    #    return HttpResponse('We had some errors <pre>' + report_html + '</pre>')
    # return response

    return render(request, "report.html", context)

def chatView(request, pk):
    allChatHistories = ChatHistory.objects.all()
    history = ChatHistory.objects.get(pk=pk)
    name = history.name
    response = json.loads(history.response)

    inputHistory = []
    for hist in response:
        inputHistory.append((HumanMessage(content=hist["question"]), AIMessage(content=hist["paragraph"])))

    context = {
        'success': True,
        'error': '',
        'error_message': '',
        'allChatHistories': allChatHistories,
        'is_report': False,
        'name': name,
        'response': response
    }

    if request.method == 'POST':
        if 'question' not in request.POST or request.POST['question'] == "":
            context['success'] = False
            context['error'] = 'Invalid question'
            context['error_message'] = 'Invalid queston. Please refresh and try again.'
            return render(request, "index.html", context)
        else:
            # Parsing qas
            question = request.POST['question']
            inputData = {}
            inputData["current_question"] = question
            inputData["history"] = inputHistory
            answer = getAnswer(inputData)
            response.append(answer)

            # Updating qas context
            context['response'] = response

            # Updating chat history
            history.response = json.dumps(response)
            history.save()

            #time.sleep(4)

            context['allChatHistories'] = ChatHistory.objects.all()

    return render(request, "chat.html", context)