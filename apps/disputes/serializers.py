from rest_framework import serializers
from .models import Dispute, DisputeMessage
from apps.users.serializers import UserSerializer
from apps.orders.serializers import OrderSerializer

class DisputeMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DisputeMessage
        fields = ['id', 'dispute', 'sender', 'sender_name', 'message', 'created_at']
        read_only_fields = ['sender']
    
    def get_sender_name(self, obj):
        return obj.sender.username
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

class DisputeSerializer(serializers.ModelSerializer):
    complainant_name = serializers.SerializerMethodField()
    order_details = serializers.SerializerMethodField()
    messages = DisputeMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dispute
        fields = [
            'id', 'order', 'order_details', 'complainant', 'complainant_name', 
            'reason', 'status', 'created_at', 'updated_at', 'resolution',
            'resolved_by', 'resolved_at', 'messages'
        ]
        read_only_fields = ['complainant', 'resolved_by', 'resolved_at']
    
    def get_complainant_name(self, obj):
        return obj.complainant.username
    
    def get_order_details(self, obj):
        return {
            'id': obj.order.id,
            'total_price': str(obj.order.total_price),
            'status': obj.order.status,
            'created_at': obj.order.created_at
        }
    
    def create(self, validated_data):
        validated_data['complainant'] = self.context['request'].user
        return super().create(validated_data)
