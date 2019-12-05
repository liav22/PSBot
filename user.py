import os
import csv

def search_user(userid, guildid): # Check if entry exists in database
	try:
		if os.path.isfile(f'userdata/{guildid}.csv'):
			with open(f'userdata/{guildid}.csv', 'rt') as f:
				reader = csv.reader(f)
				for row in reader:
					if str(userid) in row[0]:
						return True
					else:
						continue
				return False
		else:
			return False

	except Exception:
		return False # If the csv doesn't exist surely the entry doesn't
			
def register_new_user(userid, profile, guildid): # Register new entry, only executed if user is indeed unique
	with open(f'userdata/{guildid}.csv', 'a', newline='') as f:
		csv.writer(f).writerow([userid,profile])
		return
			
def lookup_user(userid, guildid): # Lookup existing entry as requested by user
	if search_user(userid, guildid):
		with open(f'userdata/{guildid}.csv', 'rt') as f:
			for row in f:
				if str(userid) in row:
					return row.rstrip()[row.find(',')+1::]
	else:
		return

def remove_user(userid, guildid): # Remove entry by mounting csv content to RAM and then rewriting entire csv
	with open(f'userdata/{guildid}.csv', 'r') as f:
		reader = csv.reader(f)
		new = list(reader)
		for line in new:
			if str(userid) in line:
				new.remove(line)

		with open(f'userdata/{guildid}.csv', 'w', newline='') as f2:
			for line in new:
				csv.writer(f2).writerow(line)