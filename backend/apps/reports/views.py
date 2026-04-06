"""
Reports Views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class ReportListView(APIView):
    """List all reports"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'message': 'Reports List API',
            'reports': []
        })


class GenerateReportView(APIView):
    """Generate a new report"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({
            'message': 'Report generation started',
            'status': 'pending'
        }, status=status.HTTP_202_ACCEPTED)


class DownloadReportView(APIView):
    """Download a report"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        return Response({
            'message': 'Report Download API',
            'report_id': str(report_id)
        })
