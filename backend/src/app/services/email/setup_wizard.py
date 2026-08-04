"""
Email Setup Wizard - Simplified onboarding for non-tech users
"""
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class EmailProvider(str, Enum):
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    YAHOO = "yahoo"
    CUSTOM_SMTP = "custom_smtp"


class SetupStep(str, Enum):
    WELCOME = "welcome"
    CHOOSE_PROVIDER = "choose_provider"
    CONNECT_EMAIL = "connect_email"
    VERIFY_CONNECTION = "verify_connection"
    COMPLETE = "complete"


@dataclass
class ProviderInfo:
    """Information about an email provider"""
    id: EmailProvider
    name: str
    icon: str
    description: str
    setup_url: str
    instructions: List[str]
    requires_oauth: bool
    smtp_required: bool


class EmailSetupWizard:
    """
    Guided setup wizard for email connection.
    Makes it easy for non-tech users to connect their email.
    """
    
    PROVIDERS = {
        EmailProvider.GMAIL: ProviderInfo(
            id=EmailProvider.GMAIL,
            name="Gmail",
            icon="📧",
            description="Google Gmail account",
            setup_url="https://accounts.google.com/o/oauth2/v2/auth",
            instructions=[
                "Click 'Connect Gmail' button below",
                "Sign in with your Google account",
                "Allow Auto Apply AI to access your email",
                "That's it! We'll handle the rest."
            ],
            requires_oauth=True,
            smtp_required=False
        ),
        EmailProvider.OUTLOOK: ProviderInfo(
            id=EmailProvider.OUTLOOK,
            name="Outlook",
            icon="📨",
            description="Microsoft Outlook/Hotmail",
            setup_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            instructions=[
                "Click 'Connect Outlook' button below",
                "Sign in with your Microsoft account",
                "Grant permissions to Auto Apply AI",
                "Done! Your email is now connected."
            ],
            requires_oauth=True,
            smtp_required=False
        ),
        EmailProvider.YAHOO: ProviderInfo(
            id=EmailProvider.YAHOO,
            name="Yahoo Mail",
            icon="✉️",
            description="Yahoo email account",
            setup_url="https://api.login.yahoo.com/oauth2/request_auth",
            instructions=[
                "Click 'Connect Yahoo' button below",
                "Sign in with your Yahoo account",
                "Authorize Auto Apply AI",
                "All set! We'll start checking your emails."
            ],
            requires_oauth=True,
            smtp_required=False
        ),
        EmailProvider.CUSTOM_SMTP: ProviderInfo(
            id=EmailProvider.CUSTOM_SMTP,
            name="Custom SMTP",
            icon="⚙️",
            description="Any email provider with SMTP access",
            setup_url="",
            instructions=[
                "Enter your email address",
                "Enter your SMTP server details",
                "Enter your email password or app password",
                "Click 'Test Connection' to verify"
            ],
            requires_oauth=False,
            smtp_required=True
        )
    }
    
    def __init__(self):
        self.current_step = SetupStep.WELCOME
        self.selected_provider: Optional[EmailProvider] = None
        self.setup_data: Dict[str, any] = {}
    
    def get_welcome_message(self) -> Dict[str, any]:
        """Get welcome screen data"""
        return {
            "step": SetupStep.WELCOME,
            "title": "Welcome to Email Setup! 📧",
            "message": "Let's connect your email in 3 simple steps. This will allow us to:",
            "benefits": [
                "✨ Send job applications directly from your email",
                "📬 Auto-detect application responses",
                "🤖 Draft intelligent replies to recruiter emails",
                "📊 Track all your email interactions"
            ],
            "time_estimate": "2 minutes",
            "difficulty": "Easy"
        }
    
    def get_provider_selection(self) -> Dict[str, any]:
        """Get provider selection screen"""
        self.current_step = SetupStep.CHOOSE_PROVIDER
        
        providers_list = []
        for provider in EmailProvider:
            info = self.PROVIDERS[provider]
            providers_list.append({
                "id": provider.value,
                "name": info.name,
                "icon": info.icon,
                "description": info.description,
                "recommended": provider == EmailProvider.GMAIL,
                "difficulty": "Easy" if info.requires_oauth else "Medium"
            })
        
        return {
            "step": SetupStep.CHOOSE_PROVIDER,
            "title": "Choose Your Email Provider",
            "subtitle": "Select the email service you want to connect",
            "providers": providers_list,
            "recommended": EmailProvider.GMAIL.value
        }
    
    def select_provider(self, provider_id: str) -> Dict[str, any]:
        """Select a provider and return next step"""
        try:
            self.selected_provider = EmailProvider(provider_id)
            self.current_step = SetupStep.CONNECT_EMAIL
            return self.get_connection_screen()
        except ValueError:
            raise ValueError(f"Invalid provider: {provider_id}")
    
    def get_connection_screen(self) -> Dict[str, any]:
        """Get connection screen for selected provider"""
        if not self.selected_provider:
            raise ValueError("No provider selected")
        
        provider_info = self.PROVIDERS[self.selected_provider]
        
        return {
            "step": SetupStep.CONNECT_EMAIL,
            "provider": {
                "id": self.selected_provider.value,
                "name": provider_info.name,
                "icon": provider_info.icon,
                "description": provider_info.description
            },
            "instructions": provider_info.instructions,
            "requires_oauth": provider_info.requires_oauth,
            "oauth_url": provider_info.setup_url if provider_info.requires_oauth else None,
            "smtp_fields_required": provider_info.smtp_required
        }
    
    def get_verification_screen(self) -> Dict[str, any]:
        """Get verification screen"""
        self.current_step = SetupStep.VERIFY_CONNECTION
        
        return {
            "step": SetupStep.VERIFY_CONNECTION,
            "title": "Testing Connection...",
            "message": "Please wait while we verify your email connection.",
            "tips": [
                "Make sure you've completed the OAuth flow",
                "Check that you clicked 'Allow' on the permission screen",
                "This usually takes 10-15 seconds"
            ]
        }
    
    def get_completion_screen(self, success: bool, message: str, email_address: Optional[str] = None) -> Dict[str, any]:
        """Get completion screen"""
        self.current_step = SetupStep.COMPLETE
        
        return {
            "step": SetupStep.COMPLETE,
            "success": success,
            "title": "🎉 Email Connected Successfully!" if success else "❌ Connection Failed",
            "message": message,
            "email_address": email_address,
            "next_steps": [
                "Start searching for jobs",
                "Enable auto-apply",
                "Customize your email preferences"
            ] if success else [
                "Check your email credentials",
                "Try connecting again",
                "Contact support if problem persists"
            ]
        }
    
    def get_setup_summary(self) -> Dict[str, any]:
        """Get summary of current setup progress"""
        return {
            "current_step": self.current_step.value,
            "selected_provider": self.selected_provider.value if self.selected_provider else None,
            "progress": self._calculate_progress(),
            "can_proceed": self._can_proceed()
        }
    
    def _calculate_progress(self) -> int:
        """Calculate setup progress percentage"""
        progress_map = {
            SetupStep.WELCOME: 0,
            SetupStep.CHOOSE_PROVIDER: 25,
            SetupStep.CONNECT_EMAIL: 50,
            SetupStep.VERIFY_CONNECTION: 75,
            SetupStep.COMPLETE: 100
        }
        return progress_map.get(self.current_step, 0)
    
    def _can_proceed(self) -> bool:
        """Check if user can proceed to next step"""
        if self.current_step == SetupStep.CHOOSE_PROVIDER:
            return self.selected_provider is not None
        elif self.current_step == SetupStep.CONNECT_EMAIL:
            return self.selected_provider is not None
        return True
    
    def reset(self):
        """Reset wizard state"""
        self.current_step = SetupStep.WELCOME
        self.selected_provider = None
        self.setup_data = {}


# Global wizard instance
email_setup_wizard = EmailSetupWizard()