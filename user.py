import os
import csv

def search_user(userid, guildid):
    """ Check if entry exists in database """
    if os.path.isfile(f'userdata/{guildid}.csv'):
        with open(f'userdata/{guildid}.csv', 'rt') as file:
            reader = csv.reader(file)
            for row in reader:
                if str(userid) in row[0]:
                    return True
            return False
    else:
        return False

def register_new_user(userid, profile, guildid):
    """ Register new entry, only executed if user is indeed unique """
    with open(f'userdata/{guildid}.csv', 'a', newline='') as file:
        csv.writer(file).writerow([userid, profile])
        return

def lookup_user(userid, guildid):
    """Lookup existing entry as requested by user"""
    if search_user(userid, guildid):
        with open(f'userdata/{guildid}.csv', 'rt') as file:
            for row in file:
                if str(userid) in row:
                    return row.rstrip()[row.find(',')+1::]
    else:
        return

def remove_user(userid, guildid):
    """ Remove entry by mounting csv content to RAM and then rewriting entire csv """
    with open(f'userdata/{guildid}.csv', 'r') as file:
        reader = csv.reader(file)
        new = list(reader)
        for line in new:
            if str(userid) in line:
                new.remove(line)

        with open(f'userdata/{guildid}.csv', 'w', newline='') as file2:
            for line in new:
                csv.writer(file2).writerow(line)
