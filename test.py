from dotenv import load_dotenv
import os

# load .env
load_dotenv()

mySecret = os.environ.get('MEMU_URL')

print(mySecret)