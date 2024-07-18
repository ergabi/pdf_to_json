from django.shortcuts import render
from .forms import PDFUploadForm
from PyPDF2 import PdfReader
from transformers import pipeline
from django.http import JsonResponse, HttpResponse

# def upload_pdf(request):
#     if request.method == 'POST':
#         form = PDFUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             pdf_file = request.FILES['pdf_file']
#             reader = PdfReader(pdf_file)
#             text = ""
#             for page in reader.pages:
#                 text += page.extract_text()
#             questions_and_answers = generate_questions_and_answers(text)
#             return JsonResponse(questions_and_answers, safe=False)
#     else:
#         form = PDFUploadForm()
#     return render(request, 'upload_pdf.html', {'form': form})



# def generate_questions_and_answers(text):
#     # Split text into sentences
#     sentences = text.split('.')
    
#     # Load the question generation pipeline
#     qg_pipeline = pipeline("text2text-generation", model="valhalla/t5-base-qg-hl", tokenizer="t5-base")

#     questions_and_answers = []

#     for sentence in sentences:
#         if sentence.strip():  # Ignore empty sentences
#             # Generate question
#             question = qg_pipeline(f"generate question: {sentence.strip()}")[0]['generated_text']
#             questions_and_answers.append({
#                 "question": question,
#                 "answer": sentence.strip()
#             })
    
#     return questions_and_answers

extracted_text = ""

def upload_pdf(request):
    global extracted_text
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']
            reader = PdfReader(pdf_file)
            extracted_text = ""
            for page in reader.pages:
                extracted_text += page.extract_text()
            return HttpResponse("PDF uploaded and text extracted successfully.")            
    else:
        form = PDFUploadForm()
    return render(request, 'upload_pdf.html', {'form': form})

def ask_question(request):
    global extracted_text
    if request.method == 'POST':
        question = request.POST.get('question')
        if question and extracted_text:
            answer = generate_answer(extracted_text, question)
            return JsonResponse({"question": question, "answer": answer})
    return HttpResponse("Please upload a PDF and ask a question.")

def generate_answer(text, question,threshold=0.1):
    qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
    
    answer = qa_pipeline(question=question, context=text)
    if answer['score'] < threshold:
        return "Invalid question"
    return answer['answer']