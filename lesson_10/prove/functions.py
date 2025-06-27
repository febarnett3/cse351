"""
Course: CSE 351, week 10
File: functions.py
Author: Fiona Barnett

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Requesting a family from the server:
family_id = 6128784944
data = get_data_from_server('{TOP_API_URL}/family/{family_id}')

Example JSON returned from the server
{
    'id': 6128784944, 
    'husband_id': 2367673859,        # use with the Person API
    'wife_id': 2373686152,           # use with the Person API
    'children': [2380738417, 2185423094, 2192483455]    # use with the Person API
}

Requesting an individual from the server:
person_id = 2373686152
data = get_data_from_server('{TOP_API_URL}/person/{person_id}')

Example JSON returned from the server
{
    'id': 2373686152, 
    'name': 'Stella', 
    'birth': '9-3-1846', 
    'parent_id': 5428641880,   # use with the Family API
    'family_id': 6128784944    # use with the Family API
}


--------------------------------------------------------------------------------------
You will lose 10% if you don't detail your part 1 and part 2 code below

Describe how to speed up part 1

<Add your comments here>


Describe how to speed up part 2

<Add your comments here>


Extra (Optional) 10% Bonus to speed up part 3

<Add your comments here>

"""
from common import *
import queue
import threading

tree_lock = threading.Lock()

def depth_fs_pedigree(family_id, tree: Tree):
    threads = []

    def process_person(person_id, recurse_on_family=False):
        if not person_id:
            return

        person_data = get_data_from_server(f'{TOP_API_URL}/person/{person_id}')
        if not person_data:
            return

        person = Person(person_data)
        with tree_lock:
            if tree.does_person_exist(person_id):
                return
            tree.add_person(person)

        next_id = person.get_familyid() if recurse_on_family else person.get_parentid()
        if next_id:
            t = threading.Thread(target=depth_fs_pedigree, args=(next_id, tree))
            t.start()
            threads.append(t)

    # Main logic
    with tree_lock:
        if tree.does_family_exist(family_id):
            return

    family_data = get_data_from_server(f'{TOP_API_URL}/family/{family_id}')
    if not family_data:
        return

    family = Family(family_data)
    with tree_lock:
        tree.add_family(family)

    # Process husband and wife
    process_person(family.get_husband(), recurse_on_family=False)
    process_person(family.get_wife(), recurse_on_family=False)

    # Process children
    for child_id in family.get_children():
        process_person(child_id, recurse_on_family=True)

    # Join threads after all processing is started
    for t in threads:
        t.join()

    # TODO - Printing out people and families that are retrieved from the server will help debugging

# -----------------------------------------------------------------------------

MAX_THREADS = 10
tree_lock = threading.Lock()

def worker(family_queue, tree: Tree):
        global tree_lock, MAX_THREADS
        while True:
            print("Getting family off queue")
            fam_id = family_queue.get()
            if fam_id is None:
                family_queue.task_done()
                break

            with tree_lock:
                if tree.does_family_exist(fam_id):
                    family_queue.task_done()
                    continue

            family_data = get_data_from_server(f'{TOP_API_URL}/family/{fam_id}')
            if not family_data:
                family_queue.task_done()
                continue

            family = Family(family_data)
            with tree_lock:
                print("adding family to tree")
                tree.add_family(family)

            # Process husband
            husband_id = family.get_husband()
            if husband_id:
                husband_data = get_data_from_server(f'{TOP_API_URL}/person/{husband_id}')
                if husband_data:
                    husband = Person(husband_data)
                    with tree_lock:
                        if not tree.does_person_exist(husband_id):
                            print("Adding husband to tree")
                            tree.add_person(husband)
                    parent_fam = husband.get_parentid()
                    if parent_fam:
                        family_queue.put(parent_fam)

            # Process wife
            wife_id = family.get_wife()
            if wife_id:
                wife_data = get_data_from_server(f'{TOP_API_URL}/person/{wife_id}')
                if wife_data:
                    wife = Person(wife_data)
                    with tree_lock:
                        if not tree.does_person_exist(wife_id):
                            print("Adding wife to tree")
                            tree.add_person(wife)
                    parent_fam = wife.get_parentid()
                    if parent_fam:
                        family_queue.put(parent_fam)

            # Process children
            for child_id in family.get_children():
                child_data = get_data_from_server(f'{TOP_API_URL}/person/{child_id}')
                if child_data:
                    child = Person(child_data)
                    with tree_lock:
                        if not tree.does_person_exist(child_id):
                            print("Adding child to tree")
                            tree.add_person(child)
                    child_family = child.get_familyid()
                    if child_family:
                        family_queue.put(child_family)

            family_queue.task_done()


def breadth_fs_pedigree(family_id, tree: Tree):
    global tree_lock, MAX_THREADS
    family_queue = queue.Queue()
    print("Putting first family on the queue")
    family_queue.put(family_id)

    # Start threads
    threads = []
    for _ in range(MAX_THREADS):
        t = threading.Thread(target=worker, args = (family_queue, tree))
        print("starting thread")
        t.start()
        threads.append(t)

    # Wait for all tasks to finish
    print("Joining threads")
    family_queue.join()

    # Send sentinel values to stop threads
    for _ in threads:
        family_queue.put(None)

    # Wait for threads to exit
    for t in threads:
        t.join()

  
# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(family_id, tree:Tree):
    # KEEP this function even if you don't implement it
    # TODO - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    pass