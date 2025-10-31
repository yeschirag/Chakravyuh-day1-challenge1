import csv
import secrets
import string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Riddle, TeamData
from django.db import transaction
import openpyxl  # <-- 1. Import the new library

# --- CONFIGURATION ---
# The master file you just uploaded.
# Place this file in the main project folder (with manage.py)
MASTER_DATA_FILE = 'Day1_InfinityCodes_Teams_100_Final.xlsx' # <-- 2. Updated filename
SHEET_NAME = 'Teams_Data' # <-- 3. Assumed sheet name

# This is the NEW file the script will create.
# It will contain all the generated passwords for you.
OUTPUT_CREDENTIALS_FILE = 'teams_credentials_FOR_ORGANIZERS.csv'
# ---------------------

def generate_password(length=12):
    """Generates a secure random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in string.punctuation for c in password)):
            return password

class Command(BaseCommand):
    help = 'Loads all teams, riddles, and answers from the master CSV.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting the ultimate team import script...'))
        
        try:
            # We open the output file for writing
            with open(OUTPUT_CREDENTIALS_FILE, 'w', newline='') as outfile:
                cred_writer = csv.writer(outfile)
                cred_writer.writerow(['team_id', 'password'])
                
                self.stdout.write(f"Opened {OUTPUT_CREDENTIALS_FILE} for writing passwords.")

                # --- 4. THIS IS THE NEW LOGIC TO READ .XSLX ---
                self.stdout.write(f"Loading Excel workbook: {MASTER_DATA_FILE}...")
                workbook = openpyxl.load_workbook(MASTER_DATA_FILE)
                
                try:
                    sheet = workbook[SHEET_NAME]
                except KeyError:
                    self.stdout.write(self.style.ERROR(f"FATAL ERROR: A sheet named '{SHEET_NAME}' was not found in your Excel file."))
                    self.stdout.write(self.style.ERROR(f"Please check the sheet name and update it in the script."))
                    return

                self.stdout.write(f"Found sheet: '{SHEET_NAME}'. Reading data...")
                
                # Get header row
                header_row = [cell.value for cell in sheet[1]]
                expected_headers = ['Team_ID', 'Riddle', 'Lead_Name', 'Final_Answer']
                if not all(h in header_row for h in expected_headers):
                    self.stdout.write(self.style.ERROR(f"FATAL ERROR: Your Excel sheet is missing required columns!"))
                    self.stdout.write(self.style.ERROR(f"It must have: {', '.join(expected_headers)}"))
                    return

                teams_created = 0
                riddles_created = 0

                # Use a transaction to ensure all or nothing is created
                with transaction.atomic():
                    self.stdout.write('Starting database transaction...')
                    
                    # Iterate rows (skip header)
                    for row in sheet.iter_rows(min_row=2, values_only=True):
                        # Map row data to headers
                        row_data = dict(zip(header_row, row))

                        team_id = row_data.get('Team_ID')
                        riddle_text = row_data.get('Riddle')
                        lead_name = row_data.get('Lead_Name')
                        final_answer = row_data.get('Final_Answer')

                        # Skip empty rows
                        if not team_id or not riddle_text:
                            continue

                        # --- 1. Find or Create Riddle ---
                        riddle, created = Riddle.objects.get_or_create(
                            riddle_text=riddle_text,
                            defaults={'lead_name': lead_name}
                        )
                        if created:
                            riddles_created += 1
                            self.stdout.write(f'Created new riddle for {lead_name}')

                        # --- 2. Find or Create User (Team) ---
                        if User.objects.filter(username=team_id).exists():
                            self.stdout.write(self.style.NOTICE(f'Team {team_id} already exists. Skipping.'))
                            continue
                        
                        password = generate_password()
                        user = User.objects.create_user(username=team_id, password=password)
                        
                        # --- 3. Create TeamData ---
                        TeamData.objects.create(
                            team=user,
                            assigned_riddle=riddle,
                            final_answer=final_answer
                        )

                        # --- 4. Write new credentials to our output file ---
                        cred_writer.writerow([team_id, password])
                        teams_created += 1

                self.stdout.write(self.style.SUCCESS(f'\n--- IMPORT COMPLETE! ---'))
                self.stdout.write(self.style.SUCCESS(f'Created {riddles_created} new riddles.'))
                self.stdout.write(self.style.SUCCESS(f'Created {teams_created} new teams.'))
                self.stdout.write(self.style.SUCCESS(f'All passwords saved to {OUTPUT_CREDENTIALS_FILE}'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'FATAL ERROR: File not found!'))
            self.stdout.write(self.style.ERROR(f'Make sure {MASTER_DATA_FILE} is in the main project folder (with manage.py).'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
            self.stdout.write(self.style.WARNING('Transaction rolled back. No changes were made.'))

