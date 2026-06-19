#!/usr/bin/env python3
"""
Engineer OOF Notification Agent
Monitors SharePoint roster for Out-of-Office status and sends Teams notifications
"""

import os
import json
import requests
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration for OOF notification agent"""
    
    SHAREPOINT_SITE = os.getenv(
        "SHAREPOINT_SITE",
        "https://microsoft.sharepoint.com/teams/WindowsAzureBuildout"
    )
    SHAREPOINT_LIBRARY = "Shared Documents"
    SHAREPOINT_FOLDER = "Shift Rosters"
    ROSTER_FILE = os.getenv("ROSTER_FILE", "Roster-2026.xlsx")
    
    TEAMS_WEBHOOK = os.getenv("TEAMS_WEBHOOK_URL", "")
    
    STATE_FILE = Path("oof-state.json")
    LOG_FILE = Path("logs/oof-notifications.log")
    
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))  # 5 minutes
    
    # Engineer tracking
    ENGINEERS = {
        "Chandan": {
            "email": "chandan@microsoft.com",
            "track": "RTEG"
        },
        "John Doe": {
            "email": "john.doe@microsoft.com",
            "track": "Pre-RTEG"
        }
    }

# ============================================================================
# LOGGING
# ============================================================================

def setup_logging() -> logging.Logger:
    """Setup logging to file and console"""
    Config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("OOFNotifier")
    logger.setLevel(logging.DEBUG)
    
    # File handler
    fh = logging.FileHandler(Config.LOG_FILE)
    fh.setLevel(logging.DEBUG)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

logger = setup_logging()

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

class StateManager:
    """Manage OOF state persistence"""
    
    @staticmethod
    def load_state() -> Dict:
        """Load previous OOF state from file"""
        if Config.STATE_FILE.exists():
            try:
                with open(Config.STATE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load state: {e}")
        return {}
    
    @staticmethod
    def save_state(state: Dict) -> None:
        """Save current OOF state to file"""
        try:
            with open(Config.STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    @staticmethod
    def detect_changes(current_state: Dict, previous_state: Dict) -> List[Dict]:
        """Detect status changes between current and previous state"""
        changes = []
        
        for name, status in current_state.items():
            prev_status = previous_state.get(name, "UNKNOWN")
            
            if status != prev_status:
                changes.append({
                    "name": name,
                    "previous": prev_status,
                    "current": status,
                    "changed": True
                })
        
        return changes

# ============================================================================
# ROSTER PARSING
# ============================================================================

class RosterParser:
    """Parse SharePoint roster data"""
    
    @staticmethod
    def get_mock_roster() -> Dict[str, str]:
        """Return mock roster data for testing (when file not available)"""
        logger.warning("Using mock roster data - install openpyxl for real data")
        
        # Mock data: engineer_name -> status (IN_OFFICE or OUT_OF_OFFICE)
        return {
            "Chandan": "OUT_OF_OFFICE",  # Tomorrow's leave in RTEG
            "John Doe": "IN_OFFICE",
            "Jane Smith": "IN_OFFICE",
        }
    
    @staticmethod
    def get_today_column_name() -> str:
        """Get tomorrow's day name (Mon, Tue, etc.)"""
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.strftime("%a")
    
    @staticmethod
    def parse_excel_roster(file_path: str) -> Dict[str, str]:
        """Parse Excel roster file"""
        try:
            import openpyxl
        except ImportError:
            logger.warning("openpyxl not installed - using mock data")
            return RosterParser.get_mock_roster()
        
        try:
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            
            roster = {}
            today = RosterParser.get_today_column_name()
            
            for row in ws.iter_rows(min_row=2, values_only=False):
                if not row[1].value:  # Skip if no engineer name
                    continue
                
                engineer_name = row[1].value
                
                # Find today's column
                for cell in row[2:]:
                    if today in (cell.value or ""):
                        status = "OUT_OF_OFFICE" if "OFF" in str(cell.value) or "Leave" in str(cell.value) else "IN_OFFICE"
                        roster[engineer_name] = status
                        break
                else:
                    roster[engineer_name] = "IN_OFFICE"
            
            return roster
            
        except Exception as e:
            logger.error(f"Failed to parse roster: {e}")
            return RosterParser.get_mock_roster()
    
    @staticmethod
    def fetch_roster() -> Dict[str, str]:
        """Fetch and parse roster from SharePoint"""
        logger.info("Fetching roster from SharePoint...")
        
        # For now, use mock data
        # In production, use PnP or SharePoint REST API to download Excel
        roster = RosterParser.get_mock_roster()
        
        logger.debug(f"Roster loaded: {roster}")
        return roster

# ============================================================================
# NOTIFICATIONS
# ============================================================================

