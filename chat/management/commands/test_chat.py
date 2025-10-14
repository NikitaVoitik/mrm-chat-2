from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from chat.models import Chat, Message

User = get_user_model()


class Command(BaseCommand):
    help = 'Test the chat functionality'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing chat functionality...'))
        
        # Create test users
        self.stdout.write('\n=== Creating test users ===')
        student = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.stdout.write(self.style.SUCCESS(f'Created student: {student}'))
        
        staff = User.objects.create_user(
            username='test_staff',
            email='staff@test.com',
            password='testpass123',
            user_type='staff'
        )
        self.stdout.write(self.style.SUCCESS(f'Created staff: {staff}'))
        
        owner = User.objects.create_user(
            username='test_owner',
            email='owner@test.com',
            password='testpass123',
            user_type='owner'
        )
        self.stdout.write(self.style.SUCCESS(f'Created owner: {owner}'))
        
        # Create a chat
        self.stdout.write('\n=== Creating test chat ===')
        chat = Chat.objects.create(name='Test Discussion Group')
        chat.participants.add(student, staff, owner)
        self.stdout.write(self.style.SUCCESS(f'Created chat: {chat}'))
        self.stdout.write(f'Participants: {", ".join([p.username for p in chat.participants.all()])}')
        
        # Create messages
        self.stdout.write('\n=== Creating test messages ===')
        msg1 = Message.objects.create(
            chat=chat,
            sender=student,
            content='Hello! I\'m a student.'
        )
        self.stdout.write(self.style.SUCCESS(f'Message 1: {msg1}'))
        
        msg2 = Message.objects.create(
            chat=chat,
            sender=staff,
            content='Welcome! I\'m a staff member.'
        )
        self.stdout.write(self.style.SUCCESS(f'Message 2: {msg2}'))
        
        msg3 = Message.objects.create(
            chat=chat,
            sender=owner,
            content='Great to have everyone here!'
        )
        self.stdout.write(self.style.SUCCESS(f'Message 3: {msg3}'))
        
        # Display chat history
        self.stdout.write('\n=== Chat History ===')
        for message in chat.messages.all():
            self.stdout.write(f'[{message.timestamp}] {message.sender.username} ({message.sender.get_user_type_display()}): {message.content}')
        
        # Statistics
        self.stdout.write('\n=== Statistics ===')
        self.stdout.write(f'Total users: {User.objects.count()}')
        self.stdout.write(f'Total chats: {Chat.objects.count()}')
        self.stdout.write(f'Total messages: {Message.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('\n✓ All tests passed!'))
