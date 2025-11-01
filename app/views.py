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
import docx2txt
import easyocr




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
            salary_slips = request.FILES.getlist('salary_slip')
            bank_statements = request.FILES.getlist('bank_statement')

            if not salary_slips and not bank_statements:
                return Response({
                    "status": 0,
                    "error": "Please upload at least one file (salary_slip or bank_statement)."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Collect text from all uploaded files
            salary_texts, bank_texts = [], []
            salary_names, bank_names = [], []

            if salary_slips:
                for file in salary_slips:
                    salary_names.append(file.name)
                    salary_texts.append(self.extract_text(file))

            if bank_statements:
                for file in bank_statements:
                    bank_names.append(file.name)
                    bank_texts.append(self.extract_text(file))

            # Combine all texts
            combined_text = f"SALARY SLIPS:\n{''.join(salary_texts)}\n\nBANK STATEMENTS:\n{''.join(bank_texts)}"

            # Send combined data to Gemini
            result = verify_document_text("salary_slip and bank_statement", combined_text)

            verification_result = {
                "salary_slip": salary_names,
                "bank_statement": bank_names,
                "salary_slip_status": result.get("salary_slip_status", "Unknown"),
                "bank_statement_status": result.get("bank_statement_status", "Unknown"),
                "matched": result.get("matched", "Unknown"),
                "explanation": result.get("explanation", "No explanation provided.")
            }

            return Response({
                "status": 1,
                "message": "Verification completed successfully.",
                "verification_result": verification_result
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": 0,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def extract_text(self, file_obj):
        import numpy as np, cv2, io, docx2txt
        from PyPDF2 import PdfReader
        import easyocr

        file_name = file_obj.name.lower()
        file_bytes = file_obj.read()
        file_obj.seek(0)
        file_stream = io.BytesIO(file_bytes)

        if file_name.endswith('.pdf'):
            reader = PdfReader(file_stream)
            text = "".join([page.extract_text() or "" for page in reader.pages])
            return text.strip()

        elif file_name.endswith('.docx'):
            return docx2txt.process(file_stream).strip()

        elif file_name.endswith(('.png', '.jpg', '.jpeg')):
            image_array = np.frombuffer(file_bytes, np.uint8)
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            reader = easyocr.Reader(['en'], gpu=False)
            text_blocks = reader.readtext(img, detail=0)
            return "\n".join(text_blocks).strip()

        return file_bytes.decode('utf-8', errors='ignore').strip()