class Notification:
    """Create and send notifications"""
    
    @staticmethod
    def create_adaptive_card(
        engineer_name: str,
        track: str,
        status: str,
        email: str
    ) -> Dict:
        """Create Teams Adaptive Card"""
        
        status_emoji = "🔴" if status == "OUT_OF_OFFICE" else "🟢"
        status_text = status.replace("_", " ")
        style = "attention" if status == "OUT_OF_OFFICE" else "good"
        
        return {
            "type": "AdaptiveCard",
            "version": "1.4",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "body": [
                {
                    "type": "Container",
                    "style": style,
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"{status_emoji} {engineer_name}",
                            "weight": "bolder",
                            "size": "extraLarge",
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": status_text,
                            "size": "large",
                            "weight": "bolder",
                            "wrap": True,
                            "spacing": "small"
                        }
                    ]
                },
                {
                    "type": "Container",
                    "separator": True,
                    "spacing": "medium",
                    "items": [
                        {
                            "type": "FactSet",
                            "facts": [
                                {
                                    "name": "Engineer:",
                                    "value": engineer_name
                                },
                                {
                                    "name": "Track:",
                                    "value": track
                                },
                                {
                                    "name": "Status:",
                                    "value": status_text
                                },
                                {
                                    "name": "Email:",
                                    "value": email
                                },
                                {
                                    "name": "Notified:",
                                    "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Contact team lead if urgent assistance is needed.",
                            "size": "small",
                            "isSubtle": True,
                            "wrap": True
                        }
                    ]
                }
            ],
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": f"Email {engineer_name.split()[0]}",
                    "url": f"mailto:{email}"
                }
            ]
        }
    
    @staticmethod
    def create_teams_message(
        engineer_name: str,
        track: str,
        status: str,
        email: str
    ) -> Dict:
        """Create Teams message with Adaptive Card"""
        
        status_text = status.replace("_", " ")
        
        return {
            "body": [
                {
                    "contentType": "text",
                    "content": f"{engineer_name} - {status_text} (Track: {track})"
                }
            ],
            "attachments": [
                {
                    "id": "adaptiveCard1",
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": Notification.create_adaptive_card(
                        engineer_name, track, status, email
                    )
                }
            ]
        }
    
    @staticmethod
    def send_teams_notification(
        engineer_name: str,
        track: str,
        status: str,
        email: str,
        webhook_url: Optional[str] = None,
        dry_run: bool = False
    ) -> bool:
        """Send notification to Teams via webhook"""
        
        if not webhook_url or webhook_url.startswith("https://outlook.webhook"):
            logger.warning("Teams webhook not configured - skipping Teams notification")
            return False
        
        status_text = status.replace("_", " ")
        
        logger.info(f"Preparing Teams notification for {engineer_name} ({status_text})")
        
        # Create message
        message = Notification.create_teams_message(
            engineer_name, track, status, email
        )
        
        if dry_run:
            logger.info(f"[DRY RUN] Would send Teams notification: {json.dumps(message, indent=2)}")
            return True
        
        try:
            response = requests.post(
                webhook_url,
                json=message,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"✓ Teams notification sent for {engineer_name}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Teams notification: {e}")
            return False

# ============================================================================
# MAIN AGENT
# ============================================================================

class OOFNotificationAgent:
    """Main OOF notification agent"""
    
    def __init__(self, dry_run: bool = False, continuous: bool = False):
        self.dry_run = dry_run
        self.continuous = continuous
        self.run_count = 0
    
    def run(self) -> None:
        """Run the OOF notification agent"""
        
        logger.info("=" * 70)
        logger.info("Engineer OOF Notification Agent Started")
        logger.info("=" * 70)
        
        if self.dry_run:
            logger.warning("Running in DRY RUN mode - notifications will not be sent")
        
        try:
            while True:
                self.run_count += 1
                self._check_status()
                
                if not self.continuous:
                    break
                
                logger.info(f"Next check in {Config.CHECK_INTERVAL} seconds...")
                time.sleep(Config.CHECK_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("Agent stopped by user")
        finally:
            logger.info("Engineer OOF Notification Agent Stopped")
    
    def _check_status(self) -> None:
        """Check OOF status and send notifications"""
        
        logger.info(f"\n{'=' * 70}")
        logger.info(f"Check #{self.run_count} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'=' * 70}")
        
        # Fetch roster
        current_roster = RosterParser.fetch_roster()
        
        # Convert to current state format
        current_state = {
            name: status
            for name, status in current_roster.items()
        }
        
        # Load previous state
        previous_state = StateManager.load_state()
        
        # Detect changes
        changes = StateManager.detect_changes(current_state, previous_state)
        
        # Process changes
        for change in changes:
            engineer_name = change["name"]
            status = change["current"]
            
            logger.info(
                f"Status change: {engineer_name}: {change['previous']} → {status}"
            )
            
            # Get engineer details
            engineer_info = Config.ENGINEERS.get(
                engineer_name,
                {
                    "email": f"{engineer_name.lower().replace(' ', '.')}@microsoft.com",
                    "track": "Unknown"
                }
            )
            
            # Send notification
            Notification.send_teams_notification(
                engineer_name=engineer_name,
                track=engineer_info["track"],
                status=status,
                email=engineer_info["email"],
                webhook_url=Config.TEAMS_WEBHOOK,
                dry_run=self.dry_run
            )
        
        # Save current state
        StateManager.save_state(current_state)
        
        # Summary
        logger.info(
            f"Summary: {len(current_roster)} engineers monitored, "
            f"{len(changes)} status changes detected"
        )

# ============================================================================
# CLI
# ============================================================================

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="Engineer OOF Notification Agent"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show notifications without sending"
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run continuously with periodic checks"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Check interval in seconds (default: 300)"
    )
    parser.add_argument(
        "--roster",
        type=str,
        default="Roster-2026.xlsx",
        help="Roster file name"
    )
    parser.add_argument(
        "--webhook",
        type=str,
        help="Teams webhook URL"
    )
    
    args = parser.parse_args()
    
    # Update config from arguments
    if args.interval:
        Config.CHECK_INTERVAL = args.interval
    if args.roster:
        Config.ROSTER_FILE = args.roster
    if args.webhook:
        Config.TEAMS_WEBHOOK = args.webhook
    
    # Create and run agent
    agent = OOFNotificationAgent(
        dry_run=args.dry_run,
        continuous=args.continuous
    )
    
    agent.run()

if __name__ == "__main__":
    main()
