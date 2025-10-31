from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import TeamData
from rest_framework import status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_riddle(request):
    """
    Retrieves the assigned riddle for the authenticated team.
    """
    try:
        # request.user is the authenticated team (User object)
        team_data = TeamData.objects.get(team=request.user)
        
        # Check if they already completed the challenge
        if team_data.is_complete:
            return Response(
                {"detail": "Mission already complete!", "is_complete": True},
                status=status.HTTP_200_OK
            )
            
        riddle = team_data.assigned_riddle
        return Response({
            "riddle_text": riddle.riddle_text,
            "is_complete": False
        })
    except TeamData.DoesNotExist:
        return Response(
            {"detail": "No game data found for this team. Contact an admin."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request):
    """
    Submits a final answer for the authenticated team.
    """
    try:
        final_answer_submission = request.data.get('answer', '').strip().upper()
        if not final_answer_submission:
            return Response(
                {"detail": "No answer provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        team_data = TeamData.objects.get(team=request.user)
        
        # Check if they are already done
        if team_data.is_complete:
            return Response(
                {"detail": "Mission already complete!", "is_complete": True},
                status=status.HTTP_200_OK
            )
        
        # Check if the answer is correct (case-insensitive, whitespace-stripped)
        correct_answer = team_data.final_answer.strip().upper()
        
        if final_answer_submission == correct_answer:
            # Mark as complete and save
            team_data.is_complete = True
            team_data.save()
            return Response(
                {"detail": "Correct! Mission Complete!", "is_complete": True},
                status=status.HTTP_200_OK
            )
        else:
            # Incorrect answer
            return Response(
                {"detail": "Incorrect answer. Try again."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except TeamData.DoesNotExist:
        return Response(
            {"detail": "No game data found for this team. Contact an admin."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
