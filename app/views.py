from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.
# views.py
import io
from PyPDF2 import PdfReader
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.doc_verify import verify_document_text




class SigninView(APIView):
    USERNAME='demouser'
    PASSWORD='password12@'
    def post(self,request):
        username=request.data.get('username')
        password=request.data.get('password')
        if username == self.USERNAME and password == self.PASSWORD:
            return Response({'message':'login successfully'},status=200)
        return Response({'error':'invalid username or password'})
    
class VerifyDocumentsView(APIView):
    def post(self, request):
        try:
            salary_slip = request.FILES.get('salary_slip')
            bank_statement = request.FILES.get('bank_statement')

            if not salary_slip and not bank_statement:
                return Response({
                    "status": 0,
                    "error": "Please upload at least one file (salary_slip or bank_statement)."
                }, status=status.HTTP_400_BAD_REQUEST)

            verification_result = {}

            # Salary Slip
            if salary_slip:
                text = self.extract_text(salary_slip)
                verification_result['salary_slip'] = verify_document_text("Salary Slip", text)

            # Bank Statement
            if bank_statement:
                text = self.extract_text(bank_statement)
                verification_result['bank_statement'] = verify_document_text("Bank Statement", text)  

            return Response({
                "status": 1,
                "message": "Document verification completed successfully.",
                "verification_result": verification_result
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": 0,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def extract_text(self, file_obj):
        if file_obj.name.lower().endswith('.pdf'):
            reader = PdfReader(io.BytesIO(file_obj.read()))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        else:
            return file_obj.read().decode('utf-8', errors='ignore')
